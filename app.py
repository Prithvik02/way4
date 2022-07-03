from flask import Flask, request,render_template, redirect, url_for, session
from datetime import timedelta, datetime, date
import sqlite3

import random
from dotenv import load_dotenv
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

con = sqlite3.connect('tracker.db', check_same_thread=False)
c = con.cursor()
 
app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=5)
app.secret_key = b'_5#y3L"F4Q8z\n\xec]/'

load_dotenv()
client = Client()

def respond(message):
    response = MessagingResponse()
    response.message(message)
    return str(response)

@app.route('/message', methods=['POST'])
def reply():
    lat = request.form.get('Latitude')
    lng = request.form.get('Longitude')
    if lat:
        sql_command2 = f"SELECT * FROM Alerts;"
        c.execute(sql_command2)
        rows = c.fetchall()
        str=''
        for i in rows:
            from geopy import distance
            center_point = [{'lat': float(lat), 'lng': float(lng)}]
            test_point = [{'lat': float(i[2]), 'lng': float(i[3])}]
            radius = 5
            center_point_tuple = tuple(center_point[0].values())
            test_point_tuple = tuple(test_point[0].values())
            dis = distance.distance(center_point_tuple, test_point_tuple).km
            if dis<=radius:
                str = str + i[1] + '//' + 'location at ' + i[2] + ',' + i[3] + '\n'
        return respond(str)
    return respond('Send your location to get nearby alerts')
    
    
    
def generateotp():
    return random.randrange(100000,999999)
def getOTPFromAPI(userNumber):
    account_sid = 'AC10c29692a537d92524ee5a93b2084394'
    auth_token = 'e08ce7939e62d7e4860f1569964fb561'
    client = Client(account_sid, auth_token)
    otp=generateotp()
    message = client.messages.create(
                            messaging_service_sid='MGa22edbe7f73b489b8a68da260eed8ee2',
                            body="Your OTP to verify for Way4 is " + str(otp) + " .It will be valid for 3 minutes.",
                            to=userNumber
                            )
    print(message.sid)
    if message.sid:
        return otp
    else:
        return False

@app.route('/')
def starting1():
    session.pop('username', None)
    return render_template("base.html")

@app.route('/signup', methods=['GET', 'POST'])
def starting2():
    error = None
    if request.method == 'POST':
        
        name = request.form.get('name')
        phone = request.form.get('phone')
        
        otp = getOTPFromAPI(phone)
        
        uname = request.form.get('username')
        passw = request.form.get('pass')
        statement = f"SELECT * from LOGIN WHERE username = '{uname}';"
        c.execute(statement)
        data1 = c.fetchone()
        
        statement = f"SELECT * from LOGIN WHERE phone = '{phone}';"
        c.execute(statement)
        data2 = c.fetchone()
        
        if data1:
            error = 'Username already Taken'
            return render_template("indexsp.html", error = error)
        else:
            if data2:
                error = 'Given Phone Number already Used'
                return render_template("indexsp.html", error = error)
            else:
                c.execute("INSERT OR IGNORE INTO LOGIN (NAME,PHONE,USERNAME,PASSWORD) VALUES (?,?,?,?)", (name,phone,uname,passw))
                con.commit()
                return redirect(url_for('otpc',uname=uname,otp=otp))
    return render_template("indexsp.html")

templist = []

@app.route('/otpverify', methods=['GET', 'POST'])
def otpc():
    global templist
    error = None
    uname = request.args.get('uname')
    otp = request.args.get('otp')
    templist.append(uname)
    templist.append(otp)
    if request.method == 'POST':
        code = request.form.get('otp')
        if templist[1] == code:
            error = 'You Can Sign In Now'
            templist = []
            return render_template("index.html", error = error)
        else:
            error = 'Incorrect OTP, Sign Up Again :('
            c.execute(f"DELETE FROM LOGIN WHERE USERNAME = '{templist[0]}'")
            con.commit()
            templist = []
            return render_template("indexsp.html", error = error)
    return render_template("otpverify.html",error = error)
    
            


@app.route('/signin', methods=['GET', 'POST'])
def starting3():
    error = None
    session.pop('username', None)
    if request.method == 'POST':
        uname = request.form.get('username')
        passw = request.form.get('pass')
        statement = f"SELECT * from LOGIN WHERE username = '{uname}';"
        c.execute(statement)
        data = c.fetchone()
        if data and passw == data[3]:
            session['username'] = uname
            return redirect(url_for('starting4', uuname = uname))
        elif not data:
            error = 'Username not found, SignUp Now'
            return render_template("index.html", error = error)
        else:
            error = 'Incorrect Password'
            return render_template("index.html", error = error)
    return render_template("index.html")

@app.route('/user/<uuname>',methods=['GET', 'POST'])
def starting4(uuname):
    statement = f"SELECT * from LOGIN WHERE username = '{uuname}';"
    c.execute(statement)
    data = c.fetchone()
    if data:
        if request.method == 'POST':
            description = request.form.get('description')
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')
            c.execute("INSERT INTO {} (username,description,latitude,longitude) VALUES (?,?,?,?)".format('Alerts'), (uuname,description,latitude,longitude))
            con.commit()
            sql_command3 = f"SELECT * FROM Alerts where username = '{uuname}';"
            c.execute(sql_command3)
            rows = c.fetchall()
            return render_template("raisealert.html",uuname = uuname, rows = rows)
        sql_command1 = """CREATE TABLE IF NOT EXISTS {} ( 
                username TEXT NOT NULL,
                description TEXT NOT NULL,
                latitude TEXT NOT NULL, 
                longitude TEXT NOT NULL);""".format('Alerts')
        c.execute(sql_command1)
        sql_command2 = f"SELECT * FROM Alerts where username = '{uuname}';"
        c.execute(sql_command2)
        rows = c.fetchall()

        if 'username' in session:
            session.permanent = True
            return render_template("raisealert.html",uuname = uuname, rows = rows)
        else:
            return render_template("index.html",error = "Session Timed Out, Login Again")
    return render_template("index.html", error = "Invalid Access Not Allowed")


@app.route('/view/<uuname>',methods=['GET', 'POST'])
def starting5(uuname):
    statement = f"SELECT * from LOGIN WHERE username = '{uuname}';"
    c.execute(statement)
    data = c.fetchone()
    if data:
        sql_command2 = f"SELECT * FROM Alerts where username != '{uuname}';"
        c.execute(sql_command2)
        rows = c.fetchall()

        if 'username' in session:
            session.permanent = True
            return render_template("viewalert.html",uuname = uuname, rows = rows)
        else:
            return render_template("index.html",error = "Session Timed Out, Login Again")
    return render_template("index.html", error = "Invalid Access Not Allowed")

@app.route('/maps/<uuname>',methods=['GET', 'POST'])
def starting6(uuname):
    statement = f"SELECT * from LOGIN WHERE username = '{uuname}';"
    c.execute(statement)
    data = c.fetchone()
    if data:
        sql_command2 = f"SELECT latitude,longitude FROM Alerts;"
        c.execute(sql_command2)
        rows = c.fetchall()
        # print(rows)
        
        final_rows = []
        for i in rows:
            final_rows.append(i[0])
            final_rows.append(i[1])
            
        # print(final_rows)
        if 'username' in session:
            session.permanent = True
            return render_template("map.html",uuname = uuname,rows = final_rows)
        else:
            return render_template("index.html",error = "Session Timed Out, Login Again")
    return render_template("index.html", error = "Invalid Access Not Allowed")
