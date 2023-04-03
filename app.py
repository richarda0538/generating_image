#General Flask Imports
from flask import Flask, render_template, request, session, redirect, url_for
import json

#For MySQL Database connection
import mysql.connector as mysql

#For OTP validation though mail
from flask_mail import Mail, Message
from random import randint

#For Art Generation
import io
import os
import warnings
from PIL import Image
import PIL
import base64
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

#Importing external files

#Intialization
app = Flask(__name__)
app.secret_key = "richard"



#Connection to the mail server to send OTP
mail = Mail(app)
app.config["MAIL_SERVER"] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'richarda0538@gmail.com'
app.config['MAIL_PASSWORD'] = 'zydmmtbspdsoknat'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


#Connection to the Database
db = mysql.connect(
    host='localhost',
    user='root',
    password='Richard@538',
    database='imagipicto',
    connect_timeout=60
)
cur = db.cursor()



#Index Page
@app.route('/')
def index():
    return render_template("index.html")

#Index Page-2 (After Login/Register)
@app.route('/index2')
def index2():
    return render_template("index2.html")

#Home Page
@app.route('/home')
def homePage():
    return render_template("home_page.html")



#MODULE1 - Registration, Login, Forgot Password, Logout

#Calling Login_Register File
@app.route('/loginRegister')
def loginRegister():
    return render_template('login_register.html')

#Validating Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        db = mysql.connect(
            host='localhost',
            user='root',
            password='Richard@538',
            database='imagipicto',
            connect_timeout=60
        )
        cur = db.cursor()
        login_email = request.form['emailid']
        login_password = request.form['loginpassword']

        sql = "SELECT firstname, lastname, email, password FROM user_data WHERE email=%s"
        cur.execute(sql, [login_email])

        user = cur.fetchone()
        
        session['firstname'] = user[0]
        session['lastname']  = user[1]
        session['email']     = user[2]
        session['password']  = user[3]

        if user:
            if login_email == user[2] and login_password == user[3]:
                return render_template('index2.html')
            else:
                return render_template('login_register.html', abc='Invalid Login!', email=login_email)
        else:
            return render_template('login_register.html', abc='No Rocords Found! Please Register!!')
    except mysql.Error as error:
        print("Error: {}".format(error))
    finally:
        cur.close()
        db.close()
        print("Connection Closed")

#Validating Register
@app.route('/register', methods=['POST'])
def register():
    try:
        db = mysql.connect(
            host='localhost',
            user='root',
            password='Richard@538',
            database='imagipicto',
            connect_timeout=60
        )
        cur = db.cursor()
        session['firstname']        = request.form['firstname']
        session['lastname']         = request.form['lastname']
        session['email']            = request.form['emailid']
        session['password']         = request.form['registerpassword']
        session['confirmpassword']  = request.form['confirmpassword']
        rflag = 0
        sql = "SELECT email FROM user_data WHERE email=%s"
        cur.execute(sql, [session['email']])
        regdata = cur.fetchone()
        
        if regdata:
            if session['email'] == regdata[0]:
                rflag = 1
                return render_template('login_register.html', abc="Account already Exists!", rflag=rflag, email=session['email'], firstname=session['firstname'], lastname=session['lastname'])
        else:
            if session['firstname'].isalpha() and session['lastname'].isalpha():
                if session['password'] == session['confirmpassword']:
                    sql = "INSERT INTO user_data(firstname, lastname, email, password) VALUES(%s, %s, %s, %s)"
                    val = (session['firstname'], session['lastname'], session['email'], session['password'])
                    cur.execute(sql, val)
                    db.commit()
                    
                    return render_template('login_register.html', abc='Registered Successfully! Please Login', rflag=0)
                else:
                    rflag = 1
                    return render_template('login_register.html', abc='Passwords did not match!', rflag=rflag, email=session['email'], firstname=session['firstname'], lastname=session['lastname'])
            else:
                rflag = 1
                return render_template('login_register.html', abc='First and Last Names should be characters', rflag=rflag, email=session['email'])
    except mysql.Error as error:
        print("Error: {}".format(error))
    finally:
        cur.close()
        db.close()
        print("Connection Closed")

