import tkinter as tk
from tkinter import Message, Text
import cv2
import os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
import tkinter.ttk as ttk
import tkinter.font as font
import os

import PySimpleGUI as sg

window = tk.Tk()
window.title("Face Recognition Based Attendance System")

dialog_title = 'QUIT'
dialog_text = 'Are you sure?'

window.configure(background='#2b2d42')
window.geometry("1900x1000")


window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)


message = tk.Label(window, text="Face Recognition Based Attendance System", bg="#8d99ae",
                   fg="#edf2f4", width=50, height=3, font=('times', 30, 'italic bold underline'))

message.place(x=200, y=20)

lbl = tk.Label(window, text="Enter ID", width=20, height=2,
               fg="#edf2f4", bg="#ef233c", font=('times', 15, ' bold '))
lbl.place(x=400, y=200)

txt = tk.Entry(window, width=20, bg="#8d99ae",
               fg="#edf2f4", font=('times', 15, ' bold '))
txt.place(x=700, y=215)

lbl2 = tk.Label(window, text="Enter Name", width=20, fg="#edf2f4",
                bg="#ef233c", height=2, font=('times', 15, ' bold '))
lbl2.place(x=400, y=300)

txt2 = tk.Entry(window, width=20, bg="#8d99ae",
                fg="#edf2f4", font=('times', 15, ' bold '))
txt2.place(x=700, y=315)

lbl3 = tk.Label(window, text="Status : ", width=20, fg="#edf2f4",
                bg="#ef233c", height=2, font=('times', 15, 'bold'))
lbl3.place(x=400, y=400)

message = tk.Label(window, text="", bg="#ef233c", fg="#edf2f4", width=40,
                   height=2, activebackground="#d90429", font=('times', 15, ' bold '))
message.place(x=700, y=400)

lbl3 = tk.Label(window, text="Attendance : ", width=20,
                fg="#edf2f4", bg="#ef233c", height=2, font=('times', 15))
lbl3.place(x=400, y=650)


message2 = tk.Label(window, text="", fg="#edf2f4", bg="#ef233c",
                    activeforeground="green", width=40, height=5, font=('times', 15, ' bold '))
message2.place(x=700, y=650)


def clear():
    txt.delete(0, 'end')
    res = ""
    message.configure(text=res)


def clear2():
    txt2.delete(0, 'end')
    res = ""
    message.configure(text=res)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def TakeImages():
    Id = (txt.get())
    name = (txt2.get())
    if (is_number(Id) and name.isalpha()):
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascadePath)
        sampleNum = 0
        while (True):
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                # incrementing sample number
                sampleNum = sampleNum+1
                # saving the captured face in the dataset folder TrainingImage
                cv2.imwrite("TrainingImage\ "+name + "."+Id + '.' +
                            str(sampleNum) + ".jpg", gray[y:y+h, x:x+w])
                # display the frame
                cv2.imshow('frame', img)
            # wait for 100 miliseconds
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            # break if the sample number is morethan 100
            elif sampleNum > 59:
                break
        cam.release()
        cv2.destroyAllWindows()
        res = "Images Saved for ID : " + Id + "   Name : " + name
        row = [Id, name]
        with open('StudentDetails\StudentDetails.csv', 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
        message.configure(text=res)
        with open('Attendance\Attendance_Sheet.csv', 'a+') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(row)
        csvFile.close()
        message.configure(text=res)
    else:
        if (is_number(Id)):
            res = "Enter Alphabetical Name"
            message.configure(text=res)
        if (name.isalpha()):
            res = "Enter Numeric Id"
            message.configure(text=res)

    if os.path.exists("TrainingImage\Trainner.yml"):
        os.remove("TrainingImage\Trainner.yml")

def TrainImages():

    if os.path.exists("TrainingImage/Trainner.yml"):
        os.remove("TrainingImage/Trainner.yml")

    else:
        recognizer = cv2.face_LBPHFaceRecognizer.create()
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(harcascadePath)
        faces, Id = getImagesAndLabels("TrainingImage")
        recognizer.train(faces, np.array(Id))
        recognizer.save("TrainingImage\Trainner.yml")
        res = "Image Trained"
        message.configure(text=res)


def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]

    faces = []
    Ids = []
    for imagePath in imagePaths:
        pilImage = Image.open(imagePath).convert('L')
        imageNp = np.array(pilImage, 'uint8')
        Id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces.append(imageNp)
        Ids.append(Id)
    return faces, Ids

