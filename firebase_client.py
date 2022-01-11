from dqrobotics.interfaces.vrep import DQ_VrepInterface
from dqrobotics.utils.DQ_Math import deg2rad, rad2deg
from firebase_config import firebaseConfig
import serial
import json
import PySimpleGUIQt as sg
import time
from vrep_functions_and_constants import ParseSerialInput, ParseInputType

import firebase_admin

from firebase_admin import db
from firebase_admin import credentials

cred = credentials.Certificate("icpviiiteleoperatedrobots-firebase-adminsdk-2ekzx-7f223412d4.json")
default_app = firebase_admin.initialize_app(cred, {
	'databaseURL':"https://icpviiiteleoperatedrobots-default-rtdb.asia-southeast1.firebasedatabase.app/"
	})

ref = db.reference("/")

# print(f'Connected to firebase: {firebase}, db: {db}')

ser = serial.Serial('COM9', 9600, timeout=1, write_timeout=0)
print(f'Serial connection made: {ser}')

# parser = ParseSerialInput()

layout = [

]


while True:
    print('While True')
    # time.sleep(.1)
    print('Slept')
    data = ref.get()['angles']
    print(f'Got values: {data}')
    t1 = data['t1']
    t2 = data['t2']
    t3 = data['t3']
    t4 = data['t4']
    t5 = data['t5']
    t6 = data['t6']
    angles = f'{t1} {t2} {t3} {t4} {t5} {t6}\n'
    try:
        print(f"Data from arduino: {ser.readline()}")
        ser.write(angles.encode('utf-8'))
    except serial.SerialTimeoutException:
        print('Exception')
    print('Data written to serial')
    print(angles)