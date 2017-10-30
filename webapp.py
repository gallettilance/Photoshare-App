from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
import psycopg2
import os, base64
from urllib import parse
import time
import re

app = Flask(__name__, template_folder='templates')
app.config['SESSION_TYPE']= 'memcached'
app.config['SECRET_KEY']= 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

parse.uses_netloc.append("postgres")
url = parse.urlparse(os.environ['DATABASE_URL'])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

db.init_app(app)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

cursor = conn.cursor()


@app.route('/', methods=['POST', 'GET'])
def home():

    #when user is not signed in
    query = 'SELECT photo_id, data, CAPTION FROM PHOTOS ORDER BY photo_id DESC LIMIT 100'
    cursor.execute(query)
    all_photos = []
    for item in cursor:
        all_photos.append([item[0], item[1], item[2]])
    return render_template('index.html', photos=all_photos)

@app.route('/login_page', methods=['POST', 'GET'])
def login_page(message='Please Log In'):
    return render_template('login_page.html', message=message)

@app.route('/signup_page', methods=['POST', 'GET'])
def signup_page(message="Please complete the form to sign up"):
    return render_template('signup_page.html', message=message)

@app.route('/signup', methods=['POST','GET'])
def signup():

    #test password mismatch
    result = request.form
    if result['password1'] != result['password2']:
        return signup_page("Password Mismatch")

    #need other input checks here (like those in mysql)
    email = result['email']
    if email == 'anon@anon':
        return signup_page("This email is invalid")

    if result['first_name'] == 'anon' or result['last_name'] == 'anon':
        return signup_page("Your name cannot be anon")

    #test account already exists

    query = 'SELECT EMAIL FROM USERS'
    cursor.execute(query)
    for item in cursor:
        if item[0] == email:
            return login_page("You may already have an account - please log in")
        if item[0] == email.lower():
            return signup_page("Please pay attention to upper and lower case in your email")

    #insert data into database
    query = 'INSERT INTO USERS(EMAIL, PASSWORD, first_name, ' \
            'last_name, DOB, HOMETOWN, GENDER) VALUES (%s, %s, %s, %s, %s, %s, %s)'
    DoB = time.strptime(result['DoB'], '%Y-%m-%d')

    #exception handling here is for potential errors from database insertion
    try:
        cursor.execute(query,
                   (result['email'], result['password1'], result['first_name'], result['last_name'],
                    time.strftime('%Y-%m-%d %H:%M:%S', DoB), result['hometown'], result['gender']))
    except:
        return signup_page("Oops, something went wrong - please try again")

    conn.commit()

    #get id generated by database upon insertion
    query = 'SELECT user_id, EMAIL, first_name FROM USERS'
    cursor.execute(query)
    for item in cursor:
        if email == item[1]:
            userid = item[0]
            my_name = item[2]
            break

    session['userid'] = userid
    session['my_name'] = my_name
    session['loggedin'] = True
    return view_profile(id=userid)

@app.route('/login', methods=['POST', 'GET'])
def login():

    result = request.form
    email = result['email']
    password = result['password']

    #check user has account
    query = 'SELECT EMAIL, PASSWORD, user_id, first_name FROM USERS'
    cursor.execute(query)
    if cursor.rowcount == 0:
        return signup_page("No Account with this email and password, would you like to create an account?")

    #check password match
    for item in cursor:
        if item[0] == email and email != 'anon@anon':
            if item[1] == password:
                session['userid'] = item[2]
                session['my_name'] = item[3]
                session['loggedin'] = True
                return view_profile(id=item[2])
            else:
                return login_page('Wrong Password')

    return signup_page("No Account with this email and password, would you like to create an account?")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    session['loggedin'] = False
    return home()

