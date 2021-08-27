import datetime
import serial
import time
from datetime import date, datetime
import threading
import tkinter
import json
import random

import sys
import os

f = open('/home/pi/Documents/pythonBC95-G/config.json')
mqttConfig = json.load(f)

userMode = ""


if len(sys.argv) < 1:
    print("please read help : python main.py -h")
    exit()

if sys.argv[1] == "-h":
    print("python main.py \"data\"")
    exit()

if sys.argv[1] == "-rd":
    userMode = "rd"

jsStrBC95G = {
    "ATE0" : ("ATE0\r\n").encode(),
    "KEEPALIVE": ("AT+QMTCFG=\"KEEPALIVE\",0,30\r\n").encode(),
    "OPEN": ("AT+QMTOPEN=0,\""+mqttConfig['mqttHost']+"\","+str(mqttConfig['mqttPort'])+"\r\n").encode(),
    "isOPEN": ("+QMTOPEN: 0,\""+mqttConfig['mqttHost']+"\","+str(mqttConfig['mqttPort'])),
    "CONN": ("AT+QMTCONN=0,\""+mqttConfig['mqttClientID']+"\",\""+mqttConfig['mqttUser']+"\",\""+mqttConfig['mqttPass']+"\"\r\n").encode(),
    "isCONN": ("+QMTCONN: 0,3"),
    "SUB": ("AT+QMTSUB=0,1,\""+mqttConfig['mqttTopSUB']+"\"\r\n").encode(),
    "PUB": ("AT+QMTPUBEX=0,0,0,0,\""+mqttConfig['mqttTopPUB']+"\","+sys.argv[1]+"\r\n").encode(),
    "DISC":("AT+QMTDISC=0\r\n").encode(),
    "CLOSE":("AT+QMTCLOSE=0\r\n").encode(),
    "CheckOpen":("AT+QMTOPEN?\r\n").encode(),
    "CheckConnection":("AT+QMTCONN?\r\n").encode(),

}

print(jsStrBC95G["KEEPALIVE"])
print(jsStrBC95G["OPEN"])
print(jsStrBC95G["CONN"])
print(jsStrBC95G["SUB"])
print(jsStrBC95G["PUB"])


def clearSerial(ser):
    while ser.inWaiting():
        ser.read()
    print(ser.port, end=" clear\r\n")
    return True

def bc95g_CheckConnection(ser):
    ser.write(jsStrBC95G["CheckConnection"])
    timeOut =datetime.now().timestamp()
    while True:
        if datetime.now().timestamp() - timeOut > 5:
            return 0
        if ser.inWaiting():
            strBC95 = ser.readline().decode().strip()
            print(strBC95)
            if strBC95 == jsStrBC95G["isCONN"]:
                print("BC95G is connected")
                return 1
            elif strBC95 =="ERROR":
                print("BC95G is not connect")
                return 0

def bc95g_CheckOpen(ser):
    ser.write(jsStrBC95G["CheckOpen"])
    timeOut =datetime.now().timestamp()
    while True:
        if datetime.now().timestamp() - timeOut > 5:
            return 0
        if ser.inWaiting():
            strBC95 = ser.readline().decode().strip()
            print(strBC95)
            if strBC95 == jsStrBC95G["isOPEN"]:
                print("BC95G is opened")
                return 1
            elif strBC95 =="ERROR":
                print("BC95G is not open")
                return 0
        
def bc95g_Ready(ser):
    ser.write(jsStrBC95G["ATE0"])
    state = False
    timeOut = datetime.now().timestamp()
    while not state:
        if datetime.now().timestamp() - timeOut > 3:
            ser.write(b'ATE0\r\n')
            timeOut = datetime.now().timestamp()
        if ser.inWaiting():
            strBC95 = ser.readline().decode().strip()
            if strBC95 == "OK":
                state = True
    print("BC95-G ready")
    return 1


def bc95g_KEEPALIVE(ser):
    ser.write(jsStrBC95G["KEEPALIVE"])
    state = False
    timeOut = datetime.now().timestamp()
    while not state:
        if datetime.now().timestamp() - timeOut > 3:
            ser.write(jsStrBC95G["KEEPALIVE"])
            timeOut = datetime.now().timestamp()
        if ser.inWaiting():
            strBC95 = ser.readline().decode().strip()
            if strBC95 == "OK":
                state = True
            elif strBC95 == "ERROR":
                ser.write(jsStrBC95G["CLOSE"])
    print("BC95-G KEEPALIVE complete")
    return 1


