import os
# Importing the necessary Firebase admin goodies
import json
import firebase_admin
from firebase_admin import credentials, db


from hashfn import *
from datetime import date, timedelta, datetime

from models.m_schedule import *

periodReplacement = '__00__'
dateformat = "%Y-%m-%d"
# Initializing the Firebase app with your service account key
cred = credentials.Certificate('maec-news-firebase-adminsdk-4xmts-47b63a3d7f.json')
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://maec-news-default-rtdb.firebaseio.com/'
})


def getMyChannels(userid):
    allsocialmedias = ['youtube', 'facebook', 'twitter', 'tiktok']
    mysocialmedia =[] 
    for sm in allsocialmedias:
         ref = db.reference(f'social-media/{sm}/{userid}')
         exist = ref.get()
         if exist:
            mysocialmedia.append(sm);
    return mysocialmedia;

def getPeriodReplacement(strValue):
     return strValue.replace('.',periodReplacement)

def createUser(replacedEmail, password, ppProfileGroupId):

    key = replacedEmail
    ref =db.reference('users')
    if ref.child(key).get():
        raise Exception("Suchnerror exist")
    hashpassword = getHash(password)
    ref.child(key).child('password').set(hashpassword)
    ref.child(key).child('ppProfileGroupId').set(ppProfileGroupId)

def isValidUser(email, password):
    ref =db.reference('users')
    key =  getPeriodReplacement(email)
    hashedPassword = ref.child(key).child('password').get()
    ppProfileGroupId = ref.child(key).child('ppProfileGroupId').get()
    if hashedPassword == getHash(password):
        return True, ppProfileGroupId
    return False, ppProfileGroupId

def getCorrectType(type):
    ltype = type
    if type == "google":
        ltype = 'youtube'
    return ltype


def get_firebase_cred(type, userid):
   
    ltype = getCorrectType(type)
    key =  getPeriodReplacement(userid)

    ref = db.reference(f'social-media/{ltype}/{key}')

    data = ref.get()
    
    return data

def getFormatedDate(date):
    return date.strftime(dateformat)

def add_firebase_Credit(type, userid, email, data):

    ltype = getCorrectType(type)
    
    ref = db.reference(f'social-media/{ltype}')
    key =  getPeriodReplacement(userid)
    ref.child(key).set(data)
    ref.child(key).child('email').set(email or '')

def print_all__():
    users = db.reference('users/').get()
    for key,value in users.items():
        for k, v in value.get('social').items():
            print(f"Key: {k}, Value: {v}")

def print_all(type,email):

    ref = db.reference('server/you')
    all_data= ref.get()
    print(all_data)

    print("Iterating through data using .each():")

    for key, value in all_data.items():
        print(f"---------------------")
        print(f"Key: {key}, Value: {value}")

    ref.child('emails').child('purusingh').set({'avc':12, 'bcd':2})
    

    #for user in all_data.each():
    #    print(f"Key: {user.key()}") # Get the unique key of the child
    #    print(f"Value: {user.val()}") # Get the data (value) of the child
def insertScheduleTest():
    #formatted_date = datetime.now().strftime("%Y-%m-%d")
    keyDate =datetime.today()
    userid = "purutest@test.com"
    data = MSchedule("10",20); 

    insertSchedule(userid , keyDate, data)

    keyDate = date.today() + timedelta(days=10)
    insertSchedule(userid , keyDate, data)
    
    keyDate =  date.today() + timedelta(days=30)
    insertSchedule(userid , keyDate, data)

def insertSchedule(userid,date,value):
    userid = getPeriodReplacement(userid)
    ref = db.reference(f'users/{userid}/schedule')
    fdate  = getFormatedDate(date)
    ref.child(fdate).set(json.dumps(value, indent=4, cls=MScheduleEncoder))


def getSchedue(userid, startdate, enddae):
     userid =getPeriodReplacement(userid)
     ref =db.reference(f'users/{userid}/schedule')
     startdate  = getFormatedDate(startdate)
     enddae  = getFormatedDate(enddae)
     data = ref.order_by_key().start_at(startdate).end_at(enddae).get()
     return data


def createSchedule(userid,type,Schedule_Type,frequency,scheduletime):
    key =  getPeriodReplacement(userid)
    
    ref =db.reference('users')
    ltype = getCorrectType(type)
    social = ref.child(key).child('social').child(ltype)
    social.child('Schedule_Type').set(Schedule_Type)
    social.child('frequency').set(frequency)
    social.child('scheduletime').set(scheduletime)

def last_day_of_month(any_day):
    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = any_day.replace(day=28) + timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    return next_month - timedelta(days=next_month.day)

if __name__ == '__main__':   
    insertScheduleTest()
    #print_all__();