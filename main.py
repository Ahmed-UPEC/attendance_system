# Author : SYED Ahmed
# Date : 31-03-2023
# Description : Attendance Management System using Python


# Check list :
# Face detection using OpenCV : done
# Saving the result using MySQL : done
# Using tts to announce the result ie person detected : done


# Importing the required libraries

# Face detection
import face_recognition
import os
import numpy as np
import cv2
import datetime

# TTS
import pyttsx3
engine = pyttsx3.init() # object creation

""" RATE"""
rate = engine.getProperty('rate')   # getting details of current speaking rate
print (rate)                        #printing current voice rate
engine.setProperty('rate', 125)     # setting up new voice rate


"""VOLUME"""
volume = engine.getProperty('volume')   #getting to know current volume level (min=0 and max=1)
print (volume)                          #printing current volume level
engine.setProperty('volume',1.0)    # setting up volume level  between 0 and 1

"""VOICE"""
voices = engine.getProperty('voices')       #getting details of current voice
engine.setProperty('voice', voices[0].id)   #changing index, changes voices. 1 for female/ 0 for male




# Database
import mysql.connector 
# connect to the database "mydatabase"

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="attendance"
)
mycursor = mydb.cursor()
#mycursor.execute("CREATE TABLE attendance (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), timestamp TIMESTAMP)")



# Global variables
global name
name = "Unknown"

def LoadEncodings(dir):
    faces=os.listdir(dir)
    images_known = []
    for x in faces:
        images_known.append(dir+"/"+x)
    known_face_encodings = []
    known_face_names = []
    for x in images_known:
        known_image = face_recognition.load_image_file(x)
        known_face_encoding = face_recognition.face_encodings(known_image,model="small")[0]
        known_face_encodings.append(known_face_encoding)
        known_face_names.append(os.path.basename(x))

    return known_face_encodings,known_face_names



def WebcamFaceRecognition(encodings_path):
    global name, temp_name
    video_capture = cv2.VideoCapture(0)
    known_face_encodings,known_face_names=LoadEncodings(encodings_path)
    temp_name = "" # empty initizing
    while True:
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        print(frame.shape)
        face_locations = face_recognition.face_locations(small_frame,model="hog")
        face_encodings = face_recognition.face_encodings(small_frame, face_locations,model="small")
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            else :
                name = ""
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, os.path.splitext(name)[0], (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        cv2.imshow('Video', frame)
        print("Press q to quit")
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # if name is different from the previous iteration we call greetings
        if name != temp_name and name != "":
            Greetings(name)
            saveResultInDatabase(name)
            temp_name = name # update previous name

    video_capture.release()
    cv2.destroyAllWindows()


def saveResultInDatabase(name):
    name = os.path.splitext(name)[0]

    # check if the name is already in the database
    # if yes we will not insert it again but we update the timestamp
    sql = "SELECT * FROM attendance WHERE name = %s"
    val = (name,)
    mycursor.execute(sql, val)
    myresult = mycursor.fetchall()
    
    # name is detected inside the db
    if len(myresult) != 0:
        # check the timestamp in database and the current timestamp
        # if the difference is less than 30 seconds we will not insert it again
        # else we will insert it
        sql = "SELECT MAX(timestamp) FROM attendance WHERE name = %s"
        val = (name,)
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        for x in myresult:
            print(x[0])
            print(datetime.datetime.now())
            # timestamp difference is less than 30 seconds so we will not insert it
            if (datetime.datetime.now() - x[0]).total_seconds() < 24*3600:
                print("already in the database")
            # add new row when the difference is more than 30 seconds
            else :
                sql = "INSERT INTO attendance (name, timestamp) VALUES (%s, NOW())"
                val = (name,)
                mycursor.execute(sql, val)
                mydb.commit()
                print(mycursor.rowcount, "record inserted.")

        
    # name is not detected inside the db so we insert it
    else :
        # insert the name and the current timestamp in the database
        sql = "INSERT INTO attendance (name, timestamp) VALUES (%s, NOW())"
        val = (name,)

        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")


def Greetings(name):
    # remove the extention .jpg from the name
    name = os.path.splitext(name)[0]
    print(name)
    engine.say("Hello " + name + " How are you ?")
    engine.runAndWait()
    engine.stop()
    


if __name__ == "__main__":
    WebcamFaceRecognition("Attendance System/Faces")
    