#Calling Forgot Password Page
@app.route('/forgot')
def forgotPassword():
    return render_template('forgot_password.html')

#Generate OTP and send to the mail
@app.route('/getOtp', methods=['POST'])
def getOtp():
    try:
        db = mysql.connect(
            host='localhost',
            user='root',
            password='Richard@538',
            database='imagipicto',
            connect_timeout=60
        )
        cur = db.cursor()
        email = request.form['emailid']
        sql = "SELECT email FROM user_data WHERE email=%s"
        cur.execute(sql, [email])
        user = cur.fetchone()
        
        if user:
            if email == user[0]:
                msg = Message(subject='OTP', sender='richardson00538@gmail.com', recipients=[email])
                session['otp'] = randint(000000, 999999)
                msg.body = str(session['otp'])
                mail.send(msg)
                return render_template('forgot_password.html', res='OTP sent!', email=str(email)[2:-2])
            else:
                return render_template('login_register.html', abc='No Rocords Found! Please Register!!')
        else:
            return render_template('login_register.html', abc='No Rocords Found! Please Register!!')
    except mysql.Error as error:
        print("Error: {}".format(error))
    finally:
        cur.close()
        db.close()
        print("Connection Closed")

#Validating the OTP obtained
@app.route('/validate', methods=["POST"])
def validate():
    user_otp = request.form['otp']
    if session['otp'] == int(user_otp):
        return render_template('reset_password.html')
    return render_template('forgot_password.html', abc="Incorrect OTP!")

#Resetting the Password
@app.route('/reset', methods=['POST'])
def reset():
    try:
        db = mysql.connect(
            host='localhost',
            user='root',
            password='Richard@538',
            database='imagipicto',
            connect_timeout=60
        )
        cur = db.cursor()
        newpass = request.form['newpass']
        confirmpass = request.form['confirmpass']
        if newpass==confirmpass:
            sql = "UPDATE user_data SET password=%s WHERE email=%s"
            val = [newpass, (session['emailid'])]
            cur.execute(sql, val)
            db.commit()
            
            return render_template('login_register.html', abc="Password Upadted! Please Re-Login")
        else:
            return render_template('reset_password.html', abc="Invaid!")
    except mysql.Error as error:
        print("Error: {}".format(error))
    finally:
        cur.close()
        db.close()
        print("Connection Closed")


#MODULE2 - Art Generation, Meme Generation, Criminal Face GEneration, Poster PResentation

#Connection to the server
os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
os.environ['STABILITY_KEY'] = 'sk-6YDuV7lnhEJpKCp8TDQVK5GNaTWfpjM6f3Cd2vwVDm81NZrF'
stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'],
    verbose=True,
    engine="stable-diffusion-v1-5"
)

#Function to generate art image
def generateimage(text):
    for resp in text:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER:
                return render_template("home_page.html")
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please modify the prompt and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE:
                insertImage(session['email'], artifact.binary)
                img = Image.open(io.BytesIO(artifact.binary))
                data = io.BytesIO()
                img.save(data, "JPEG")
                encoded_img_data = base64.b64encode(data.getvalue())
                #img.show()
    return encoded_img_data.decode('utf-8')

#ART GENERATION

#Calling Art Generation Page(art)
@app.route('/art')
def art():
    return render_template('art_generation.html')

#Generating the art image based on given input
@app.route('/generateArt', methods=["POST"])
def generateArt():
    text = request.form['t1']
    prompt="detailed 4k resolution image of " + text
    answers = stability_api.generate(
    prompt=prompt,
    #seed=992446758,
    steps=30,
    cfg_scale=8.0,
    width=512,
    height=512,
    samples=1,
    sampler=generation.SAMPLER_K_DPMPP_2S_ANCESTRAL,
    guidance_preset=generation.GUIDANCE_PRESET_FAST_GREEN
    )
    img_data = generateimage(answers)
    return render_template("art_generation.html", img_data=img_data, prompt=text)


#Criminal Face Generation