@app.route('/view_profile/<id>', methods=['POST', 'GET'])
def view_profile(id):

    #get name of the person who's profile you're viewing
    query = 'SELECT user_id, first_name FROM USERS'
    cursor.execute(query)
    for item in cursor:
        if int(id) == int(item[0]):
            person_name = item[1]

    #get album_id of all albums of user
    query = 'SELECT album_id, user_id FROM ALBUMS ORDER BY album_id DESC'
    cursor.execute(query)
    all_albums = []
    for item in cursor:
        if int(item[1]) == int(id):
            all_albums.append(int(item[0]))

    #get all_photos
    query = 'SELECT photo_id, DATA, CAPTION, album_id FROM PHOTOS ORDER BY photo_id DESC LIMIT 100'
    cursor.execute(query)
    all_photos = []
    user_photos = []
    for item in cursor:
        all_photos.append([item[0], item[1], item[2]])
        if int(item[3]) in all_albums:
            user_photos.append([item[0], item[1], item[2]])

    #if you're logged in
    if session.get('loggedin', None):

        #get my name and userid
        userid = session.get('userid', None)
        my_name = session.get('my_name', None)

        if int(userid) == int(id):
            return render_template('profile.html', name=person_name, username=my_name,
                                   loggedin=True,
                                   myprofile=True, userid=userid, id=id, photos=all_photos)

        #get friends of id
        query = 'SELECT user_id1, user_id2 FROM FRIENDSHIP'
        cursor.execute(query)
        all_friends = []
        for item in cursor:
            if int(id) == int(item[0]):
                all_friends.append(int(item[1]))
            elif int(id) == int(item[1]):
                all_friends.append(int(item[0]))
                
        if userid in all_friends:
            friends = True
        else:
            friends = False
        
            return render_template('profile.html', name=person_name, username=my_name, loggedin=True,
                               myprofile=False, userid=userid, id=id, photos=all_photos, user_photos=user_photos, friends=friends)

        #otherwise
        return render_template('profile.html', name=person_name, loggedin=False, id=id, user_photos=user_photos)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    userid = session.get('userid', None)
    my_name = session.get('my_name', None)
    return render_template('upload.html', username=my_name, userid=userid)


@app.route('/create_album', methods=['GET', 'POST'])
def create_album():

    userid = session.get('userid', None)
    my_name = session.get('my_name', None)

    #insert into database album
    result = request.form
    query = 'INSERT INTO ALBUMS(user_id, album_name) VALUES (%s, %s) RETURNING album_id'

    cursor.execute(query, (userid, result['album']))
    res = cursor.fetchone()
    album_id = res[0]
    conn.commit()

    return render_template('upload_photo.html', album_id=album_id, username=my_name, userid=userid)



@app.route('/upload_photo/<album_id>', methods=['GET', 'POST'])
def upload_photo(album_id):

    userid = session.get('userid', None)
    my_name = session.get('my_name', None)

    if request.method == 'POST':
        cap = request.form['caption']

        hashtags = re.findall(r'\B(\#[a-zA-Z]+\b)(?!;)', cap)

        # insert tag and photo
        query1 = 'INSERT INTO ASSOCIATE(photo_id, HASHTAG) VALUES (%s, %s)'
        query2 = 'INSERT INTO TAG(HASHTAG) VALUES (%s)'
        query3 = 'SELECT * FROM TAG'

        for tag in hashtags:
            if len(tag) < 40:
                t = ''.join(list(tag)[1:])
                cap = re.sub(tag, "<a href=\"/view_tag/" + t + "\") }}\"> " + tag + " </a>", cap)

        query = 'INSERT INTO PHOTOS(album_id, DATA, CAPTION) VALUES (%s, %s, %s) RETURNING photo_id'
        image = request.files['img']

        img = ''.join(list(str(base64.standard_b64encode(image.read())))[2:-1])

        cursor.execute(query, (int(album_id), img, cap))
        res = cursor.fetchone()
        photo_id = res[0]
        conn.commit()

        cursor.execute(query3)

        # only insert tag if not duplicate
        all_tags = []
        for item in cursor:
            all_tags.append(item[0])

        for tag in hashtags:
            if tag not in all_tags and len(tag) < 40:
                cursor.execute(query2, [tag])
                conn.commit()
                all_tags.append(tag)

        for tag in hashtags:
            if len(tag) < 40:
                cursor.execute(query1, (photo_id, tag))
                conn.commit()

        return render_template('upload_photo.html', album_id=album_id, username=my_name, userid=userid)

    return render_template('upload_photo.html', album_id=album_id, username=my_name, userid=userid)

