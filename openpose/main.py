import numpy as np
from time import sleep
import sys,os
import list_mouvement
import config
from person import person

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
list_person = np.empty([100, 5], dtype='person')

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
        list_person = np.empty(100, dtype=person)
        datum.cvInputData = frame
        opWrapper.emplaceAndPop([datum])

        poseKeypoints = datum.poseKeypoints

        if poseKeypoints.size > 1:
            for keypoints in poseKeypoints:
                pers = person.detect_pose_last(keypoints, list_person, list_person_last)
                neck_x, neck_y = keypoints[0,:2]
                neck_x = int(neck_x)
                neck_y = int(neck_y)
                bary_x, bary_y = pers.barycenter().get_value()
                bary_x = int(bary_x)
                bary_y = int(bary_y)
                frame = cv2.circle(frame, (bary_x, bary_y), 10, (0, 0, 255), -1)
                frame = cv2.circle(frame, (bary_x, bary_y), config.TRACKING_RADIUS, (0, 0, 255), 2)
                frame = cv2.putText(frame,  str(pers.id), (neck_x, neck_y), cv2.FONT_HERSHEY_PLAIN, config.FONT_SIZE, config.TEXT_COLOR, config.FONT_THICKNESS)

        list_person_last = list_person

    if use_open_pose:
        cv2.imshow("output data", frame)
        cv2.imshow("OpenPose test", datum.cvOutputData)
    else:
        cv2.imshow("OpenPose test", frame)

    key = cv2.waitKey(fps_wait) & 0xFF
    if key == 27 or key == ord('q'):
        break

cv2.destroyAllWindows()