#Calling Criminal Face Generation Page
@app.route('/criminal_face_generation')
def criminal_face():
    return render_template('criminal_face_generation.html')

#Generating face based on the given text
@app.route('/generateFace', methods=["POST"])
def generateFace():
    gender = request.form['gender']
    age = request.form['age']
    hair = request.form['hair']
    face = request.form['face']
    eyes = request.form['eyes']
    nose = request.form['nose']
    lips = request.form['lips']
    skin = request.form['skin']
    t2 = request.form['t2']
    prompt = "a neat realistic, 8k clear coloured front centered image, "+gender+" of "+age+" years old, "+hair+" hair, "+face+" face, "+eyes+" eyes, "+nose+" nose, "+lips+" lips, "+skin+" skin, "+t2
    answers = stability_api.generate(
    prompt=prompt,
    #seed=992446758,
    steps=30,
    cfg_scale=8.0,
    width=512,
    height=512,
    samples=1,
    sampler=generation.SAMPLER_K_DPMPP_2S_ANCESTRAL,
    guidance_preset=generation.GUIDANCE_PRESET_FAST_GREEN
    )
    img_data = generateimage(answers)
    return render_template("criminal_face_generation.html", img_data=img_data, gender=gender, age=age, hair=hair, face=face, eyes=eyes, nose=nose, lips=lips, skin=skin, t2=t2)

#Meme Generation

#Calling Criminal Face Generation Page
@app.route('/memes_generation')
def memes():
    return render_template('memes_generation.html')

#Generating the art image based on given input
@app.route('/generateMeme', methods=["POST"])
def generateMeme():
    expression=request.form['expression']
    text=request.form['meme']
    answers = stability_api.generate(
    prompt="a meme on "+expression+" with text "+text,
    #seed=992446758,
    steps=30,
    cfg_scale=8.0,
    width=512,
    height=512,
    samples=1,
    sampler=generation.SAMPLER_K_DPMPP_2M
    )
    img_data = generateimage(answers)
    return render_template("memes_generation.html", img_data=img_data, expression=expression, meme=text)

#Poster Generation

#Calling Poster Generation Page
@app.route('/poster_generation')
def poster():
    return render_template('poster_generation.html')

#Generating the poster based on given input
@app.route('/generatePoster', methods=["POST"])
def generatePoster():
    Type=request.form['type']
    text=request.form['text']
    answers = stability_api.generate(
    prompt="a "+Type+" poster on "+text,
    #seed=992446758,
    steps=30,
    cfg_scale=8.0,
    width=512,
    height=512,
    samples=1,
    sampler=generation.SAMPLER_K_DPMPP_2S_ANCESTRAL,
    guidance_preset=generation.GUIDANCE_PRESET_FAST_GREEN
    )
    img_data = generateimage(answers)
    return render_template("poster_generation.html", img_data=img_data, type=Type, text=text)


#MODULE3 - Profile Page

#Storing Searched Images into Database
def insertImage(email, photo):
    try:
        db = mysql.connect(
            host='localhost',
            user='root',
            password='Richard@538',
            database='imagipicto',
            connect_timeout=60
        )
        cur = db.cursor()
        print("Inserting Image into Database")
        sql_insert_image_query = """ INSERT INTO userimages(email, photo) VALUES (%s,%s)"""
        insert_image_tuple = (email, photo)
        result = cur.execute(sql_insert_image_query, insert_image_tuple)
        db.commit()
        
        print("Image inserted successfully into table")
    except mysql.Error as error:
        print("Error: {}".format(error))
    finally:
        cur.close()
        db.close()
        print("Connection Closed")

#Extracting Images from the Database
def extractImage(email):
    try:
        db = mysql.connect(
            host='localhost',
            user='root',
            password='Richard@538',
            database='imagipicto',
            connect_timeout=60
        )
        cur = db.cursor()
        print("Reading BLOB data from python_employee table")
        sql_fetch_image_query = """SELECT * from userimages where email = %s"""
        cur.execute(sql_fetch_image_query, (email,))
        record = cur.fetchall()
        
        pic = []
        Id = []
        for i in record:
            Id.append(i[0])
            pic.append(i[2])
        return Id, pic
    except mysql.Error as error:
        print("Error: {}".format(error))
    finally:
        cur.close()
        db.close()
        print("Connection Closed")