@app.route('/view_all_albums/<uploader_id>', methods=['GET', 'POST'])
def view_all_albums(uploader_id):

    #most recently created album first
    query = 'SELECT album_id, album_name, user_id FROM ALBUMS ORDER BY album_id DESC'
    cursor.execute(query)
    all_albums = []
    for item in cursor:
        if int(item[2]) == int(uploader_id):
            all_albums.append([item[0], item[1]])

    query = 'SELECT user_id, first_name FROM USERS'
    cursor.execute(query)
    for item in cursor:
        if int(item[0]) == int(uploader_id):
            uploader_name = item[1]
            break

    if session.get('loggedin', None):
        userid = session.get('userid', None)
        my_name = session.get('my_name', None)

        return render_template('view_all_albums.html', username=my_name, userid=userid, uploader_name=uploader_name,
                               all_albums=all_albums, loggedin=True, uploader_id=uploader_id)

    return render_template('view_all_albums.html', uploader_name=uploader_name,
                           all_albums=all_albums, loggedin=False, uploader_id=uploader_id)


@app.route('/view_album_content/<album_id>', methods=['GET', 'POST'])
def view_album_content(album_id):

    # get the album name and uploader id
    query = 'SELECT album_id, album_name, user_id FROM ALBUMS'
    cursor.execute(query)
    for item in cursor:
        if int(item[0]) == int(album_id):
            album_name = item[1]
            uploader_id = item[2]
            break

    # get uploader name
    query = 'SELECT first_name, user_id FROM USERS'
    cursor.execute(query)
    for item in cursor:
        if int(item[1]) == int(uploader_id):
            uploader_name = item[0]
            break

    # get photo data from all photos with corresponding ids
    query = 'SELECT photo_id, DATA, CAPTION, album_id FROM PHOTOS'
    cursor.execute(query)
    all_photos = []
    for item in cursor:
        if int(item[3]) == int(album_id):
            all_photos.append([item[0], item[1], item[2]])

    #if logged in
    if session.get('loggedin'):

        userid = session.get('userid', None)
        my_name = session.get('my_name', None)
        return render_template('view_album_content.html', username=my_name, uploader_name=uploader_name, loggedin=True,
                               userid=int(userid), uploader_id=int(uploader_id), photos=all_photos, album_id=album_id,
                               album_name=album_name)

    else:
        return render_template('view_album_content.html', uploader_name=uploader_name, loggedin=False,
                               uploader_id=uploader_id, photos=all_photos, album_id=album_id, album_name=album_name)

@app.route('/view_photo/<photo_id>', methods=['GET', 'POST'])
def view_photo(photo_id):

    # get the photo data and caption
    query = 'SELECT photo_id, DATA, CAPTION, album_id FROM PHOTOS'
    cursor.execute(query)
    for item in cursor:
        if int(item[0]) == int(photo_id):
            photo = [item[1], item[2], photo_id]
            album_id = int(item[3])

    #get all comment ids and user id of these comments on this photo
    query = 'SELECT photo_id, comment_id, CONTENT, user_id FROM COMMENTS'
    cursor.execute(query)
    comments = []
    for item in cursor:
        if int(item[0]) == int(photo_id):
            comments.append([int(item[3]), item[2], item[1]])

    commenterids = [x[0] for x in comments]
    all_comments = []

    #get names of all commenters
    query = 'SELECT user_id, first_name FROM USERS'
    cursor.execute(query)
    all_commenters = []
    for item in cursor:
        if int(item[0]) in commenterids:
            all_commenters.append([int(item[0]), item[1]])

    for i in range(len(comments)):
        for j in range(len(all_commenters)):
            if comments[i][0] == all_commenters[j][0]:
                all_comments.append([comments[i][0], all_commenters[j][1], comments[i][1], int(comments[i][2])])


    # get the album name and uploader id
    query = 'SELECT album_name, album_id, user_id FROM ALBUMS'
    cursor.execute(query)
    for item in cursor:
        if int(item[1]) == int(album_id):
            album_name = item[0]
            uploader_id = item[2]
            break

    # get uploader name
    query = 'SELECT first_name, user_id FROM USERS'
    cursor.execute(query)
    for item in cursor:
        if int(item[1]) == int(uploader_id):
            uploader_name = item[0]
            break

    # find all likes
    query = 'SELECT user_id, photo_id FROM LIKETABLE'
    cursor.execute(query)
    likers = []
    for item in cursor:
        if int(item[1]) == int(photo_id):
            likers.append(int(item[0]))

    #find names of all likers
    query = 'SELECT first_name, user_id FROM USERS'
    cursor.execute(query)
    likedby = []
    for item in cursor:
        if int(item[1]) in likers:
            likedby.append([item[1], item[0]])


    #find all tags
    query = 'SELECT HASHTAG, photo_id FROM ASSOCIATE'
    cursor.execute(query)
    tagged_with = []
    for item in cursor:
        if int(item[1]) == int(photo_id):
            tagged_with.append(item[0])


    # if logged in
    if session.get('loggedin'):

        userid = session.get('userid', None)
        my_name = session.get('my_name', None)

        if userid in likers:
            liked = True
        else:
            liked = False

        if int(userid) == int(uploader_id):
            mypic = True
        else:
            mypic = False

        return render_template('view_photo.html', username=my_name, uploader_name=uploader_name, loggedin=True,
                               liked=liked, likedby=likedby, like_num=len(likedby), userid=int(userid),
                               uploader_id=int(uploader_id), photo=photo, album_id=album_id, album_name=album_name,
                               comments=all_comments, mypic=mypic)

    else:
        return render_template('view_photo.html', uploader_name=uploader_name, loggedin=False, likedby=likedby, like_num=len(likedby),
                               uploader_id=uploader_id, photo=photo, album_id=album_id, album_name=album_name,
                               comments=all_comments)

