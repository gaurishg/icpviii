from dqrobotics.interfaces.vrep import DQ_VrepInterface
from dqrobotics.utils.DQ_Math import deg2rad, rad2deg
from firebase_config import firebaseConfig
import serial
import json
import pyrebase
import PySimpleGUIQt as sg
import time
from vrep_functions_and_constants import ParseSerialInput, ParseInputType

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()
auth = firebase.auth()

print(f'Connected to firebase: {firebase}, db: {db}')

ser = serial.Serial('COM9', 9600, timeout=1, write_timeout=0)
print(f'Serial connection made: {ser}')

# parser = ParseSerialInput()

layout = [

]


while True:
    print('While True')
    # time.sleep(.1)
    print('Slept')
    data = db.get().val()['angles']
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