def Defaulters():
    # Load the attendance data from the CSV file
    attendance = pd.read_csv('Attendance\Attendance_Sheet.csv')

    # Calculate the defaulters list
    threshold = 2
    attendance['Defaulters'] = attendance.iloc[:,2:].sum(axis=1) < threshold
    attendance.loc[attendance['Defaulters'], 'Defaulters'] = True

    # Save the attendance report to a new CSV file
    attendance.to_csv('Defaulters_List.csv', index=False)
    res = "Defaulters File Generated"
    message.configure(text=res)


def TrackImages():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    # cv2.createLBPHFaceRecognizer()
    recognizer.read("TrainingImage\Trainner.yml")
    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath)
    df = pd.read_csv("StudentDetails\StudentDetails.csv")
    name_list = []
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    col_names = ['Id', 'Name', 'Date', 'Time']
    attendance = pd.DataFrame(columns=col_names)
    while True:
        ret, im = cam.read()
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(im, (x, y), (x+w, y+h), (225, 0, 0), 2)
            Id, conf = recognizer.predict(gray[y:y+h, x:x+w])
            if (conf < 50):
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(
                    ts).strftime('%H:%M:%S')
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                aa = df.loc[df['Id'] == Id]['Name'].values
                string = str(aa[0])
                name_list.append(string)
                name_list = list(set(name_list))
                print(name_list)

                time_date = datetime.datetime.fromtimestamp(
                    ts).strftime('%Y-%m-%d')
                # frame=pd.read_csv("Attendance\Attendance_Sheet.csv")
                # frame[date]=0
                # row_index = df.index[df['Name'] == string].tolist()[0]
                # # print(row_index)
                # frame.loc[row_index, time_date] = 1
                # # print(frame)
                # frame.to_csv("Attendance\Attendance_Sheet.csv",index=False)

                col = [date]
                # frame=pd.read_csv('Attendance\Attendance.csv')
                # frame[datetime.datetime.fromtimestamp(ts).strftime('%m-%d')] =""

                tt = str(Id)+"-"+aa
                attendance.loc[len(attendance)] = [Id, aa, date, timeStamp]

            else:
                Id = 'Unknown'
                tt = str(Id)
            if (conf > 75):
                noOfFile = len(os.listdir("ImagesUnknown"))+1
                cv2.imwrite("ImagesUnknown\Image"+str(noOfFile) +
                            ".jpg", im[y:y+h, x:x+w])
            cv2.putText(im, str(tt), (x, y+h), font, 1, (255, 255, 255), 2)
        attendance = attendance.drop_duplicates(subset=['Id'], keep='first')
        cv2.imshow('im', im)
        if (cv2.waitKey(1) == ord('q')):
            break
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour, Minute, Second = timeStamp.split(":")
    frame = pd.read_csv("Attendance\Attendance_Sheet.csv")
    frame[date] = 0
    # frame['2023-04-01']=0

    # frame[date]=''
    for row in name_list:
        row_index = df.index[df['Name'] == row].tolist()[0]
        print(row_index)
        frame.loc[row_index, time_date] = 1
        # frame.loc[row_index,'2023-04-01'] = 1

        frame.to_csv("Attendance\Attendance_Sheet.csv", index=False)

    # row_index = df.index[df['Name'] == string].tolist()[0]
    # print(row_index)
    # frame.loc[row_index, time_date] = 1
    # print(frame)
    # frame.to_csv("Attendance\Attendance_Sheet.csv",index=False)
    # fileName="Attendance\Attendance.csv"
    # attendance.to_csv(fileName,index=False)
    # frame=pd.read_csv("D:\FR. CRCE\SEM VI\PBL Mini Project\Face-Recognition-Based-Attendance-System-master\Face-Recognition-Based-Attendance-System-master\StudentDetails\StudentDetails.csv")
    # frame[date]=''
    # row_index = df.index[df['Name'] == string].tolist()[0]
    # print(row_index)
    # df.loc[row_index, time] = 1

    cam.release()
    cv2.destroyAllWindows()
    # print(attendance)
    res = attendance
    message2.configure(text=res)

