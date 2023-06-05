import numpy as np
from time import sleep
import sys, os

def detect_pose_main(keypoints):
    neck_x,neck_y       = keypoints[1,:2]
    relbow_x, relbow_y  = keypoints[3,:2]
    rhand_x,rhand_y     = keypoints[4,:2]
    lelbow_x, lelbow_y  = keypoints[3,:2]
    lhand_x,lhand_y     = keypoints[7,:2]
    if(rhand_y < neck_y and lhand_y < neck_y): # Detection avec le cosinus de l'angle entre le coude et la main
        return "2 mains en l'air"
    elif(rhand_y < neck_y or lhand_y < neck_y):
        return "Une main en l'air"
    else:
        return "0 mains en l'air"