import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("faceatt.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceatt-ea0e3-default-rtdb.firebaseio.com/"
})

ref=db.reference('Students')
data={
    
        "20103188": 
        {
            "Name": "Rushil Gupta",
            "Course": "B.Tech",
            "Branch": "CSE",
            "Batch": "B7",
            "Subject": "Software Engineering",
            "Total_attendance": 9,
            "last_attendance_time":"2023-05-04  13:50:00" 
        },
        "messi": 
        {
            "Name": "messi",
            "Course": "B.Tech",
            "Branch": "CSE",
            "Batch": "B7",
            "Total_attendance": 9,
            "last_attendance_time":"2023-05-04  13:50:00" 
        }
}
for key,value in data.items():
    ref.child(key).set(value)