@app.route('/comment/<photo_id>', methods=['GET', 'POST'])
def comment(photo_id):

    comm = request.form['comment']
    hashtags = re.findall(r'\B(\#[a-zA-Z]+\b)(?!;)', comm)

    # insert tag and photo
    query1 = 'INSERT INTO ASSOCIATE(photo_id, HASHTAG) VALUES (%s, %s)'
    query2 = 'INSERT INTO TAG(HASHTAG) VALUES (%s)'
    query3 = 'SELECT * FROM TAG'

    for tag in hashtags:
        if len(tag)<40:
            t = ''.join(list(tag)[1:])
            comm = re.sub(tag, "<a href=\"/view_tag/"+t+"\") }}\"> "+tag+" </a>", comm)

    cursor.execute(query3)

    #only insert tag if not duplicate
    all_tags = []
    for item in cursor:
        all_tags.append(item[0])

    for tag in hashtags:
        if (tag not in all_tags) and len(tag)<40:
            cursor.execute(query2, [tag])
            conn.commit()
            all_tags.append(tag)

    for tag in hashtags:
        if len(tag) < 40:
            try:
                cursor.execute(query1, (photo_id, tag))
            except:
                break
            conn.commit()

    if session.get('loggedin', None):

        userid = session.get('userid', None)

        # insert comment and user id
        query = 'INSERT INTO COMMENTS(photo_id, CONTENT, user_id) VALUES (%s, %s, %s)'

        cursor.execute(query, (photo_id, comm, userid))
        conn.commit()

        return view_photo(photo_id=photo_id)

    #find anon user
    anon_email = "anon@anon"

    query = 'SELECT user_id, EMAIL, first_name FROM USERS WHERE EMAIL=%s'
    cursor.execute(query, [anon_email])

    anon_user = []

    for item in cursor:
        anon_user = [item[0], item[2]]

    #if we previously created an anon user
    if anon_user:

        userid = anon_user[0]
        # insert comment and user id
        query = 'INSERT INTO COMMENTS(photo_id, CONTENT, user_id) VALUES (%s, %s, %s)'

        cursor.execute(query, (photo_id, comm, userid))
        conn.commit()

        return view_photo(photo_id=photo_id)

    #otherwise we create one
    anon_password = "hello123"
    anon_name = 'anon'
    anon_dob = '1900-01-01'
    anon_gender = 'O'

    query = 'INSERT INTO USERS(EMAIL, PASSWORD, first_name, ' \
            'last_name, DOB, HOMETOWN, GENDER) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING user_id'
    cursor.execute(query, (anon_email, anon_password, anon_name, anon_name, anon_dob, anon_name, anon_gender))
    res = cursor.fetchone()
    userid = res[0]
    conn.commit()

    # insert comment and user id
    query = 'INSERT INTO COMMENTS(photo_id, CONTENT, user_id) VALUES (%s, %s, %s)'

    cursor.execute(query, (photo_id, comm, userid))
    conn.commit()

    return view_photo(photo_id=photo_id)

