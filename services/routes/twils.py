from flask_restful import reqparse
from flask_restful import Resource
from flask import  jsonify, abort, make_response, request, g
from twilio.rest import TwilioRestClient
import MySQLdb
import collections
import logging
import os
import kaptan

from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
from jsonschema import validate

config = kaptan.Kaptan(handler="json")
config.import_config(os.getenv("CONFIG_FILE_PATH", 'config.json'))

sid=config.get('account_sid')
token=config.get('Auth_token')
twilnum=config.get('Twilio_number')


# Purchase the first number in the list
# if numbers:
#     numbers[0].purchase()

class TwilioNewNumber(Resource):
    def get(self):
        logger = logging.getLogger("create a new twilio number")
        logger.info('Entered into TwilioNewNumber get methos')
        try:
            client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
            countrycode = request.args.get('countrycode')
            choice = request.args.get('choice')
            name = request.args.get('name')
            phnumber = request.args.get('phnumber')
            areacode = request.args.get('areacode')
            cursor = g.appdb.cursor()

        except:
            logger.error("DB connection or url parameters error", exc_info=True)
        numbers = client.phone_numbers.search(area_code=areacode,country=countrycode,type="local",contains=choice)
        if len(numbers)>0:
        else:

        logger.info('Exited from Add_User post method')
        return jsonify({"status":"success", "response":"New user created successfully"})

    def get(self):
        logger = logging.getLogger("AddUserStoresList get")
        logger.info('Entered into AddUserStoresList  get method')
        try:
            cursor = g.appdb.cursor()
        except:
            logger.error('DB Connection error', exc_info=True)
        query = """ SELECT id AS store_id from store where id not in (
              select store_id from user_role ur
              inner join role r on ur.role_id = r.id
              where r.name in ('Employee', 'Manager')
              group by store_id having count(*)>=2) """
        cursor.execute(query)
        rv = cursor.fetchall()
        logger.info('Exited from AddUserStoresList Get method')
        return jsonify({"status":"success", "response":rv})


#Sending message
class SendingMessage(Resource):
    def post(self):
        logger = logging.getLogger("Sending a message from twilio")
        logger.info('Entered into TwilioNewNumber get methos')
        try:
            client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
            value = request.json
            receiver = value['receiver']
            sender = value['sender']
            message = value['message']
            print message.sid
            cursor = g.appdb.cursor()

        except:
            logger.error("DB connection or url parameters error", exc_info=True)
        mess = client.messages.create(to=to,from_=from_,body=body)

        query= """INSERT INTO messageLog(sender,receiver,message,senttime,msg_sid)values(%s,%s,%s,%s,%s,) """
        logger.info('Exited from Add_User post method')
        return jsonify({"status":"success", "response":"New user created successfully"})

    def get(self):
        logger = logging.getLogger("AddUserStoresList get")
        logger.info('Entered into AddUserStoresList  get method')
        try:
            cursor = g.appdb.cursor()
        except:
            logger.error('DB Connection error', exc_info=True)
        query = """ SELECT id AS store_id from store where id not in (
              select store_id from user_role ur
              inner join role r on ur.role_id = r.id
              where r.name in ('Employee', 'Manager')
              group by store_id having count(*)>=2) """
        cursor.execute(query)
        rv = cursor.fetchall()
        logger.info('Exited from AddUserStoresList Get method')
        return jsonify({"status":"success", "response":rv})
