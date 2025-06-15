#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is project created in aims of controlling and running 
computer & etc devices with hands motion

@author: Vadim Davilin
@lisence GPL-V3
"""

#### ATTENTION!
FILENAME = "main.py"
FUNCTION = "understand gestures and controll computer"
AUTORNAME = "Vadim Davilin"

import pyautogui 
import numpy as np

#### struct 
GestureTypes = ('f',
                'd')

GestureHandlers = {
    }

class Gesture():
    pass

class ComputerController():
    def __init__(self):
        pass
    def control_with_gesture(self, gesture:Gesture):
        pass

class GestureDetector():
    def __init__(self):
        pass
    def detect_gesture(self, landmarks_pos) -> Gesture:

        print(np.linalg.norm(landmarks_pos[0][4] - landmarks_pos[0][8]))
       # print()
