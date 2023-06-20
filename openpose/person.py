"""
Created on Mon 12 2023
@author : Laforcade
"""
import numpy as np
import config
import random
import cv2

# TRACKING_RADIUS can be modified in config file
TRACKING_RADIUS = config.TRACKING_RADIUS

class point2D:
    """
    Class for a 2D point that is part of a person skeleton
    """
    def __init__(self, x = 0, y = 0) -> None:
        """
        Class constructor from x and y values
        Args :
            x, y : float
        """
        self.x = x
        self.y = y

    @classmethod
    def from_array(cls, array) -> None:
        """
        Class constructor with vector
        Args :
            array : 2D vector with the point coordinates
        """
        return cls(array[0], array[1])

    def set_from_array(self, keypoint: np.ndarray) -> None:
        """
        Set point coordinates from an array
        Args : 
            keypoint : np.ndarray, the 2d vector with values
        """
        self.x = keypoint[0]
        self.y = keypoint[1]

    def set_from_value(self, x, y) -> None:
        """
        Set points coordinates from x and y values
        Args :
            x, y : float, the new coordinates of the point
        """
        self.x = x
        self.y = y

    def get_value(self) -> None:
        """
        Const : Getter for the point coordinates
        Ret :
            x, y : int, the coordinates of the point
        """
        return self.x, self.y
    
    def get_array(self) -> None:
        """
        Const : Getter for the point coordinates as a vector
        Ret :
            vector : np.array, the point vector
        """
        return np.array([self.x, self.y])
    
    def Show(self) -> None:
        """
        Const : Shows a point coordinates
        """
        if(self.x == 0 and self.y == 0):
            print("Pas d'infos sur le point")
        else :
            print(self.x,";",self.y)

    def get_dist(p1 : 'point2D', p2 : 'point2D') -> float:
        """
        Const : Return the euclidian distance between 2D points
        Args :
            p1, p2 : 'point2D', points
        Ret :
            dist = int, euclidian distance between p1 and p2
        """
        return np.sqrt((p1.x - p2.x)**2+(p1.y - p2.y)**2)

class skeleton:
    """
    Class skeleton that encapsulates the output of openpose processing
    """
    # table with all the keypoints name and sorted as openpose output
    labels = (  "nose"              , "neck"            , "Right Shoulder"  , "Right Elbow"     , \
                "Right Wrist"       , "Left Shoulder"   , "Left Elbow"      , "Left Wrist"      , \
                "Middle Hip"        , "Right Hip"       , "Right Knee"      , "Right Ankle"     , \
                "Left Hip"          , "Left Knee"       , "Left Ankle"      , "Right Eye"       , \
                "Left Eye"          , "Right Ear"       , "Left Ear"        , "Left Big Toe"    , \
                "Left Small Toe"    , "Left Heel"       , "Right Big Toe"   , "Right Small Toe" , \
                "Right Heel"        , "Background")
    
    def __init__(self, keypoints = None) -> None:
        """
        Class constructor from openpose output data
        Args : 
            keypoints : np.array([26, 3]), table with coordinates of skeleton points
        """
        if(keypoints.all() != None) : 
            self.tab = np.empty(26, dtype=point2D)
            for i in range (25):
                self.tab[i] = point2D(keypoints[i][0], keypoints[i][1])

    def barycenter(self) -> 'point2D':
        """
        Const : Calculates the barycenter of a skeleton with points that we determined
        Ret :
            barycenter : 'point2D', barycenter 
        """
        rshoulder = point2D.get_array(self.tab[2])
        lshoulder = point2D.get_array(self.tab[5])
        rhip      = point2D.get_array(self.tab[9])
        lhip      = point2D.get_array(self.tab[12])
        card = 4
        if(rshoulder.all() == None):
            card -= 1
        if(lshoulder.all() == None):
            card -= 1
        if(rhip.all() == None):
            card -= 1
        if(lhip.all() == None):
            card -= 1
        res_x = (rshoulder[0] + lshoulder[0] + rhip[0] + lhip[0])/card
        res_y = (rshoulder[1] + lshoulder[1] + rhip[1] + lhip[1])/card
        return point2D(res_x, res_y)

    def update_from_array(self, keypoints) -> None:
        """
        Updates the person's position with new openpose dataset
        Args : 
            keypoints : openpose detection data
        """
        for i, keypoint in enumerate(keypoints):
            self.tab[i] = point2D.from_array(keypoint)

    def Show(self) -> None:
        """
        Const : dipslays all the kepoints of a person
        """
        if(self.tab == None):
            print("Error : Person initiated but not defined")
            return
        for label, keypoint in zip(skeleton.labels, self.tab):
            print(label, " : ", end='')
            if keypoint is None:
                print("Keypoint is NoneType")
            else :
                keypoint.Show()