def display_attendance():
    root = tk.Tk()
    root.title("Attendance sheet")

    class CSVViewer(tk.Frame):
        def __init__(self, master = None):
            super().__init__(master)
            self.master = master
            self.grid()
            self.create_widgets()

        def create_widgets(self):
            with open("Attendance\Attendance_Sheet.csv", newline = '') as csvfile:
                reader = csv.reader(csvfile)
                for i, row in enumerate(reader):
                    for j, item in enumerate(row):
                        label = tk.Label(self, text = item, relief = tk.RIDGE, width = 20)
                        label.grid(row = i, column = j)
    CSVViewer(root)

def display_def():
    root = tk.Tk()
    root.title("Defaulters List")

    class CSVViewer(tk.Frame):
        def __init__(self, master = None):
            super().__init__(master)
            self.master = master
            self.grid()
            self.create_widgets()

        def create_widgets(self):
            with open("Defaulters_List.csv", newline = '') as csvfile:
                reader = csv.reader(csvfile)
                for i, row in enumerate(reader):
                    for j, item in enumerate(row):
                        label = tk.Label(self, text = item, relief = tk.RIDGE, width = 20)
                        label.grid(row = i, column = j)
    CSVViewer(root)

clearButton = tk.Button(window, text="Clear", command=clear, fg="#edf2f4", bg="#ef233c",
                        width=20, height=2, activebackground="#d90429", font=('times', 15, ' bold '))
clearButton.place(x=950, y=200)
clearButton2 = tk.Button(window, text="Clear", command=clear2, fg="#edf2f4", bg="#ef233c",
                         width=20, height=2, activebackground="#d90429", font=('times', 15, ' bold '))
clearButton2.place(x=950, y=300)
takeImg = tk.Button(window, text="Take Images", command=TakeImages, fg="#edf2f4", bg="#3a86ff",
                    width=20, height=3, activebackground="#d90429", font=('times', 15, ' bold '))
takeImg.place(x=50, y=500)
trainImg = tk.Button(window, text="Train Model", command=TrainImages, fg="#edf2f4", bg="#3a86ff",
                     width=20, height=3, activebackground="#d90429", font=('times', 15, ' bold '))
trainImg.place(x=350, y=500)
trackImg = tk.Button(window, text="Mark Attendance", command=TrackImages, fg="#edf2f4",
                     bg="#3a86ff", width=20, height=3, activebackground="#d90429", font=('times', 15, ' bold '))
trackImg.place(x=650, y=500)
Default = tk.Button(window, text="Defaulters", command=Defaulters, fg="#edf2f4",
                     bg="#3a86ff", width=20, height=3, activebackground="#d90429", font=('times', 15, ' bold '))
Default.place(x=950, y=500)
quitWindow = tk.Button(window, text="Quit", command=window.destroy, fg="#edf2f4", bg="#3a86ff",
                       width=20, height=3, activebackground="#d90429", font=('times', 15, ' bold '))
quitWindow.place(x=1250, y=500)

disp_att = tk.Button(window, text="Display Attendance sheet ",command=display_attendance, fg="#edf2f4",
                     bg="#3a86ff", width=20, height=3, activebackground="#d90429", font=('times', 15, ' bold '))
disp_att.place(x=50, y=650)

disp_def = tk.Button(window, text="Display Defaulters sheet ",command=display_def, fg="#edf2f4",
                     bg="#3a86ff", width=20, height=3, activebackground="#d90429", font=('times', 15, ' bold '))
disp_def.place(x=1250, y=650)


window.mainloop()
