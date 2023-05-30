import numpy as np
from time import sleep
import sys,os

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

    # if poseKeypoints.size > 1:
    #     for keypoints in poseKeypoints:
    #         # keypoint indices
    #         # face center : 0
    #         # neck : 1
    #         # right hand : 4
    #         # left hand : 7
    #         # hips center : 8
    #         # right eye : 15
    #         # left eye : 16
    #         # right ear : 17
    #         # left ear : 18
    #         face_x,face_y = keypoints[0,:2]
    #         neck_x,neck_y = keypoints[1,:2]
    #         rhand_x,rhand_y = keypoints[4,:2]
    #         lhand_x,lhand_y = keypoints[7,:2]
    #         hips_x,hips_y = keypoints[8,:2]
    #         reye_x,reye_y = keypoints[15,:2]
    #         leye_x,leye_y = keypoints[16,:2]
    #         rear_x,rear_y = keypoints[17,:2]
    #         lear_x,lear_y = keypoints[18,:2]
    #
    #         dright = np.sqrt((rhand_x-reye_x)**2 + (rhand_y-reye_y)**2)
    #         dleft = np.sqrt((lhand_x-leye_x)**2 + (lhand_y-leye_y)**2)
    #
    #         tol = 8
    #         between_ears = rear_x < min(reye_x,leye_x) and lear_x > max(reye_x,leye_x)
    #         if dleft < tol and dright < tol and between_ears:
    #             pass
    #
    #         cv2.circle(frame, (int(face_x),int(face_y)), 1, (255,0,0), thickness=-1, lineType=cv2.FILLED)
    #         cv2.circle(frame, (int(neck_x),int(neck_y)), 1, (0,255,0), thickness=-1, lineType=cv2.FILLED)
    #         cv2.circle(frame, (int(rhand_x),int(rhand_y)), 1, (0,0,255), thickness=-1, lineType=cv2.FILLED)
    #         cv2.circle(frame, (int(lhand_x),int(lhand_y)), 1, (255,255,0), thickness=-1, lineType=cv2.FILLED)
    #         cv2.circle(frame, (int(hips_x),int(hips_y)), 1, (0,255,255), thickness=-1, lineType=cv2.FILLED)

    if use_open_pose:
        cv2.imshow("OpenPose test", datum.cvOutputData)
    else:
        cv2.imshow("OpenPose test", frame)

    key = cv2.waitKey(fps_wait) & 0xFF
    if key == 27 or key == ord('q'):
        break

cv2.destroyAllWindows()