#Opening images in the profile
def openImg(pic):
    if not pic:
        return None
    img = Image.open(io.BytesIO(pic))
    data = io.BytesIO()
    img.save(data, "JPEG")
    encoded_img_data = base64.b64encode(data.getvalue())
    return encoded_img_data.decode('utf-8')

#Delete image from the profile
@app.route('/delete-image/<int:Id>', methods=['POST'])
def deleteImage(Id):
    try:
        db = mysql.connect(
            host='localhost',
            user='root',
            password='Richard@538',
            database='imagipicto',
            connect_timeout=60
        )
        cur = db.cursor()
        sql = """DELETE FROM userimages WHERE id=%s"""
        cur.execute(sql, [Id])
        db.commit()
        print("Image Deleted")
        return redirect(url_for('profilePage'))
    except mysql.Error as error:
        print("Error: {}".format(error))
    finally:
        cur.close()
        db.close()
        print("Connection Closed")

#Delete Account
@app.route('/delete-account')
def deleteAccount():
    try:
        db = mysql.connect(
            host='localhost',
            user='root',
            password='Richard@538',
            database='imagipicto',
            connect_timeout=60
        )
        cur = db.cursor()
        sql = """DELETE FROM userimages WHERE email=%s"""
        cur.execute(sql, [session['email']])
        db.commit()
        sql = """DELETE FROM user_data WHERE email=%s"""
        cur.execute(sql, [session['email']])
        db.commit()
        print("Account Deleted")
        return render_template('login_register.html', abc="Account Deleted!!")
    except mysql.Error as error:
        print("Error: {}".format(error))
    finally:
        cur.close()
        db.close()
        print("Connection Closed")

#Calling Profile Page
@app.route('/profile')
def profilePage():
    Id, images = extractImage(session['email'])
    for i in range(len(images), 30):
        Id.append(None)
        images.append(None)
    return render_template('profile_page.html', name=str(session['firstname']+" "+session['lastname']), email=session['email'],
                                                id1=Id[0], img1=openImg(images[0]),
                                                id2=Id[1], img2=openImg(images[1]),
                                                id3=Id[2], img3=openImg(images[2]),
                                                id4=Id[3], img4=openImg(images[3]),
                                                id5=Id[4], img5=openImg(images[4]),
                                                id6=Id[5], img6=openImg(images[5]),
                                                id7=Id[6], img7=openImg(images[6]),
                                                id8=Id[7], img8=openImg(images[7]),
                                                id9=Id[8], img9=openImg(images[8]),
                                                id10=Id[9], img10=openImg(images[9]),
                                                id11=Id[10], img11=openImg(images[10]),
                                                id12=Id[11], img12=openImg(images[11]),
                                                id13=Id[12], img13=openImg(images[12]),
                                                id14=Id[13], img14=openImg(images[13]),
                                                id15=Id[14], img15=openImg(images[14]),
                                                id16=Id[15], img16=openImg(images[15]),
                                                id17=Id[16], img17=openImg(images[16]),
                                                id18=Id[17], img18=openImg(images[17]),
                                                id19=Id[18], img19=openImg(images[18]),
                                                id20=Id[19], img20=openImg(images[19]),
                                                id21=Id[20], img21=openImg(images[20]),
                                                id22=Id[21], img22=openImg(images[21]),
                                                id23=Id[22], img23=openImg(images[22]),
                                                id24=Id[23], img24=openImg(images[23]),
                                                id25=Id[24], img25=openImg(images[24]),
                                                id26=Id[25], img26=openImg(images[25]),
                                                id27=Id[26], img27=openImg(images[26]),
                                                id28=Id[27], img28=openImg(images[27]),
                                                id29=Id[28], img29=openImg(images[28]),
                                                id30=Id[29], img30=openImg(images[29]))

@app.route('/display')
def display():
    return None



#Running the code
if __name__ == "__main__":
    app.run(debug=True)