import numpy as np
from time import sleep
import sys,os
import list_mouvement
import config
from person import person
import person as pe

MARGIN = config.MARGIN
ROW_SIZE = config.ROW_SIZE
FONT_SIZE = config.FONT_SIZE
FONT_THICKNESS = config.FONT_THICKNESS
TEXT_COLOR = config.TEXT_COLOR
FPS = config.FPS

sys.path.append('F:/openpose/build/python/openpose/Release');
os.environ['PATH']  = os.environ['PATH'] + ';' + 'F:/openpose/build/x64/Release;' +  'F:/openpose/build/bin;'
import pyopenpose as op
import cv2

use_open_pose   = True
fps_wait        = 40
time_s          = 0
list_person = np.empty([config.NB_PERSON_MAX], dtype=person)

if use_open_pose:
    opWrapper = op.WrapperPython()
    opWrapper.configure(dict(model_folder="F:/openpose/models/"))
    opWrapper.start()
    datum = op.Datum()
    fps_wait = 10

cap = cv2.VideoCapture("Enregistrements\\Videos_20230602_115702\\20230602_115702_Kinect_8.mkv")

if not cap.isOpened():
    print("Erreur ouverture fichier video")

while cap.isOpened():
    success, frame = cap.read()
    time_s += 1/FPS

    if not success:
        sleep(0.02)
        continue

    if use_open_pose:
        datum.cvInputData = frame
        opWrapper.emplaceAndPop([datum])

        poseKeypoints = datum.poseKeypoints

        if poseKeypoints.size > 1:
            for keypoints in poseKeypoints:
                person.tracking_pred(keypoints, list_person)

        for Person in list_person:
            if Person == None:
                continue
            Person.update()


    frame = pe.Show_list_person(frame, list_person)
    frame = pe.Show_tracking_radius(frame, list_person)

    if use_open_pose:
        cv2.imshow("output data", frame)
        cv2.imshow("OpenPose test", datum.cvOutputData)
    else:
        cv2.imshow("OpenPose test", frame)

    key = cv2.waitKey(fps_wait) & 0xFF
    if key == 27 or key == ord('q'):
        break

cv2.destroyAllWindows()