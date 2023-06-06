import numpy as np
from time import sleep
import sys,os
import list_mouvement

MARGIN = 10  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 2
FONT_THICKNESS = 1
TEXT_COLOR = (255, 0, 0)  # blue

sys.path.append('F:/openpose/build/python/openpose/Release');
os.environ['PATH']  = os.environ['PATH'] + ';' + 'F:/openpose/build/x64/Release;' +  'F:/openpose/build/bin;'
import pyopenpose as op
import cv2

use_open_pose = True
fps_wait = 40

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

    if not success:
        sleep(0.02)
        continue

    if use_open_pose:
        datum.cvInputData = frame
        opWrapper.emplaceAndPop([datum])

        poseKeypoints = datum.poseKeypoints

        if poseKeypoints.size > 1:
            for keypoints in poseKeypoints:
                neck_x, neck_y      = keypoints[1,:2]
                neck_x, neck_y      = int(neck_x), int(neck_y)
                relbow_x, relbow_y  = keypoints[3,:2]
                relbow_x, relbow_y  = int(relbow_x), int(relbow_y)
                rhand_x, rhand_y    = keypoints[4,:2]
                rhand_x, rhand_y    = int(rhand_x), int(rhand_y)

                pose = list_mouvement.detect_pose_zone(keypoints)

                cv2.circle(frame, (neck_x, neck_y), 3, (0, 0, 255))
                cv2.circle(frame, (relbow_x, relbow_y), 3, (0, 0, 255))
                cv2.circle(frame, (rhand_x,rhand_y), 3, (0, 0, 255))
                cv2.putText(frame,  pose, (neck_x, neck_y), cv2.FONT_HERSHEY_PLAIN, FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

    if use_open_pose:
        cv2.imshow("output data", frame)
        cv2.imshow("OpenPose test", datum.cvOutputData)
    else:
        cv2.imshow("OpenPose test", frame)

    key = cv2.waitKey(fps_wait) & 0xFF
    if key == 27 or key == ord('q'):
        break

cv2.destroyAllWindows()