@app.route('/friend_add/<friend_id>', methods=['GET', 'POST'])
def friend_add(friend_id):

    userid = session.get('userid', None)

    # insert friendship
    query = 'INSERT INTO FRIENDSHIP(user_id1, user_id2) VALUES (%s, %s)'
    cursor.execute(query, (userid, friend_id))
    conn.commit()

    return view_profile(friend_id)

@app.route('/view_friends/<id>', methods=['GET', 'POST'])
def view_friends(id):

    #get the name of the id
    query = 'SELECT user_id, first_name FROM USERS'
    cursor.execute(query)
    for item in cursor:
        if int(item[0]) == int(id):
            name = item[1]

    # get friends of id
    query = 'SELECT user_id1, user_id2 FROM FRIENDSHIP'
    cursor.execute(query)
    friends = []
    for item in cursor:
        if int(id) == int(item[0]):
            friends.append(int(item[1]))
        elif int(id) == int(item[1]):
            friends.append(int(item[0]))

    #get names of friends
    query = 'SELECT user_id, first_name FROM USERS'
    cursor.execute(query)
    all_friends = []
    for item in cursor:
        for fid in friends:
            if int(item[0]) == fid:
                all_friends.append([item[0], item[1]])

    #if logged in
    if session.get('loggedin', None):

        userid = session.get('userid', None)
        my_name = session.get('my_name', None)

        recommended_friends = friend_recommendation(userid, friends)

        return render_template("view_friends.html", friends=all_friends, username=my_name, userid=int(userid),
                               name=name, id=int(id), loggedin=True, recommended_friends=recommended_friends)

    return render_template("view_friends.html", friends=all_friends, name=name, id=id,
                           loggedin=False)


@app.route('/like/<photo_id>', methods=['GET', 'POST'])
def like(photo_id):

    userid = session.get('userid', None)

    # insert like into liketable
    query = 'INSERT INTO LIKETABLE(user_id, photo_id) VALUES (%s, %s)'
    cursor.execute(query, (userid, photo_id))
    conn.commit()

    return view_photo(photo_id)


@app.route('/view_tag/<tag>', methods=['GET', 'POST'])
def view_tag(tag):

    if tag[0] != '#':
        tag = '#'+tag

    # select all photos with that tag
    query = 'SELECT photo_id, HASHTAG FROM ASSOCIATE'
    all_photoids = []
    cursor.execute(query)
    for item in cursor:
        if item[1] == tag:
            all_photoids.append(int(item[0]))

    #get the photos
    query = 'SELECT photo_id, DATA FROM PHOTOS'
    all_photos = []
    cursor.execute(query)
    for item in cursor:
        for photo in all_photoids:
            if photo == int(item[0]):
                all_photos.append([item[0], item[1]])

    if session.get('loggedin', None):

        return render_template('view_tag.html', tag=tag, photos=all_photos, loggedin=True,
                               userid=session.get('userid', None), username=session.get('my_name', None))

    return render_template('view_tag.html', tag=tag, photos=all_photos, loggedin=False)


@app.route('/delete_photo/<photo_id>', methods=['GET', 'POST'])
def delete_photo(photo_id):

    userid = session.get('userid', None)

    query = 'DELETE FROM PHOTOS WHERE photo_id=%s'
    cursor.execute(query, [photo_id])
    conn.commit()

    return view_profile(id=userid)

@app.route('/delete_comment/<comment_id>', methods=['GET', 'POST'])
def delete_comment(comment_id):

    userid = session.get('userid', None)

    query= 'SELECT comment_id, CONTENT, photo_id FROM COMMENTS'
    cursor.execute(query)

    for item in cursor:
        if int(item[0]) == int(comment_id):
            comm = item[1]
            photo_id = item[2]
            break

    tags = re.findall(r'\B(\#[a-zA-Z]+\b)(?!;)', comm)

    query = 'DELETE FROM ASSOCIATE WHERE photo_id=%s AND HASHTAG=%s'
    for tag in tags:
        cursor.execute(query, (photo_id, tag))

    query = 'DELETE FROM COMMENTS WHERE comment_id=%s'
    cursor.execute(query, [comment_id])
    conn.commit()

    return view_photo(photo_id=photo_id)

