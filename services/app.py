#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request, g , render_template
from flask_restful import reqparse
from flask_restful import Resource, Api
from twilio.rest import TwilioRestClient
from twilio import twiml
import MySQLdb
from MySQLdb.cursors import DictCursor
import logging
import json
import datetime
import logging.config
import sys
import json
import kaptan
import os
import time


#import routes here
from routes.twils import Countrycodes
from routes.twils import TwilioNewNumber
from routes.twils import SendingMessage
from routes.twils import ForwardingMessage

app = Flask(__name__)

config = kaptan.Kaptan(handler="json")
config.import_config(os.getenv("CONFIG_FILE_PATH", 'config.json'))
environment = config.get('environment')


ACCOUNT_SID=config.get("account_sid")
AUTH_TOKEN=config.get("Auth_token")

api = Api(app)
logger = logging.getLogger(__name__)


def connect_db():
    """Connects to the specific database."""
    try:
        db = MySQLdb.connect(host=config.get('dbhost'),  # your host, usually localhost
                         user=config.get("dbuser"),  # your username
                         passwd=config.get("dbpass"),  # your password
                         db=config.get("dbname"), cursorclass=DictCursor,sql_mode="STRICT_TRANS_TABLES")  # name of the data base
        return db
    except:
        logger.error('Failed to Connect to the database', exc_info=True)
        sys.exit("not able to connect to database")

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'appdb'):
        g.appdb = connect_db()
    return g.appdb

@app.route('/')
def home():
     cursor = g.appdb.cursor()
     query="""SELECT * FROM countryCodes"""
     cursor.execute(query)
     rv=cursor.fetchall()
     return render_template('index.html',rv=rv)


@app.route('/choosenum', methods=['POST'])
def choosenum():

    country=str(request.form['countries'])
    phno=str(request.form['ynumber'])
    contain=str(request.form['mnumber'])
    name=str(request.form['name'])
    areaCode=str(request.form['areacode'])
    now=datetime.datetime.now()
    datecreation=now.strftime("%Y-%m-%d %H:%M:%S")
    
    db = MySQLdb.connect( host="localhost",user="root",passwd="root",db="twilio" )
    cur = db.cursor()
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    numbers = client.phone_numbers.search(
        areaCode=areaCode,
        country=country,
        type="local",
        contains=contain
    )
    if (len(numbers)>0):
        allnumbers=[]
        for i in numbers:
            di={}
            di['friendly_name']=i.friendly_name
            di['phone_number']=i.phone_number
            allnumbers.append(di)
           
    else:
        allnumbers= "sorry no numbers available"
    return render_template('response.html',result=allnumbers)
    # query="""INSERT into twilioNumbers(name,phNumber,twilioNumber,twilioSid,createdDate)values(%s,%s,%s,%s)"""
    # cur.execute(query,(name,ynumber,nos,datecreation))
    # print "Record successfully added"
    # db.commit()
    # cur.close()
    # db.close()


@app.route('/purchase',methods=['POST'])
def purchase():
    # return 'hiiiiiiii'
        # logger = logging.getLogger("Purchasing a New Number")
        logger.info('Entered into PUT method to purchase a new twilio number')
        client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
        cursor = g.appdb.cursor()
        # name = request.json['name']
        # phnumber = request.json['ynumber']
        # chosen =request.json['chosen']
        now=datetime.datetime.now()
        createdDate=now.strftime("%Y-%m-%d %H:%M:%S")
        nos=request.form['nos']
        print nos

        # except:
        #     logger.error('DB Connection error', exc_info=True)

        number = client.phone_numbers.purchase(phone_number=nos)
        print '<<<<<<<<<<<<<<purchase'
        # Twilsid = number['ACCOUNT_SID']
        # print Twilsid
        # TwilNum = number['AUTH_TOKEN']
        # createdDate=now.strftime("%Y-%m-%d %H:%M:%S")
         # query=""" INSERT INTO `twilioNumbers`(`name`,`phNumber`,`twilioNumber`,`twilioSid`,`createdDate`) VALUES (%s,%s,%s,%s,%s); """
         # cursor.execute(query,(name,phnumber,TwilNum,Twilsid,createdDate))
        # g.appdb.commit()
        # logger.info('Exited from Purchasing a new number PUT method')
        return render_template("rresponse.html",nos=nos)


@app.route('/sndmsg',methods=['POST'])
def sndmsg():
    return render_template('home.html')



@app.route('/receivingMessages',methods=['POST'])
def sms():
    sid=config.get("account_sid")
    token=config.get("Auth_token")
    now=datetime.datetime.now()
    recvtime=now.strftime('%Y-%m-%d %H:%M:%S')
    forw = '+919951439132'

    client = TwilioRestClient(sid, token)
    number = request.form['From']
    mesagecon = request.form['Body']
    to =request.form['To']
    MsgSid = request.form['MessageSid']
    fordmsg='Hi madan '+number+' said '+mesagecon+ ' on '+recvtime
    client.messages.create(to=forw,from_='+18556638279',body=fordmsg)

@app.before_request
def before_request():
    g.appdb = get_db()
    setEmailRequirements()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'appdb'):
        g.appdb.close()

@app.before_first_request
def setup_logging(default_path='logconf.json', default_level=logging.INFO, env_key='LOG_CFG_PATH'):
    """Setup logging configuration"""
    path = default_path
    print "setup_logging before_first_request"
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

def setEmailRequirements():
    if not hasattr(g, 'config'):
        g.config = config

#give your URLs here

api.add_resource(SendingMessage, '/api/sendingmessage', endpoint='SendingMessage')
api.add_resource(TwilioNewNumber, '/api/twilionewnumber', endpoint='TwilioNewNumber')
api.add_resource(Countrycodes, '/api/countrycodes', endpoint='Countrycodes')
api.add_resource(ForwardingMessage,'/api/forwardingmessage',endpoint='ForwardingMessage')

@app.route('/api')
def index():
    # same result even with Flask-MySQL - We need to use the Index to Get
    # Values and Map to OrderedDict to create JSON.
    logger.info('Entered into Get /api Call')
    logger.debug(request.headers.get('User-Agent'))
    logger.info('Exiting from Get /api Call')
    return jsonify({"status": "success", "response": "API is up at the URL"})


def get_file_params(filename):
    filepath = g.config.get("excel_sheets_location") + '/'+filename
    with open(filepath, 'r') as f:
        content = f.read()
    return content



#,ssl_context='adhoc'
if __name__ == '__main__':
    app.run(host=config.get("host"), debug=config.get("debug"))
