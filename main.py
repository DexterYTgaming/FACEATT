import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("faceatt.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceatt-3f797-default-rtdb.firebaseio.com/",
    'storageBucket': "faceatt-3f797.appspot.com"
})

bucket=storage.bucket()
imgStudent = []
folderpath='Training_images'
images = []
classNames = []
counter=0
id=-1
x=0
# importing student images
pathlist=os.listdir(folderpath)
print(pathlist)
path1 = 'D:\minor\FaceAttendance-main\Training_images'

for path in pathlist:
    images.append(cv2.imread(os.path.join(folderpath,path)))
    classNames.append(os.path.splitext(path)[0]) 
    
    fileName=f'{folderpath}/{path}'
    bucket=storage.bucket()
    blob=bucket.blob(fileName)
    blob.upload_from_filename(fileName)


myList = os.listdir(path1)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path1}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)


def findEncodings(images):
    encodeList = []


    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList



def markAttendance(Enrol):
    with open('D:\minor\FaceAttendance-main\Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
            if Enrol not in nameList:
                x = datetime.now()
                print(x)
                f.writelines(f'\n{Enrol}')
                break
            if Enrol in nameList:
                print('already marked')
                break
encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap = cv2.VideoCapture(0)

if __name__ == '__main__':
    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)
            # print(matchIndex)

            if matches[matchIndex]:
                Enrol = classNames[matchIndex].upper()
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (255, 0, 0), cv2.FILLED)
                cv2.putText(img, Enrol, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                id=classNames[matchIndex]#id is name 
                if counter==0:
                    counter=1
                    
            if counter!=0:
                if counter==1:
                    #get the data
                    studentInfo=db.reference(f'Students/{id}').get()
                    print(studentInfo)
                    #getting image from storage
                    blob=bucket.get_blob(f'Training_images/{id}.jpg')
                    array= np.frombuffer(blob.download_as_string(),np.uint8)
                    imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                    
                        #update the database
                    datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],"%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                    print(secondsElapsed)
                    ref=db.reference(f'Students/{id}')
                    studentInfo['Total_attendance']+=1
                    ref.child('Total_attendance').set(studentInfo['Total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    counter+=1
                    
                nameFile = open('D:\minor\FaceAttendance-main\Attendance.csv', 'r+')
                nameList = nameFile.readlines()
                for line in nameList:
                    entry = line.split(',')
                    if Enrol in entry:
                        print('already marked')
                        break
                else:
                    markAttendance(Enrol)
                    counter=1
                    break

        # exit the program if the user presses 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        cv2.imshow('Face Recognition System', img)
        cv2.waitKey(1)