@app.route('/delete_album/<album_id>', methods=['GET', 'POST'])
def delete_album(album_id):

    userid = session.get('userid', None)

    query = 'DELETE FROM ALBUMS WHERE album_id=%s'
    cursor.execute(query, [album_id])
    conn.commit()

    return view_profile(id=userid)


@app.route('/unlike/<photo_id>', methods=['GET', 'POST'])
def unlike(photo_id):

    userid = session.get('userid', None)

    query = 'DELETE FROM LIKETABLE WHERE photo_id=%s AND user_id=%s'
    cursor.execute(query, (photo_id, userid))
    conn.commit()

    return view_photo(photo_id=photo_id)


@app.route('/unfriend/<friend_id>', methods=['GET', 'POST'])
def unfriend(friend_id):

    userid = session.get('userid', None)

    query = 'DELETE FROM FRIENDSHIP WHERE (user_id1=%s AND user_id2=%s) OR (user_id2=%s AND user_id1=%s)'
    cursor.execute(query, (friend_id, userid, friend_id, userid))
    conn.commit()

    return view_profile(id=friend_id)


@app.route('/all_users', methods=['GET', 'POST'])
def all_users():
    query = 'SELECT user_id, first_name, last_name FROM USERS'
    cursor.execute(query)

    all_users = []
    for item in cursor:
        all_users.append([item[0], item[1]+' '+item[2]])

    if session.get('loggedin', None):
        userid = session.get('userid', None)
        my_name = session.get('my_name', None)


        return render_template('all_users.html', all_users=all_users, username=my_name, userid=userid, loggedin=True)

    return render_template('all_users.html', all_users=all_users)


@app.route('/top_users', methods=['GET', 'POST'])
def top_users():

    query0 ='SELECT user_id, COUNT(*) AS Pscore ' \
            'FROM PHOTOS AS P JOIN ALBUMS AS A ON P.album_id = A.album_id ' \
            'GROUP BY user_id '

    query1 = 'SELECT user_id, COUNT(comment_id) AS Cscore FROM COMMENTS GROUP BY user_id'

    query2 = 'SELECT user_id FROM USERS'
    query3 = 'SELECT user_id FROM USERS WHERE EMAIL =%s'

    anon = -1
    anon_email = 'anon@anon'

    cursor.execute(query3, [anon_email])
    for item in cursor:
        anon = int(item[0])
        break

    cursor.execute(query2)

    all_users = []
    for item in cursor:
        if int(item[0]) != anon:
            all_users.append(int(item[0]))

    cursor.execute(query0)

    top10id_photo = []
    for item in cursor:
        top10id_photo.append([int(item[0]), int(item[1])])

    only_ids_photo = [x[0] for x in top10id_photo]

    for user in all_users:
        if user not in only_ids_photo:
            top10id_photo.append([user, 0])

    cursor.execute(query1)

    top10id_comment = []
    for item in cursor:
        top10id_comment.append([int(item[0]), int(item[1])])

    only_ids_comment = [x[0] for x in top10id_comment]

    for user in all_users:
        if user not in only_ids_comment:
            top10id_comment.append([user, 0])

    top10id = [[x[0], x[1] + y[1]] for x in top10id_photo for y in top10id_comment if x[0] == y[0]]

    top10id = list(reversed(sorted(top10id, key=lambda x: x[1])))[:10]

    query = 'SELECT first_name, user_id FROM USERS WHERE user_id = %s'

    top10 = []
    for topid in top10id:
        cursor.execute(query, [topid[0]])
        for item in cursor:
            top10.append([item[1], item[0]])

    if session.get('loggedin', None):

        userid = session.get('userid', None)
        my_name = session.get('my_name', None)

        return render_template('top_users.html', top10=top10, userid=userid, username=my_name, loggedin=True)

    return render_template('top_users.html', top10=top10, loggedin=False)


@app.route('/top_tags', methods=['GET', 'POST'])
def top_tags():

    query = 'SELECT COUNT(*) AS score, HASHTAG FROM ASSOCIATE GROUP BY HASHTAG ORDER BY score DESC LIMIT 10'
    cursor.execute(query)

    top10 = []
    for item in cursor:
        top10.append(item[1])

    if session.get('loggedin', None):

        userid = session.get('userid', None)
        my_name = session.get('my_name', None)

        return render_template('top_tags.html', top10=top10, userid=userid, name=my_name, loggedin=True)

    return render_template('top_tags.html', top10=top10, loggedin=False)


