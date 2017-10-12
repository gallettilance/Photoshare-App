from flask import Flask, render_template, request, flash, redirect, url_for, session
from flaskext.mysql import MySQL
import os

app = Flask(__name__, template_folder='templates')
db = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'hello123'
app.config['MYSQL_DATABASE_DB'] = 'CS660_webapp'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
db.init_app(app)

conn = db.connect()
cursor = conn.cursor()


@app.route('/', methods=['POST', 'GET'])
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    return render_template('signup.html', message="Please complete the form to sign up")

@app.route('/create_profile', methods=['POST','GET'])
def create_profile():
    result = request.form
    if result['password1'] != result['password2']:
        return render_template('signup.html', message="Password Mismatch")
    session['email'] = result['email']
    return render_template('profile.html', name=result['email'])

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    result = request.form
    email = result['email']
    password = result['password']
    if email != 'Lance' or password != '123':
        return redirect(url_for('signup'))
    session['email'] = result['email']
    return render_template("profile.html", name=result['email'].split('@')[0])

@app.route('/albums', methods=['GET', 'POST'])
def albums():
    return render_template('albums.html', name=session.get('email', None).split('@')[0], recent=None)

@app.route('/friend_search', methods=['GET', 'POST'])
def friend_search():
    return render_template('friendsearch.html', name=session.get('email', None).split('@')[0])
    
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('upload.html', name=session.get('email', None).split('@')[0])
    
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    return render_template('index.html')

@app.route('/put_photos_in_database', methods=['GET', 'POST'])
def put_photos_in_database():
    result = request.form
    session['album'] = result['album']
    return render_template('albums.html', name=session.get('email', None).split('@')[0], recent=session.get('album', None))

if __name__=='__main__':
    app.secret_key = os.urandom(100)
    app.run(debug=True)