class person(skeleton):
    """
    Class person to calculate and show all the informations on a person
    """
    # Static attribute that keep track of number of person we created
    nb_person = 0
    def __init__(self, keypoints =  None, time = 0.) -> None:
        """
        Class constructor from an openpose data on a skeleton
        Args :
            Keypoints : array, openpose data output on a single person
        """

        # Creates a skeleton for a person from keypoints
        skeleton.__init__(self, keypoints)

        # Add a person to the counter
        person.nb_person += 1 

        # Creates an random ID (should be updated so 2 persons cant have the same ID)
        self.id = random.randint(0, 100)

        # Set the starting time of a person
        self.start_time = time

    def __del__(self) -> None:
        """
        Class destructor
        """
        # Looses track of a person 
        person.nb_person -= 1

    def set_start_time(self, time : float) -> None:
        """
        Set the time when we detect a person for the first time
        Args :
            time : float, time of detection in seconds
        """
        self.start_time = time
   
    def get_time_from_start(self, time : float) -> float:
        """
        Returns the time a person spent in front of an installation
        Args :
            time : float, the moment we want to know how much time the person spent in front of the installation
        Ret : 
            snap_diff : time person spent in front of the installation in s
        """
        return time - self.start_time
    
    def get_time_with_reset(self, time : float) -> float:
        """
        Returns the time a person spent i front of the installation and reset the start time of a person
        Args : 
            time : float, the current time
        Ret : 
            snap_diff : time person spent in front of the installation in s
        """
        res = time - self.start_time
        self.set_start_time(time)
        return res
    
    def get_idx_last(keypoints, list_person_last) -> int:
        """
        Functions that determines whether or not a person was present on last frame
        Args : 
            keypoints : np.array, openpose data output
        Ret :
            idx_last : int, index of the person in list_person_last or -1 if None is found
        """
        rshoulder_x, rshoulder_y    = keypoints[2,:2]
        lshoulder_x, lshoulder_y    = keypoints[5,:2]
        rhip_x, rhip_y              = keypoints[9,:2]
        lhip_x, lhip_y              = keypoints[12,:2]
        c = point2D((rshoulder_x+lshoulder_x+rhip_x+lhip_x)/4.0, (rshoulder_y+lshoulder_y+rhip_y+lhip_y)/4.0)
        for i, person_last in enumerate(list_person_last) :
            if(person_last != None):
                dist = point2D.get_dist(c, person_last.barycenter())
                if (dist < TRACKING_RADIUS):
                    return i
        return -1
    
    def detect_pose_last(keypoints, list_person, list_person_last) -> 'person':
        """
        Function that update list_person for each person detect on the frame
        Args :
            keypoints : np.array, openpose output for one person
            list_person : np.array, list of person to be updated
            list_person_last : np.array, list of person detected on last frame
        Ret : 
            person : 'person', new person or person with updated pose
        """
        idx = person.get_idx_last(keypoints, list_person_last)
        if(idx == -1) : # the person doesnt exist
            list_person[person.nb_person-1] = person(keypoints)
            return list_person[person.nb_person-1]
        else: # the person already exists
            list_person[idx] = list_person_last[idx]
            list_person[idx].update_from_array(keypoints)
            return list_person[idx]
            

def get_nb_person() -> None:
    """
    Getter for the number of person on a frame
    """
    return person.nb_person