def photo_search(key_words):

    results = []

    query3 = "SELECT photo_id, HASHTAG FROM ASSOCIATE"
    cursor.execute(query3)

    photo_id_set = []
    id_tag = []

    for item in cursor:
        # if the photo_id is not already in id_tag
        if int(item[0]) not in photo_id_set:
            id_tag.append([int(item[0]), item[1]])
            photo_id_set.append(int(item[0]))

        # otherwise
        else:
            # find the photo_id and append tag to its list of hashtags
            for i in range(len(id_tag)):
                if int(id_tag[i][0]) == int(item[0]):
                    id_tag[i].append(item[1])

    # compute_similarity pair between tags set and the key_words
    pid_sim = []
    for tag in id_tag:
        pid = int(tag[0])
        ptags = tag[1:]
        sim = compute_jaccard_index(set(key_words), set(ptags))

        pid_sim.append([pid, sim])

    rank = list(reversed(sorted(pid_sim, key=lambda x: x[1])))
    pids = [int(x[0]) for x in rank if x[1] > 0]

    # getting the image data

    query = 'SELECT photo_id, DATA, CAPTION, album_id FROM PHOTOS'
    cursor.execute(query)

    pic_and_data = []
    for item in cursor:
        pic_and_data.append([int(item[0]), item[1]])

    # preserving the order

    for i in range(len(pids)):
        for j in range(len(pic_and_data)):
            if int(pids[i]) == int(pic_and_data[j][0]):
                results.append([pic_and_data[j][0], pic_and_data[j][1]])

    return results


@app.route('/search', methods=['GET', 'POST'])
def search():

    results = []

    if request.method == 'POST':

        search_type = request.form['search_type']
        search_word = request.form['search_word']

        if search_type == "comment":

            hashtags = re.findall(r'\B(\#[a-zA-Z]+\b)(?!;)', search_word)

            for tag in hashtags:
                if len(tag) < 40:
                    t = ''.join(list(tag)[1:])
                    search_word = re.sub(tag, "<a href=\"/view_tag/" + t + "\") }}\"> " + tag + " </a>", search_word)

            query1 = 'SELECT user_id, CONTENT FROM COMMENTS'
            cursor.execute(query1)
            user = []
            for item in cursor:
                if item[1] == search_word:
                    user.append(int(item[0]))

            query2 = 'SELECT first_name, user_id FROM USERS'
            cursor.execute(query2)
            for item in cursor:
                if int(item[1]) in user:
                    results.append([item[1], item[0]])  # append user_id and first_name to "results"

            the_results = []
            all_ids = []
            for i in range(len(results)):
                count = 0
                for j in range(i, len(results)):
                    if results[i][0] == results[j][0]:
                        count += 1
                if results[i][0] not in all_ids:  # to avoid repetition, since the same user_id can appear multiple times, and we only need to compute once
                    all_ids.append(results[i][0])
                    the_results.append([results[i][0], results[i][1], count])

            results = list(reversed(sorted(the_results, key=lambda x: x[2])))  # the results has: user_id and user's first_name

            if session.get('loggedin', None):

                userid = session.get('userid', None)
                my_name = session.get('my_name', None)

                return render_template('search.html', search_results=results, search_type="comments", username=my_name,
                                       userid=userid, loggedin=True)

            return render_template('search.html', search_results=results, search_type="comments", loggedin=False)

        elif search_type == "photo":

            key_words = search_word.split(" ")
            for i in range(len(key_words)):
                if key_words[i][0] != '#':
                    key_words[i] = '#' + key_words[i]

            results = photo_search(key_words)

            if session.get('loggedin', None):
                userid = session.get('userid', None)
                my_name = session.get('my_name', None)

                return render_template('search.html', search_results=results, search_type="photos", username=my_name,
                                       userid=userid, loggedin=True)

            return render_template('search.html', search_results=results, search_type="photos", loggedin=False)

        elif search_type == "user":
            names = []
            key_words = search_word.split(" ")
            if len(key_words) < 2:
                key_words.append('')

            #get first and last names of all users
            query4 = "SELECT user_id, first_name, last_name FROM USERS"
            cursor.execute(query4)

            for item in cursor:
                names.append([int(item[0]), item[1], item[2]])

            for name in names:
                if (key_words[0] == name[1] or key_words[1] == name[1]):
                    results.append(name)

            for name in names:
                if (key_words[1] == name[2] or key_words[0] == name[2]) and (name not in results):
                    results.append(name)

            results = [[x[0], ' '.join([x[1], x[2]])] for x in results]

            if session.get('loggedin', None):

                userid = session.get('userid', None)
                my_name = session.get('my_name', None)

                return render_template('search.html', search_results=results, search_type="users", username=my_name,
                                       userid=userid, loggedin=True)

            return render_template('search.html', search_results=results, search_type="users", loggedin=False)

        if session.get('loggedin', None):
            userid = session.get('userid', None)
            my_name = session.get('my_name', None)

            return render_template('search.html', search_results=results, username=my_name,
                                   userid=userid, loggedin=True)

        return render_template('search.html', search_results=results, loggedin=False)

    if session.get('loggedin', None):
        userid = session.get('userid', None)
        my_name = session.get('my_name', None)

        return render_template('search.html', search_results=results, username=my_name,
                                   userid=userid, loggedin=True)

    return render_template('search.html', search_results=results, loggedin=False)

