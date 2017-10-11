from flask import Flask, render_template, request
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()
conn = mysql.connect()
cursor = conn.cursor()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'CS660_webapp'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

@app.route('/html/login/', methods=['POST'])
def get_data():
  email=request.form['email']
  password=request.form['password']
  query = 'SELECT email, password FROM users'
  cursor.execute(query)
  data = []
  for item in cursor:
    if item[0]== email:
      if item[1] == password:
        return profile(email)
      else:
        return "Wrong password"
  
  return "Username not found - do you have an account?"
    

@app.route('/html/profile/<name>')
def profile(name):
    return render_template("profile.html", name=name)
    
