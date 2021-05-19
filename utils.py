import cv2
from scipy.spatial import distance

def enchance_image(frame) :
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    wb = cv2.xphoto.createSimpleWB()
    wb.setP(0.3)
    temp_img = frame
    img_wb = wb.balanceWhite(temp_img)
    img_lab = cv2.cvtColor(img_wb, cv2.COLOR_BGR2Lab)
    l, a, b = cv2.split(img_lab)
    img_l = clahe.apply(l)
    img_clahe = cv2.merge((img_l, a, b))
    return cv2.cvtColor(img_clahe, cv2.COLOR_Lab2BGR)

def eye_aspect_ratio(eye) :
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])

    ear = (A+B) / (2*C)
    return ear