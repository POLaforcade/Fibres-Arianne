import numpy as np
from time import sleep
import sys, os

def euclidian_dist(point1, point2) -> float:
    """
    Returns the euclidian distance between 2 points 2D
        Args : 
            point_1 : a tuple with 2 rows with point 1 position
            point_2 : a tuple with 2 rows with point 2 position
        Ret :
            Distance : int euclidian distance between those 2 points
    """
    return np.sqrt((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)

def calculate_angle(point1, point2, point3) -> float:
    """
    Returns the angle between 3 points in a RGB image
        Args : 
            point1 : a tuple with 2 rows with point 1 position
            point2 : the middle point, a tuple with 2 rows with point 2 position
            point3 : a tuple with 2 rows with point 3 position
        Ret :
            angle_degree : float angle in degree
    """
    v1 = np.array(point1) - np.array(point2)
    v2 = np.array(point3) - np.array(point2)
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    angle = np.arccos(dot_product / (norm_v1 * norm_v2))
    angle_degrees = np.degrees(angle)
    return angle_degrees

def check_angle_threshold(point1, point2, point3, threshold) -> bool:
    """
    Determines if an angle is above a threshold in degree
        Args :
            point1 : a tuple with 2 rows with point 1 position
            point2 : the middle point, a tuple with 2 rows with point 2 position
            point3 : a tuple with 2 rows with point 3 position
            threshold : a tuple with the angle interval value we want to test
        Ret :
            bool value : true if the angle is within the interval.
    """
    angle = calculate_angle(point1, point2, point3)
    return threshold[0] <= angle <= threshold[1]

def detect_pose_main(keypoints) -> str:
    """
    Returns the number of hands up for a person looking at the camera
        Args : 
            keypoints : OpenPose data received for 1 person only
        Ret :
            Number of hands up : str
    """
    rshoulder_x, rshoulder_y    = keypoints[2,:2]
    relbow_x, relbow_y          = keypoints[3,:2]
    rhand_x,rhand_y             = keypoints[4,:2]
    lshoulder_x, lshoulder_y    = keypoints[5,:2]
    lelbow_x, lelbow_y          = keypoints[6,:2]
    lhand_x,lhand_y             = keypoints[7,:2]
    rthreshold                   = (235, 325)
    lthreshold                   = (35, 145)
    if(check_angle_threshold((rshoulder_x, rshoulder_y), (relbow_x, relbow_y), (rhand_x,rhand_y), rthreshold) and \
       check_angle_threshold((lshoulder_x, lshoulder_y), (lelbow_x, lelbow_y), (lhand_x,lhand_y), lthreshold)):
        return "2 mains en l'air"
    elif(check_angle_threshold((rshoulder_x, rshoulder_y), (relbow_x, relbow_y), (rhand_x,rhand_y), rthreshold)):
        return "Main droite en l'air"
    elif(check_angle_threshold((lshoulder_x, lshoulder_y), (lelbow_x, lelbow_y), (lhand_x,lhand_y), lthreshold)):
        return "Main gauche en l'air"
    else:
        return "0 mains en l'air"
    
def detect_pose_pied(keypoints) -> str:
    """
    Returns the position of the legs for a person looking at the camera
        Args : 
            keypoints : OpenPose data received for 1 person only
        Ret :
            Position of the feet : str
    """
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
    
def detect_pose_epaule(keypoints) -> str :
    """
    Returns the position of the shoulders for a person
        Args : 
            keypoints : OpenPose data received for 1 person only
        Ret :
            Position of the shoulders : str
    """
    neck_x, neck_y              = keypoints[1,:2]
    rshoulder_x, rshoulder_y    = keypoints[2,:2]
    lshoulder_x, lshoulder_y    = keypoints[5,:2]
    if():
        return "De face"
    elif():
        return "De profil droit"
    elif():
        return "De profil gauche"
    else:
        return "De dos"

def detect_pose_zone(keypoints) -> str:
    """
    Returns a string that tells us if a person is in a zone or not.
        Args : 
            keypoints : OpenPose data received for 1 person only
        Ret :
            Position of the person : str
    """
    lheel_x, lheel_y = keypoints[21,:2]
    rheel_x, rheel_y = keypoints[24,:2]
    if(lheel_y>500 or rheel_y>350):
        return "zone valide"
    else:
        return "zone non valide"
    
def detect_interaction(keypoints):
    """
    Returns a string that tells us if we can considerate a person interacts with the installation
        Args :
            keypoints : OpenPose data received for 1 person only
        Ret :
            Person interaction : str
    """
    main = detect_pose_main(keypoints)
    pied = detect_pose_pied(keypoints)
    zone = detect_pose_zone(keypoints)
    if(True):
        return "Interaction"
    else:
        return "Pas d'interaction"