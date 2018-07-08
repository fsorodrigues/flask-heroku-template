from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

APP_ROOT = os.path.join(os.path.dirname('__file__'), '..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

DBHOSTNAME = os.getenv('DBHOSTNAME')
DBPASSWORD = os.getenv('DBPASSWORD')
DBSCHEMA = os.getenv('DBSCHEMA')
DBUSERNAME = os.getenv('DBUSERNAME')

app = Flask(__name__)
mysql = SQLAlchemy()

# MySQL configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://' + DBUSERNAME + ':' + DBPASSWORD + '@' + \
                                        DBHOSTNAME + '/' + DBSCHEMA

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

mysql.init_app(app)

# map models
class Messages(mysql.Model):
    __tablename__ = 'hello'
    id = mysql.Column(mysql.Integer, primary_key=True)
    message = mysql.Column(mysql.String(255), nullable=False)

    def __repr__(self):
        return '<Result: (%s, %s) >' % (self.id, self.message)
        # return dict(id=self.id, message=self.message)

@app.route("/", methods=['GET'])
def hello():
    return "Hello World!!!!!!!"

# READ
@app.route('/message', methods=['GET'])
def getMessage():
    data = Messages.query.all() # fetch all products on the table

    data_all = []

    for msg in data:
        data_all.append(dict(id=msg.id,message=msg.message)) # prepare visual data

    return jsonify(messages=data_all)

# CREATE
@app.route('/message', methods=['POST'])
def createMessage():

    # fetch message from the request
    _message = request.json['message']

    message = Messages(message=_message) # prepare query statement

    curr_session = mysql.session # open database session
    try:
        curr_session.add(message) # add prepared statement to opened session
        curr_session.commit() # commit changes
    except:
        curr_session.rollback()
        curr_session.flush() # for resetting non-commited .add()

    messageId = message.id # fetch last inserted id
    data = Messages.query.filter_by(id=messageId).first() # fetch our inserted product

    result = dict(id=data.id,message=data.message) # prepare visual data

    return jsonify(session=result)

# UPDATE
@app.route('/<int:messageId>/message', methods=['PATCH'])
def updateMessage(messageId):

    message = request.json['message']
    print(message)
    curr_session = mysql.session

    try:
        msg = Messages.query.filter_by(id=messageId).first() # fetch the message do be updated
        msg.message = message # update column info fetched from request
        curr_session.commit() # commit changes
    except:
        curr_session.rollback()
        curr_session.flush()

    messageId = msg.id
    data = Messages.query.filter_by(id=messageId).first() # fetch our updated message

    result = dict(id=data.id,message=data.message) # prepare visual data

    return jsonify(session=result)


# REMOVE
@app.route('/message/<int:messageId>', methods=['DELETE'])
def deleteMessage(messageId):

    curr_session = mysql.session # initiate database session

    Messages.query.filter_by(id=messageId).delete() # finds the message by messageId and deletes it
    curr_session.commit() # commit changes to the database

    return getMessage() # return all messages

if __name__ == "__main__":
    app.run()
