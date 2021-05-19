from utils import *
from skimage.exposure import is_low_contrast
from imutils import face_utils
import numpy as np
import argparse
import pygame
import time
import dlib
import cv2

pygame.mixer.init()
pygame.mixer.music.load('audio/alert.wav')

EAR_THREASH_HOLD = 0.3
EAR_FRAME_PIPLINE = 50
DIVERSION_FRAME_TRESHHOLD = 50
EYE_DIVERSION_COUNTER = 0
DIVERSION_COUNTER = 0
ALERTING = False

face_cascade = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_default.xml")

ap = argparse.ArgumentParser()
ap.add_argument("-t", "--thresh", type=float, default=0.45,
	help="threshold for low contrast")
args = vars(ap.parse_args())

shape_predictor = "model/shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(shape_predictor)

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']

video_capture = cv2.VideoCapture(0)
time.sleep(2)

while(True):
    ret, frame = video_capture.read()
    frame = cv2.flip(frame,1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    text = "Image Enhancer : Disabled"
    color = (0, 255, 0)

    if is_low_contrast(gray, fraction_threshold=args["thresh"]):
        frame = enchance_image(frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        text = "Image Enhancer : Enabled"
        color = (0, 0, 255)

    cv2.putText(frame, text, (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    faces = detector(gray, 0)
    face_rectangle = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x,y,w,h) in face_rectangle:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)

    for face in faces:
        shape = predictor(gray, face)
        shape = face_utils.shape_to_np(shape)
        
        if (len(face_rectangle) == 0) :
            DIVERSION_COUNTER += 1
            if DIVERSION_COUNTER > DIVERSION_FRAME_TRESHHOLD :
                if not ALERTING :
                    pygame.mixer.music.play(-1)
                    ALERTING = True
                cv2.putText(frame, "Stay focus on road traveller", (10,400), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 2)
            else :
                pygame.mixer.music.stop()
                DIVERSION_COUNTER = 0
                ALERTING = False

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]

        leftEyeAspectRatio = eye_aspect_ratio(leftEye)
        rightEyeAspectRatio = eye_aspect_ratio(rightEye)
        eyeAspectRatio = (leftEyeAspectRatio + rightEyeAspectRatio) / 2

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        if(eyeAspectRatio < EAR_THREASH_HOLD):
            EYE_DIVERSION_COUNTER += 1
            if EYE_DIVERSION_COUNTER >= EAR_FRAME_PIPLINE:
                if not ALERTING :
                    pygame.mixer.music.play(-1)
                    ALERTING = True
                cv2.putText(frame, "You are Drowsy", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 2)
        else:
            pygame.mixer.music.stop()
            EYE_DIVERSION_COUNTER = 0
            ALERTING = False

    cv2.imshow('Video', frame)
    if(cv2.waitKey(1) & 0xFF == ord('q')):
        break

video_capture.release()
cv2.destroyAllWindows()