def bc95g_QMTOPEN(ser):
    ser.write(jsStrBC95G["OPEN"])
    state = False
    timeOut = datetime.now().timestamp()
    while not state:
        if datetime.now().timestamp() - timeOut > 3:
            print(jsStrBC95G["OPEN"])
            ser.write(jsStrBC95G["OPEN"])
            timeOut = datetime.now().timestamp()
        if ser.inWaiting():
            strBC95 = ser.readline().decode().strip()
            print(strBC95)
            if strBC95 == "+QMTOPEN: 0,0":
                state = True
            elif strBC95 == "ERROR":
                ser.write(jsStrBC95G["DISC"])
                ser.write(jsStrBC95G["CLOSE"])
            elif strBC95 == "+QMTCLOSE: 0,0":
                clearSerial(ser)
            elif strBC95 == "+QMTOPEN: 0,-1":
                ser.write(jsStrBC95G["OPEN"])

    print("BC95-G QMTOPEN complete")
    return 1

def bc95g_QMTCONN(ser):
    ser.write(jsStrBC95G["CONN"])
    state = False
    timeOut = datetime.now().timestamp()
    while not state:
        if datetime.now().timestamp() - timeOut > 10:
            ser.write(jsStrBC95G["CONN"])
            timeOut = datetime.now().timestamp()
        if ser.inWaiting():
            strBC95 = ser.readline().decode().strip()
            print(strBC95)
            if strBC95 == "+QMTCONN: 0,0,0":
                state = True
            elif strBC95 == "ERROR":
                ser.write(jsStrBC95G["DISC"])
    print("BC95-G QMTCONN complete")
    return 1

def bc95g_QMTPUBX(ser):
    print(jsStrBC95G["PUB"])
    ser.write(jsStrBC95G["PUB"])
    # ser.write(str(datetime.now().timestamp()).encode())
    state = False
    timeOut = datetime.now().timestamp()
    while not state:
        if datetime.now().timestamp() - timeOut > 10:
            ser.write(jsStrBC95G["PUB"])
            timeOut = datetime.now().timestamp()
        if ser.inWaiting():
            strBC95 = ser.readline().decode().strip()
            print(strBC95)
            if strBC95 == "+QMTPUBEX: 0,0,0":
                state = True
    print("BC95-G QMTPUBX complete")
    return 1
    
# def read_from_port(ser):
#     while True:
#         print(ser.read().decode(), end="")
#         # reading = ser.readline()
#         # handle_data(reading)


# def sendData(ser):
#     while True:
#         cmd = input()
#         # print("user |", end="")
#         # print(str.encode(cmd), end="|\r\n")

#         ser.write(str.encode(cmd))
#         ser.write(b'\r\n')


# def error(serial):
#     serial.write(b'at\r\n')
#     return "error"


# def keepAlive(serial):
#     return "tuesday"


# def QMTOPEN(serial):
#     return "wednesday"


# def QMTCONN(serial):
#     return "thursday"


# def QMTSUB(serial):
#     return "friday"


# def QMTPUB(serial):
#     return "saturday"


# def default():
#     return "Incorrect day"

# switcher = {
#     1: error,
#     2: keepAlive,
#     3: QMTOPEN,
#     4: QMTCONN,
#     5: QMTSUB,
#     6: QMTPUB
# }


# def initBC95_G(sw, serial):
#     return switcher.get(sw, default)(serial)


# serialDataLog = serial.Serial(
#     '/dev/ttyUSB0',
#     baudrate=9600
# )

serialBC95G = serial.Serial(
    mqttConfig["serialBC95GPort"],
    baudrate=mqttConfig["serialBC95GBaudrate"]
)


while not clearSerial(serialBC95G):
    pass


if bc95g_CheckConnection(serialBC95G) == 1 :
    if bc95g_CheckOpen(serialBC95G) == 1:
        if userMode =="rd":
            while True :
                jsStrBC95G["PUB"] = ("AT+QMTPUBEX=0,0,0,0,\""+mqttConfig['mqttTopPUB']+"\","+ str(random.randrange(0,10))+"\r\n").encode()
                bc95g_QMTPUBX(serialBC95G)
                time.sleep(15)
        else:
            bc95g_QMTPUBX(serialBC95G)
else :
    bc95g_Ready(serialBC95G)
    bc95g_KEEPALIVE(serialBC95G)
    bc95g_QMTOPEN(serialBC95G)
    bc95g_QMTCONN(serialBC95G)


exit()



thBC95G = threading.Thread(target=read_from_port, args=(serialBC95G))
thBC95G.start()


# datetime.now().timestamp()  return time in float seconds
timeOutLoop = datetime.now().timestamp()


# exit()

if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

bc95Buffer = []
bc95G_Isconnect = False

# create main window
master = tkinter.Tk()
master.title("BC95-G")
master.geometry("1024x600")
# set full screen
master.attributes('-fullscreen', True)
# make a label for the window
label1 = tkinter.Label(master, text='BC95-G')
# Lay out label
label1.pack()
# Run forever!




thBC95G = threading.Thread(target=read_from_port, args=(serialBC95G))
thBC95G.start()
thUser2BC95 = threading.Thread(target=sendData,args=(serialBC95G))
thUser2BC95.start()
# master.mainloop()

# bc95_IsConnect=False

initBC95_G(1, serialBC95G)
while True:
    pass
