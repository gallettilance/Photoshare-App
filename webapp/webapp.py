from flask import Flask, render_template, request, flash, redirect, url_for, session
from flaskext.mysql import MySQL
import os
import time
import numpy as np
import pandas as pd

app = Flask(__name__, template_folder='templates')
app.config['SESSION_TYPE']= 'memcached'
app.config['SECRET_KEY']= 'super secret key'
db = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'YWSSD'
app.config['MYSQL_DATABASE_DB'] = 'CS660_webapp'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
db.init_app(app)

conn = db.connect()
cursor = conn.cursor()


@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login(message='Please Log In'):
    return render_template('login.html', message=message)

@app.route('/signup', methods=['POST', 'GET'])
def signup(message="Please complete the form to sign up"):
    return render_template('signup.html', message=message)

@app.route('/create_profile', methods=['POST','GET'])
def create_profile():                             #signup function
    result = request.form
    if result['password1'] != result['password2']:
        return signup("Password Mismatch")
    email=result['email']
    query = 'SELECT email FROM users'
    cursor.execute(query)
    for item in cursor:
        if item[0] == email:         #item[0] is the email attribute of the user
            return login("You may already have an account - please log in")

    session['email'] = email
    query = 'INSERT INTO users(email, password, first_name, last_name, DoB, hometown, gender) VALUES (%s, %s, %s, %s, %s, %s, %s)'
    DoB = time.strptime(result['DoB'], '%Y-%m-%d')
    try:       # query= 'INSERT INTO users(...) VALUES(%s,..)'   and cursor.execute(query, (vlaues....))
        cursor.execute(query,
                   (result['email'], result['password1'], result['first_name'], result['last_name'],
                    time.strftime('%Y-%m-%d %H:%M:%S', DoB), result['hometown'], result['gender']))
    except:
        return signup("Oops, something went wrong - please try again")

    return render_template("profile.html", name=session['email'].split('@')[0])

@app.route('/profile', methods=['POST', 'GET'])
def profile():                                      #login function
    if request.method == 'POST':
        result = request.form
        email = result['email']
        password = result['password']
        query = 'SELECT email, password FROM users'
        cursor.execute(query)
        if cursor.rowcount == 0:
            return signup("No Account with this email and password, would you like to create an account?")
        for item in cursor:
            if item[0] == email:
                if item[1] == password:
                    session['email'] = result['email']
                    return render_template("profile.html", name=result['email'].split('@')[0])
                else:
                    return login('Wrong Password')
        return signup("No Account with this email and password, would you like to create an account?")
    print(session)
    return render_template("profile.html", name=session['email'].split('@')[0])





@app.route('/albums', methods=['GET', 'POST'])
def albums(recent=None):
    return render_template('albums.html', name=session.get('email', None).split('@')[0], recent=recent)

@app.route('/friend_search', methods=['GET', 'POST'])
def friend_search():
    return render_template('friendsearch.html', name=session.get('email', None).split('@')[0])

@app.route('/search', methods=['GET', 'POST'])
def search():
    return render_template('search.html', name=session.get('email', None).split('@')[0])

@app.route('/friends', methods=['GET', 'POST'])
def friends():
    return render_template('friends.html', name=session.get('email', None).split('@')[0])


@app.route('/friend_add', methods=['GET', 'POST'])
def friend_add():
    return render_template('friend_add.html', name=session.get('email', None).split('@')[0])

@app.route('/friend_delete', methods=['GET', 'POST'])
def friend_delete():
    return render_template('friend_delete.html', name=session.get('email', None).split('@')[0])

@app.route('/friend_list', methods=['GET', 'POST'])
def friend_list():
    return render_template('friend_list.html', name=session.get('email', None).split('@')[0])


@app.route('/people_search', methods=['GET', 'POST'])
def people_search():
    return render_template('people_search.html')

@app.route('/photo_recommend', methods=['GET', 'POST'])
def photo_recommend():
    return render_template('photo_recommend.html')



    
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('upload.html', name=session.get('email', None).split('@')[0])
    
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    return render_template('index.html')

@app.route('/visit', methods=['GET', 'POST'])
def visit():
    return render_template('visit.html')


@app.route('/photo_search', methods=['GET', 'POST'])
def photo_search():
    return render_template('photo_search.html')



@app.route('/put_photos_in_database', methods=['GET', 'POST'])
def put_photos_in_database():
    result = request.form
    session['album'] = result['album']
    return albums(session.get('album', None))

if __name__=='__main__':
    app.secret_key = os.urandom(100)
    app.run(debug=True)
