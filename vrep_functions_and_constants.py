from dqrobotics.utils.DQ_Math import deg2rad, rad2deg
from typing import Optional, Tuple, TypedDict
import math
import numpy as np
import json
import ast

AB: int = 85
BC: int = 160
BASE_HEIGHT: int = 75
P: int = AB
Q: int = BC

XMIN: int = 20
XMAX: int = 240
YMIN: int = -160
YMAX: int = 160
ZMIN: int = 0
ZMAX: int = 200

class ParseInputType(TypedDict):
    AB: int
    BC: int
    BASE_HEIGHT: int
    P: int
    Q: int

    XMIN: int
    XMAX: int
    YMIN: int
    YMAX: int
    ZMIN: int
    ZMAX: int

    coords: Tuple[int, int, int]
    pot_values: Tuple[int, int, int, int, int, int]
    servo_values: Tuple[int, int, int, int, int, int]

    x: int
    y: int
    z: int

    error: bool
    error_t2: bool
    error_t3: bool

class ParseSerialInput:
    def __init__(self) -> None:
        self.AB: int
        self.BC: int
        self.BASE_HEIGHT: int
        self.P: int
        self.Q: int
        
        self.XMIN: int
        self.XMAX: int
        self.YMIN: int
        self.YMAX: int
        self.ZMIN: int
        self.ZMAX: int

        self.coords: Tuple[int, int, int]
        self.x: int
        self.y: int
        self.z: int

        self.pot_values: Tuple[int, int, int, int, int, int]
        self.servo_values: Tuple[int, int, int, int, int, int]
    
    def validate_input(self, msg: str) -> bool:
        return msg.startswith("UMIBEGIN{") and msg.endswith("}UMIEND")
    
    def parse_serial_msg(self, msg: str) -> ParseInputType:
        if self.validate_input(msg):
            msg = msg[8:-6]
            # msg_obj = json.loads(msg)
            msg_obj = ast.literal_eval(msg)
            msg_obj['error'] = False
            return msg_obj
        else:
            return {'error': True}

def linear_map(value: int, src_range_start: int, src_range_end: int,
                target_range_start: int, target_range_end: int) -> int:
    src_range = src_range_end - src_range_start
    target_range = target_range_end - target_range_start
    magnification = target_range / src_range
    return magnification * (value - src_range_start) + target_range_start

def xyz_to_t1(x: int, y: int, z: int=0, P: int=0, Q: int=0):
    return round(rad2deg(math.atan2(y, x)))

def xyz_to_t2(x: int, y: int, z: int, P: int=0, Q: int=0) -> Optional[int]:
    r = (x * x + y * y) ** 0.5
    R = (r * r + z * z) ** 0.5
    phi = math.degrees(math.atan2(z, r))

    cos_theta_q = (P * P + R * R - Q * Q) / (2 * P * R)
    if -1 <= cos_theta_q <= 1:
        theta_q = math.degrees(math.acos(cos_theta_q))
        return round(90 - (theta_q + phi))
    else:
        print(f'ERROR in t2, cos_theta_q = {cos_theta_q}')
        return None


def xyz_to_t3(x: int, y: int, z: int, P: int, Q: int)->Optional[int]:
    r = (x * x + y * y) ** 0.5
    R = (r * r + z * z) ** 0.5
    
    cos_theta = (P * P + Q * Q - R * R) / (2 * P * Q)

    if -1 < cos_theta < 1:
        return round(math.degrees(math.acos(cos_theta)) - 90)
    else:
        print('ERROR in t3')
        return None


class ReturnValueOfAnglesToXyz(TypedDict):
    B: Tuple[int, int, int]
    C: Tuple[int, int, int]

def angles_to_xyz(t1: int, t2: int, t3: int, P: int, Q: int) -> ReturnValueOfAnglesToXyz:
    # Calculate X and Z without t1 rotation
    # A is at (0, 0, 0), get position of B (, , )
    B_wrt_A = np.round(np.array((
        AB * math.sin(math.radians(t2)),
        0,
        AB * math.cos(math.radians(t2)),
        )), decimals=0)

    C_wrt_B = np.round(np.array((
        BC * math.cos(math.radians(t2 - t3)),
        0,
        -BC * math.sin(math.radians(t2 - t3)),
    )), decimals=0)

    C_wrt_A = B_wrt_A + C_wrt_B

    # Now calculate the rotation, z will not change
    return {
        "B": (
            round(B_wrt_A[0]),
            round(B_wrt_A[1]),
            round(B_wrt_A[2]),
        ),
        "C": (
            round(C_wrt_A[0] * math.cos(math.radians(t1))),
            round(C_wrt_A[0] * math.sin(math.radians(t1))),
            round(C_wrt_A[2]),
            )
        }