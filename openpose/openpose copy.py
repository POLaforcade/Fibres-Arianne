import numpy as np
from time import sleep
import sys,os
import list_mouvement

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

cap = cv2.VideoCapture("Recording_Les_Fibres_d_Arianne/Videos_20230511_140210/20230511_140210_Kinect_8.mkv")

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
        mains = list_mouvement.detect_pose_main(poseKeypoints)
        cv2.putText(datum.cvOutputData, mains)

    if use_open_pose:
        cv2.imshow("OpenPose test", datum.cvOutputData)
    else:
        cv2.imshow("OpenPose test", frame)

    key = cv2.waitKey(fps_wait) & 0xFF
    if key == 27 or key == ord('q'):
        break

cv2.destroyAllWindows()