def compute_jaccard_index(set_1, set_2):
    n = len(set_1.intersection(set_2))
    return n / float(len(set_1) + len(set_2) - n)


def friend_recommendation(userid, friends):

    friends = [int(x) for x in friends]

    def get_friends(id):
        query = 'SELECT user_id1, user_id2 FROM FRIENDSHIP'
        cursor.execute(query)
        friends = []
        for item in cursor:
            if int(id) == int(item[0]):
                friends.append(int(item[1]))
            elif int(id) == int(item[1]):
                friends.append(int(item[0]))

        return friends

    def get_name(id):
        query = 'SELECT user_id, first_name, last_name FROM USERS'
        cursor.execute(query)
        for item in cursor:
            if int(item[0]) == int(id):
                return item[1]+' '+item[2]

    suggestions = dict()

    for i in range(len(friends)):
        one_hop_friends = get_friends(friends[i])
        for i in range(len(one_hop_friends)):
            if one_hop_friends[i] != int(userid) and (one_hop_friends[i] not in friends):
                if one_hop_friends[i] not in suggestions.keys():
                    suggestions[one_hop_friends[i]] = 1
                else:
                    suggestions[one_hop_friends[i]] += 1

    sug_friends = suggestions.items()

    sug_friends = list(reversed(sorted(sug_friends, key=lambda x: x[1])))

    return [[x[0], get_name(x[0])] for x in sug_friends]

@app.route('/recommendations/<id>', methods=['GET', 'POST'])
def recommendations(id):

    #get all tags of photos of user

    query = 'SELECT album_id FROM ALBUMS WHERE user_id = %s'
    cursor.execute(query, [int(id)])

    albums_of_id = []
    for item in cursor:
        albums_of_id.append(item[0])

    query = 'SELECT photo_id FROM PHOTOS WHERE album_id = %s'
    photos_of_id = []
    for album in albums_of_id:
        cursor.execute(query, [int(album)])
        for item in cursor:
            photos_of_id.append(int(item[0]))

    query = 'SELECT HASHTAG FROM ASSOCIATE WHERE photo_id = %s'
    tags_of_id = []
    count_tags_of_id = dict()
    for photo in photos_of_id:
        cursor.execute(query, [int(photo)])
        for item in cursor:
            if item[0] in tags_of_id:
                count_tags_of_id[item[0]] += 1
            else:
                count_tags_of_id[item[0]] = 1
                tags_of_id.append(item[0])

    #get top 5 commonly used tags
    tag_list = count_tags_of_id.items()
    tag_list = list(reversed(sorted(tag_list, key=lambda x: x[1])))[:5]
    top5_tags = [x[0] for x in tag_list]

    recommended_photos = photo_search(top5_tags)

    #remove pics of the user
    recommended_photos = [x for x in recommended_photos if int(x[0]) not in photos_of_id]

    userid = session.get('userid', None)
    my_name = session.get('my_name', None)

    return render_template('recommendations.html', userid=userid, username=my_name, recommended_photos=recommended_photos)


if __name__=='__main__':
    app.secret_key = os.urandom(100)
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
