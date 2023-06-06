import numpy as np
from time import sleep
import sys, os

def euclidian_dist(point_1, point_2):
    """
    Retruns the euclidian distance between 2 points 2D
        Args : 
            point_1 : a tuple with 2 rows with point 1 position
            point_2 : a tuple with 2 rows with point 2 position
        Ret :
            Distance : int euclidian distance between those 2 points
    """
    return np.sqrt((point_1[0]-point_2[0])**2+(point_1[1]-point_2[1])**2)

def detect_pose_main(keypoints):
    """
    Returns the number of hands up for a person looking at the camera
        Args : 
            keypoints : OpenPose data received for 1 person only
        Ret :
            Number of hands up : str
    """
    neck_x,neck_y       = keypoints[1,:2]
    relbow_x, relbow_y  = keypoints[3,:2]
    rhand_x,rhand_y     = keypoints[4,:2]
    lelbow_x, lelbow_y  = keypoints[3,:2]
    lhand_x,lhand_y     = keypoints[7,:2]
    if():
        return "2 mains en l'air"
    elif():
        return "Une main en l'air"
    else:
        return "0 mains en l'air"
    
def detect_pose_pied(keypoints):
    rknee_x, rknee_y = keypoints[10,:2]
    lknee_x, lknee_y = keypoints[13,:2]
    lheel_x, lheel_y = keypoints[21,:2]
    rheel_x, rheel_y = keypoints[24,:2]
    if(rknee_x < lknee_x and rheel_x > lheel_x): # Detection en comparant les positions des genoux et des pieds
        return "Jambes croisees"
    elif(euclidian_dist((rheel_x, rheel_y),(lheel_x, lheel_y)) > 2*euclidian_dist((rknee_x, rknee_y),(lknee_x, lknee_y))) :
        return "Jambes ecartees"
    else :
        return "Jabmes droites"

def detect_pose_zone(keypoints):
    lheel_x, lheel_y = keypoints[21,:2]
    rheel_x, rheel_y = keypoints[24,:2]
    if(lheel_y>500 or rheel_y>350):
        return "zone valide"
    else:
        return "zone non valide"