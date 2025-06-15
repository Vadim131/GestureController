#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 19:06:51 2025

@author: archuser
"""

""" This params is used for set size of camera frame and application. 
Must be more, than 300x300 for correct work"""
FRAME_W = 700
FRAME_H = 600

""" This value """
FREQ_OF_WORK = 15 

""" This img will be used if there is no signal from camera """
NOSIGNAL_IMG_PATH = "nosignal.jpg"

""" This is param from mediapipe, choce model complexity 0 or 1 (0 in enough in most aims) """
MP_MODEL_COMPLEXITY = 0

""" This is used to choce how much arms do you need from 1 to x.
    If you chose 1 hand, "shift" would not be possible to use
    WARNING! I haven't tested more than 2 hands!  """
MAX_NUM_HANDS = 2

""" This is index of camera which will be used to capture an image of hands """
CAMERA_INDEX = 0

if __name__ == "__main__":
    docstr = """This is config module, there you can change variables 
in your own, to set programm preferences\n@autor: Vadim Davilin"""
    print(docstr)