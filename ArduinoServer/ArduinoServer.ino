#include <Servo.h>
#include <math.h>

Servo myservos[6];  // create servo object to control a servo
long int pot_values[6] {};
long int servo_angles[6] {};

const long int BASE_HEIGHT = 75; // 75 mm
const long int AB = 85; // 85 mm
const long int BC = 160; // 160 mm
const long int P = AB;
const long int Q = BC;


const long int servo_ports[] = {3, 5, 6, 9, 10, 11};
const long int potentiometer_ports[] = {0, 1, 2, 3, 4, 5};
const long int XMIN = 20; // 20 mm
const long int XMAX = 275; // 160 mm
const long int YMIN = -160;
const long int YMAX = 160;
const long int ZMIN = 0;
const long int ZMAX = 200;

long int x{Q}, y{}, z{P}, t1{}, t2{}, t3{};


struct degree_return_value
{
  long int degree;
  bool error;
};

/**
 * Convert an angle from radian to degree
 */
long int rad2deg(const double rad)
{
  return 180 * rad / M_PI;
}

/**
 * Convert an angle from degree to radians
 */
double deg2rad(const long int deg)
{
  return M_PI * deg / 180;
}

/**
 * Take x and y as input and gives value of 
 * first servo angle between -90 to +90 degrees
 */
long int xy_to_t1(const long int x, const long int y)
{
  return rad2deg(atan2(y, x));
}

degree_return_value xyz_to_t2(const long int x, const long int y, const long int z)
{
  const double r = sqrt(x * x + y * y);
  const double R = sqrt(r * r + z * z);
  const long int phi = rad2deg(atan2(z, r));

  const double cos_theta_q = ((double)P * P + (double)R * R - (double)Q * Q) / (2.0 * P * R);
  if (cos_theta_q > 1 || cos_theta_q < -1)
  {
    return {0, true};
  }
  else
  {
    long int theta_q = rad2deg(acos(cos_theta_q));
    return {90-(theta_q+phi), false};
  }
}

degree_return_value xyz_to_t3(const long int x, const long int y, const long int z)
{
  const double r = sqrt(x * x + y * y);
  const double R = sqrt(r * r + z * z);

  const double cos_theta = ((double)P * P + (double)Q * Q - R * R) / (2.0 * P * Q);
  if (cos_theta > 1 || cos_theta < -1)
  {
    return {0, true};
  }
  else
  {
    return {rad2deg(acos(cos_theta)) - 90, false};
  }
}

degree_return_value xyz_to_beta(const long int x, const long int y, const long int z)
{
  const double R_square = (double)x * x + y * y + z * z;
  const double R = sqrt(R_square);
  const double cos_beta = ((double)P * P + R_square - Q * Q) / (2.0 * P * R);
  if (cos_beta > 1 || cos_beta < -1)
  {
    return {0, true};
  }
  else
  {
    return {rad2deg(acos(cos_beta)), false};
  }
}

long int limit_value(const long int value, const long int min_value = -90, const long int max_value = 90)
{
  if (value < min_value)
    return min_value;
  else if (value > max_value)
    return max_value;
  return value;
}



void setup() {
  for (long int i=0; i<6; ++i)
  {
    myservos[i].attach(servo_ports[i]);
  }
  Serial.begin(9600);
  
  servo_angles[0] = 90;
  servo_angles[1] = 90;
  servo_angles[2] = 90;
  servo_angles[3] = 90;
  servo_angles[4] = 90;
  servo_angles[5] = 180;

  for (long int i=0; i<6; ++i)
  {
    myservos[i].write(servo_angles[i]);
    delay(200);
  }
}

void add_msg(String& msg, const String& str, const long int value)
{
  msg += "\"";
  msg += str + "\"";
  msg += ":";
  msg += value;
  msg += ",";
}

void loop() {

  String msg("UMIBEGIN{");
  msg.reserve(2000);
  add_msg(msg, "BASE_HEIGHT", BASE_HEIGHT);
  add_msg(msg, "AB", AB);
  add_msg(msg, "BC", BC);
  add_msg(msg, "P", P);
  add_msg(msg, "Q", Q);
  add_msg(msg, "XMIN", XMIN);
  add_msg(msg, "XMAX", XMAX);
  add_msg(msg, "YMIN", YMIN);
  add_msg(msg, "YMAX", YMAX);
  add_msg(msg, "ZMIN", ZMIN);
  add_msg(msg, "ZMAX", ZMAX);

  msg += "\"pot_values\":[";
  for (long int i=0; i<6; ++i)
  {
    pot_values[i] = analogRead(potentiometer_ports[i]);
    msg += pot_values[i];
    msg += ",";
  }
   msg += "],";


  msg += "\"coords\":[";
  x = map(pot_values[0], 0, 1023, XMIN, XMAX); // x in mm, I have not started x from 0mm so that our robot does not try to get inside itself
                                            // I have also left negative x because we do not need those for the challenge
  msg += x;
  msg += ",";
  y = map(pot_values[1], 0, 1023, -YMIN, -YMAX); // y in mm
  msg += y;
  msg += ",";
  z = map(pot_values[2], 0, 1023, ZMAX, ZMIN); // z in mm
  msg += z;
  msg += "],";

  add_msg(msg, "x", x);
  add_msg(msg, "y", y);
  add_msg(msg, "z", z);

  long int r = sqrt(x * x + y * y);
  long int phi = rad2deg(atan2(z, r));
  
    
  auto t2_wrapper = xyz_to_t2(x, y, z);
  auto t3_wrapper = xyz_to_t3(x, y, z);

  add_msg(msg, "error_t2", t2_wrapper.error);
  add_msg(msg, "error_t3", t3_wrapper.error);

  if (!t2_wrapper.error && !t3_wrapper.error)
  {
    t2 = t2_wrapper.degree;
    t3 = t3_wrapper.degree;

    servo_angles[1] = map(t2, -90, 90, 0, 180);
    servo_angles[2] = map(t3, -90, 90, 0, 180);
  }
  t1 = xy_to_t1(x, y);
  servo_angles[0] = map(t1, -90, 90, 0, 180);
  servo_angles[3] = map(pot_values[3], 0, 1023, 0, 180);

  long int end_effector_target_angle = map(pot_values[4], 0, 1023, -90, 90);
  servo_angles[4] = limit_value(end_effector_target_angle + t2 - t3);
  servo_angles[4] = map(servo_angles[4], -90, 90, 0, 180);
  servo_angles[5] = map(pot_values[5], 0, 1023, 110, 150);

  

  msg += "\"servo_values\":[";
  for (long int i=0; i<6; ++i)
  {
    myservos[i].write(servo_angles[i]);
    long int angle = map(servo_angles[i], 0, 180, -90, 90);
    msg += angle;
    msg += ",";
  }
  msg += "]";

  msg += "}UMIEND";
  Serial.println(msg);
    delay(5);
//  delay(50);
}
