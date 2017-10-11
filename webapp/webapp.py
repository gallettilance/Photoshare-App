from flask import Flask, render_template, request, flash, redirect, url_for
from flaskext.mysql import MySQL

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
    return render_template('signup.html')

@app.route('/authenticate', methods=['POST', 'GET'])
def authenticate():
    return render_template("profile.html", name=request.form['email'])


@app.route('/profile/<name>')
def profile(name):
    return render_template("profile.html", name=name)


if __name__=='__main__':
    app.run(debug=True)