from flask import  jsonify, abort, make_response, request, g
from flask_restful import reqparse
from flask_restful import Resource
from twilio.rest import TwilioRestClient
import MySQLdb
from MySQLdb.cursors import DictCursor
import collections
import logging
import os
import kaptan

from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
from jsonschema import validate
import datetime

config = kaptan.Kaptan(handler="json")
config.import_config(os.getenv("CONFIG_FILE_PATH", 'config.json'))

sid=config.get('account_sid')
token=config.get('Auth_token')
twilnum=config.get('Twilio_number')

#This fetches the country, areacodes from DB
class Countrycodes(Resource):
    def get(self):
        logger = logging.getLogger("fetching all the country codes")
        logger.info('Entered into Countrycodes get method')
        try:
            cursor = g.appdb.cursor()
            print dir(cursor)
        except:
            logger.error("DB connection or url parameters error", exc_info=True)
        query="""SELECT * FROM countryCodes"""
        cursor.execute(query)
        rv=cursor.fetchall()
        logger.info('Exited Countrycodes get method')
        return jsonify({"status":"success", "response":"New user created successfully","response":rv})

#Fetches the available new numbers based on the user choice and country
class TwilioNewNumber(Resource):
    def post(self):
        logger = logging.getLogger("create a new twilio number")
        logger.info('Entered into TwilioNewNumber get methos')
        try:
            client = TwilioRestClient(sid, token)
            countrycode = request.json['countrycode']
            choice = request.json['choice']
            areacode = request.json['areacode']
            cursor = g.appdb.cursor()

        except:
            logger.error("DB connection or url parameters error", exc_info=True)
        numbers = client.phone_numbers.search(area_code=areacode,country=countrycode,type="local",contains=choice)
        ind=0
        lis=[]
        if len(numbers)>0:
            status="success"
            for i in numbers:
                di={}
                di["index"]=ind
                di["phonenumber"]= i.phone_number
                lis.append(di)
                ind += 1
        else:
            status="failed"
        logger.info('Exited from genrating twilio number post method')
        return jsonify({"status":status, "response":lis})

    def put(self):
        logger = logging.getLogger("Purchasing a New Number")
        logger.info('Entered into PUT method to purchase a new twilio number')
        try:
            client = TwilioRestClient(sid, token)
            cursor = g.appdb.cursor()
            name = request.json['name']
            phnumber = request.json['phnumber']
            chosen =request.json['chosen']
            now=datetime.datetime.now()
            createdDate=now.strftime("%Y-%m-%d %H:%M:%S")

        except:
            logger.error('DB Connection error', exc_info=True)

        number = client.phone_numbers.purchase(phone_number=chosen)
        Twilsid = number['sid']
        TwilNum = number['phone_number']
        createdDate=now.strftime("%Y-%m-%d %H:%M:%S")
        query=""" INSERT INTO `twilioNumbers`(`name`,`phNumber`,`twilioNumber`,`twilioSid`,`createdDate`) VALUES (%s,%s,%s,%s,%s); """
        cursor.execute(query,(name,phnumber,TwilNum,Twilsid,createdDate))
        g.appdb.commit()
        logger.info('Exited from Purchasing a new number PUT method')
        return jsonify({"status":"success", "number":number["friendly_name"],"result":"congrats you've owned this number"})

#Sending message
class SendingMessage(Resource):
    #this will send messages
    def post(self):
        logger = logging.getLogger("Sending a message from twilio")
        logger.info('Entered into TwilioNewNumber get methos')
        try:
            client = TwilioRestClient(sid,token)
            value = request.json
            receiver = value['receiver']
            sender = value['sender']
            message = value['message']
            now=datetime.datetime.now()
            senttime = now.strftime("%Y-%m-%d %H:%M:%S")
            cursor = g.appdb.cursor()

        except:
            logger.error("DB connection or url parameters error", exc_info=True)
        mess = client.messages.create(to=receiver,from_=sender,body=message)
        query="""INSERT INTO `sendmessage`(`sender`,`receiver`,`message`,`messageSid`,`sentTime`)VALUES(%s,%s,%s,%s,%s)"""
        cursor.execute(query,(sender,receiver,message,str(mess.sid),senttime))
        g.appdb.commit()
        return jsonify({"status":"success", "response":"Message hasbeen sent successfully"})

    #This fetches the history of a number
    def get(self):
        logger = logging.getLogger("sendingmessage get call")
        logger.info('fetches all the messages that have been sent so far from a number')
        try:
            client=TwilioRestClient(sid,token)
            fromnumber = '+'+str(request.args.get('fromnumber'))
            cursor = g.appdb.cursor()
        except:
            logger.error("DB connection or url parameters error", exc_info=True)
        query="""SELECT `receiver`,`message`,`messageSid` as sid,`sentTime` FROM `sendmessage` WHERE `sender`=%s"""
        cursor.execute(query,(fromnumber))
        rv=cursor.fetchall()
        logger.info('Exited from AddUserStoresList Get method')
        return jsonify({"status":"success", "response":rv})

#ForwardingMessage
class ForwardingMessage(Resource):
    def get(self):
        logger = logging.getLogger("create a new twilio number")
        logger.info('Entered into TwilioNewNumber get methos')
        try:
            client = TwilioRestClient(sid, token)
        except:
            logger.error("DB connection or url parameters error", exc_info=True)
        query="""INSERT INTO `receivedMessages`(`sender`,`receiver`,`receivedTime`,`message`,`msgSid`)VALUES(%s,%s,%s,%s,%s);"""
        messages = client.messages.list(direction="inbound",)
        rv=[]
        for message in messages:
            di={}
            di['dateup'] = message.date_updated
            di['from'] = message.from_
            di['body'] = message.body
            di['date'] = message.date_sent
            di['to'] = message.to
            di['sid'] = message.sid
            di['status'] = message.status
            di['direction'] = message.direction
            rv.append(di)

        logger.info('Exited from Add_User post method')
        return jsonify({"status":"success", "response":rv})
