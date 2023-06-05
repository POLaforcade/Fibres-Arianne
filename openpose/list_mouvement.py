import numpy as np
from time import sleep
import sys, os

def detect_pose_main(poseKeypoints):
    for keypoints in poseKeypoints:
        neck_x,neck_y       = keypoints[1,:2]
        relbow_x, relbow_y  = keypoints[3,:2]
        rhand_x,rhand_y     = keypoints[4,:2]
        lelbow_x, lelbow_y  = keypoints[3,:2]
        lhand_x,lhand_y     = keypoints[7,:2]
        if(rhand_y < relbow_y and lhand_y < lelbow_y):
            return "Une main en l'air"
        elif():
            return "2 mains en l'air"
        else:
            return "0 mains en l'air"
    