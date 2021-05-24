from utils import *
from skimage.exposure import is_low_contrast
from imutils import face_utils
import numpy as np
import argparse
import pygame
import time
import dlib
import cv2
import os

face_cascade=cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_default.xml")
ds_factor= 0.7
shape_predictor = "model/shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(shape_predictor)

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']

pygame.mixer.init()
pygame.mixer.music.load('audio/alert.wav')

class VideoCamera(object):
    
    def __init__(self) :
        self.video = cv2.VideoCapture(0)
        self.LOW_CONTRAST_THRESH = 0
        self.EAR_THREASH_HOLD = 0.3
        self.EAR_FRAME_PIPLINE = 50
        self.DIVERSION_FRAME_TRESHHOLD = 50
        self.EYE_DIVERSION_COUNTER = 0
        self.DIVERSION_COUNTER = 0
        self.ALERTING = False
        self.REST_ALERT_THRESH = 0
        self.REST_ALERT_FRAME_THRESH = 0
        self.ALERT_COUNTER = 0
        self.FRAME_COUNTER = 0
        self.message = ''
    
    def __del__(self) :
        self.video.release()

    def get_frame(self) :
            ret, frame = self.video.read()
            # print(frame)
           
            if frame is not None :

                frame=cv2.resize(frame,None,fx=ds_factor,fy=ds_factor,interpolation=cv2.INTER_AREA)                 

                frame = cv2.flip(frame,1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                text = "Image Enhancer : Disabled"
                color = (0, 255, 0)

                if is_low_contrast(gray, fraction_threshold = self.LOW_CONTRAST_THRESH) :
                    frame = enchance_image(frame)
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    text = "Image Enhancer : Enabled"
                    color = (0, 0, 255)

                cv2.putText(frame, text, (10, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.putText(frame, f'Blink Counter : {str(self.ALERT_COUNTER)}', (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0 , 0 , 255), 2)
                faces = detector(gray, 0)
                face_rectangle = face_cascade.detectMultiScale(gray, 1.3, 5)

                for (x,y,w,h) in face_rectangle:
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

                for face in faces:
                    shape = predictor(gray, face)
                    shape = face_utils.shape_to_np(shape)
                    
                    if (len(face_rectangle) == 0) :
                        self.DIVERSION_COUNTER += 1
                        if self.DIVERSION_COUNTER > self.DIVERSION_FRAME_TRESHHOLD :
                            if not self.ALERTING :
                                pygame.mixer.music.play(-1)
                                self.ALERTING = True

                            self.message = "Stay focus on road traveller"
                            cv2.putText(frame, self.message, (10,200), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
                        else :
                            pygame.mixer.music.stop()
                            self.DIVERSION_COUNTER = 0
                            self.ALERTING = False

                    leftEye = shape[lStart:lEnd]
                    rightEye = shape[rStart:rEnd]

                    leftEyeAspectRatio = eye_aspect_ratio(leftEye)
                    rightEyeAspectRatio = eye_aspect_ratio(rightEye)
                    eyeAspectRatio = (leftEyeAspectRatio + rightEyeAspectRatio) / 2

                    leftEyeHull = cv2.convexHull(leftEye)
                    rightEyeHull = cv2.convexHull(rightEye)
                    cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                    cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

                    if(eyeAspectRatio < self.EAR_THREASH_HOLD):
                        self.EYE_DIVERSION_COUNTER += 1
                        if self.EYE_DIVERSION_COUNTER >= self.EAR_FRAME_PIPLINE:
                            if not self.ALERTING :
                                pygame.mixer.music.play(-1)
                                self.ALERTING = True
                            self.message = "You Are Drowsy"
                            cv2.putText(frame, self.message, (10,20), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 2)
                            
                    else:
                        if self.EYE_DIVERSION_COUNTER >= self.EAR_FRAME_PIPLINE :
                            self.ALERT_COUNTER += 1
                        if self.ALERT_COUNTER >= self.REST_ALERT_THRESH :
                            if self.FRAME_COUNTER < (self.REST_ALERT_FRAME_THRESH) :
                                if not self.ALERTING :
                                    pygame.mixer.music.play(-1)
                                    self.ALERTING = True
                                self.FRAME_COUNTER += 1
                                
                                self.message ="You should take Rest"
                                cv2.putText(frame, self.message, (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 2)
                            else :
                                self.ALERT_COUNTER = 0
                                self.FRAME_COUNTER = 0
                                pygame.mixer.music.stop()
                                EYE_DIVERSION_COUNTER = 0
                                ALERTING = False
                        else :
                            pygame.mixer.music.stop()
                            self.EYE_DIVERSION_COUNTER = 0
                            ALERTING = False
                        pygame.mixer.music.stop()
                        self.EYE_DIVERSION_COUNTER = 0
                        self.ALERTING = False

                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                face_rects=face_cascade.detectMultiScale(gray,1.3,5)
                for (x,y,w,h) in face_rects:
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                    break
                # encode OpenCV raw frame to jpg and displaying it
                ret, jpeg = cv2.imencode('.jpg', frame)
                return jpeg.tobytes() , self.message
            else : 
                return None