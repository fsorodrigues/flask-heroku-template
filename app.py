from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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
class Courses(mysql.Model):
    __tablename__ = 'courserepository'
    id = mysql.Column(mysql.Integer, primary_key=True)
    title = mysql.Column(mysql.String(45), nullable=False)
    created = mysql.Column(mysql.DateTime, nullable=False)
    modified = mysql.Column(mysql.DateTime, nullable=False)

    def __repr__(self):
        return '<Result: (%s, %s, %s, %s) >' % (self.id, self.title, self.created, self.modified)
        # return dict(id=self.id, message=self.message)

@app.route("/", methods=['GET'])
def hello():
    return "Hello World!!!!!!!"

# READ
@app.route('/courses', methods=['GET'])
def getCourses():
    data = Courses.query.all() # fetch all products on the table

    data_all = []

    for course in data:
        data_all.append(dict(id=course.id,title=course.title,created=course.created,modified=course.modified)) # prepare visual data

    return jsonify(courses=data_all)

# CREATE
@app.route('/course', methods=['POST'])
def createCourse():

    # fetch message from the request
    title = request.get_json()['title']

    course = Courses(title=title,created=datetime.now()) # prepare query statement

    curr_session = mysql.session # open database session

    try:
        curr_session.add(course) # add prepared statement to opened session
        curr_session.commit() # commit changes
    except:
        curr_session.rollback()
        curr_session.flush() # for resetting non-commited .add()

    courseId = course.id # fetch last inserted id
    data = Courses.query.filter_by(id=courseId).first() # fetch our inserted product

    result = dict(id=course.id,title=course.title,created=course.created) # prepare visual data

    return jsonify(course=result)

# UPDATE
@app.route('/<int:courseId>/course', methods=['PATCH'])
def updateCourse(courseId):

    title = request.get_json()['title']

    curr_session = mysql.session

    try:
        _course = Courses.query.filter_by(id=courseId).first() # fetch the entry do be updated
        _course.title = title # update column info fetched from request
        _course.modified = datetime.now() # update modified column
        curr_session.commit() # commit changes
    except:
        curr_session.rollback()
        curr_session.flush()

    # courseId = course.id
    course = Courses.query.filter_by(id=courseId).first() # fetch our updated message

    result = dict(id=course.id,title=course.title,created=course.created,modified=course.modified) # prepare visual data

    return jsonify(course=result)


# REMOVE
@app.route('/course/<int:courseId>', methods=['DELETE'])
def deleteCourse(courseId):

    curr_session = mysql.session # initiate database session

    Courses.query.filter_by(id=courseId).delete() # finds the message by messageId and deletes it
    curr_session.commit() # commit changes to the database

    return getCourses() # return all messages

if __name__ == "__main__":
    app.run()
