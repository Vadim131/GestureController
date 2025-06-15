#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Created on Tue Apr 15 17:47:45 2025

"""
This is project created in aims of controlling and running 
computer & etc devices with hands motion

@author: Vadim Davilin
@lisence GPL-V3
"""

# ATTENTION!
import config as conf
from gesture_handling import GestureDetector, ComputerController
from sys import exit, argv
import time
import mediapipe.python.solutions.drawing_styles as mp_drawing_styles
import mediapipe.python.solutions.drawing_utils as mp_drawing
import mediapipe.python.solutions.hands as mp_hands
import numpy as np
import cv2
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, \
 QGraphicsPixmapItem, QApplication, QMainWindow
from PyQt6.QtCore import QObject, QThread, pyqtSignal, Qt

FILENAME = "main.py"
FUNCTION = "core of project"
AUTORNAME = "Vadim Davilin"

# TODO: Сделать нормальный конфиг
# from gui import Gui


class HandsDetector():
    def __init__(self, complexity, max_hands, static_mode=False,
                 detection_con=0.5, track_con=0.5):

        self.Hands = mp_hands.Hands(
            static_image_mode=static_mode,
            model_complexity=complexity,
            max_num_hands=max_hands,
            min_tracking_confidence=track_con,
            min_detection_confidence=detection_con)

        self.detected_hands = 0

    def detect_hands(self, img: np.ndarray):
        self.detected_hands = self.Hands.process(img)

    def draw_landmarks(self, img: np.ndarray):
        """ Draws circles on frame to show detected landmarks """
        if 0 == self.detected_hands:
            print("Error! Process hands firstly!")

        if img.flags.writeable:
            if self.detected_hands.multi_hand_landmarks:
                for hand_landmarks in self.detected_hands.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        img,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style(),
                    )
        else:
            print("Error! Img is not writiable!")

    def get_landmarks_xy_pos(self, hand_num=0) -> np.array:
        """ Retuns np.array 20x2 with x,y coordinates mediapipe discovered"""

        if self.detected_hands.multi_hand_landmarks and \
                len(self.detected_hands.multi_hand_landmarks) > hand_num:
            xy_pos = np.zeros((21, 2))
            hand = self.detected_hands.multi_hand_landmarks[hand_num]

            # get the landmark pos in mediapipe coordinates
            for i, lm in enumerate(hand.landmark):
                # mediapipe gives us 8 signs after comma. We don't need so much
                xy_pos[i][0] = np.round(lm.x*1000)
                xy_pos[i][1] = np.round(lm.y*1000)
            return xy_pos
        # else
        return None


class Core(QObject):
    frame_to_show = pyqtSignal(object)  # send frame data

    def __init__(self):
        """ This inits core items of project. Core thread manages mediapipe, 
        opencv and gesture handling modules """
        super().__init__()

        # Core params
        self.camera_index = conf.CAMERA_INDEX

        """ This img will be used if there is no signal from camera """
        self.nosignal_path = conf.NOSIGNAL_IMG_PATH

        """ This is param from mediapipe, choce model complexity 0 or 1 
        (0 in enough in most aims) """
        self.model_complexity = conf.MP_MODEL_COMPLEXITY

        self.max_num_hands = conf.MAX_NUM_HANDS

        """ This params is used for set size of camera frame and application. 
        Must be more, than 300x300 for correct work"""
        self.frame_w = 700
        self.frame_h = 500

        self.params_names = ("camera_index",
                             "nosignal_path",
                             "model_complexity",
                             "max_num_hands",
                             "frame_w",
                             "frame_h"
                             )

        # Core objects
        self.HandsDetector = HandsDetector(
            self.model_complexity, self.max_num_hands, track_con=0.5)
        self.GestureDetector = GestureDetector()
        self.Controller = ComputerController()

        self.Cap = cv2.VideoCapture(0)
        self.Cap.set(3, self.frame_w)
        self.Cap.set(4, self.frame_h)

        self.running = False

    def set_param(self, param, value):
        if param not in self.params_names:
            print("Error! Core don't have such param")
            return

    def run(self):
        self.running = True

        nosignal = cv2.imread(self.nosignal_path)
        time0 = 0
        time1 = 0

        while self.running:
            landmarks_xy_arr = [None]*self.max_num_hands

            success, frame = self.Cap.read()

            if success:

                frame = cv2.flip(frame, 1)

                # for optimization we do frame non-writeable
                frame.flags.writeable = False
                self.HandsDetector.detect_hands(frame)

                frame.flags.writeable = True
                self.HandsDetector.draw_landmarks(frame)

                for i in range(self.max_num_hands):
                    landmarks_xy_arr[i] = self.HandsDetector.get_landmarks_xy_pos(i)
                # print(landmarks_xy_arr, "\n")

                time1 = time.time()
                instant_fps = 1 / (time1 - time0)
                time0 = time1

                cv2.putText(frame, str(int(instant_fps)), (10, 70), 
                            cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
                # time.sleep(0.05)

            else:
                frame = nosignal
                # to prevent to many pyqt signals and cpu overload
                time.sleep(0.1)

            # make singnal for gui to show frame
            self.frame_to_show.emit(frame)
            if (np.all(landmarks_xy_arr[0])):
                gesture = self.GestureDetector.detect_gesture(landmarks_xy_arr)
                self.Controller.control_with_gesture(gesture)

        self.Cap.release()

    def stop(self):
        self.running = False


class App(QMainWindow):
    def __init__(self):
        """ Creates thread for core (mdpipe & cv2). It's own thread runs gui"""
        super().__init__()

        # This is for core
        self.Thread = QThread()
        self.Core = Core()
        self.Core.moveToThread(self.Thread)
        self.Core.frame_to_show.connect(self.processFrame)
        self.Thread.started.connect(self.Core.run)
        self.Thread.start()

        # This is gui
        self.graphicsView = QGraphicsView()
        self.graphicsView.show()
        self.graphicsView.setGeometry(50, 50, 700, 500)

        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        self.scenePixmapItem = None

    def processFrame(self, frame):
        # Convert the frame to a format that Qt can use
        image = QImage(
            frame.data,
            frame.shape[1],
            frame.shape[0],
            QImage.Format.Format_BGR888,
        )
        pixmap = QPixmap.fromImage(image)

        if self.scenePixmapItem is None:
            self.scenePixmapItem = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.scenePixmapItem)
            self.scenePixmapItem.setZValue(0)
            self.fitInView(self.scene.sceneRect(),
                           Qt.AspectRatioMode.KeepAspectRatio)
        else:
            self.scenePixmapItem.setPixmap(pixmap)

    def stop_and_exit(self):
        self.Core.stop()
        self.Thread.quit()
        self.Thread.wait()

    def fitInView(self, rect, aspectRatioMode):
        self.graphicsView.fitInView(rect, aspectRatioMode)


def assert_config():
    pass


if __name__ == "__main__":
    app = QApplication(argv)
    main = App()
    app.exec()
    # after closing
    main.stop_and_exit()
