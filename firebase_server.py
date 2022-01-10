from firebase_config import firebaseConfig
import serial
import json
import pyrebase
import time
from vrep_functions_and_constants import ParseSerialInput, ParseInputType

firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()
print(f'Connected to firebase: {firebase}, db: {db}')

ser = serial.Serial('COM9', 9600, timeout=1)
print(f'Serial connection made: {ser}')

parser = ParseSerialInput()

while True:
    time.sleep(0.2)
    line = ser.readline()
    line = line.decode('utf-8').strip()
    parsed_obj: ParseInputType = parser.parse_serial_msg(line)

    if not parsed_obj['error']:
        t1, t2, t3, t4, t5, t6 = parsed_obj['servo_values']
        db.update(data={
            't1': t1, 
            't2': t2,
            't3': t3,
            't4': t4,
            't5': t5,
            't6': t6
            })
        print(f'Updated data to : {[t1, t2, t3, t4, t5, t6]}')
