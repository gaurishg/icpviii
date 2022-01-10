#include <Servo.h>

Servo myservos[6];
int servo_ports[] = {3, 5, 6, 9, 10, 11};
int potentiometer_ports[] = {0, 1, 2, 3, 4, 5};
int servo_angles[6] {0, 0, 0, 0, 0, 0};

void setup() {
  Serial.begin(9600);
  
  for (int i=0; i<6; ++i)
  {
    myservos[i].attach(servo_ports[i]);
  }
}

void parseDataFromString(String& str, int arr[6])
{
  str.trim();
  int index = 0;
  if (str.length() > 0)
  {
    String number;
    for (int i=0; i<str.length(); ++i)
    {
      if (isSpace(str[i]))
      {
        arr[index++] = number.toInt();
        number = "";
      }
      else
      {
        number += str[i];
      }
    }
    arr[index] = number.toInt();
  }
}

void loop() {
  if (Serial.available() > 0)
  {
    String str = Serial.readString();
    str.trim();
    parseDataFromString(str, servo_angles);
    Serial.print(str);
    for (int i=0; i<6; ++i)
    {
      Serial.print(" ");
      Serial.print(servo_angles[i]);
    }
    Serial.println();

    for (int i=0; i<6; ++i)
    {
      myservos[i].write(map(servo_angles[i], -90, 90, 0, 180));
    }
  }
  delay(20);
}
