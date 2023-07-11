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
            for i in range (26):
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
        if(type(self.tab) != np.ndarray):
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

        # Count for each iteration a person appears or disappears
        self.is_tracked = 0
        self.is_lost = 0

        # Creates an empty table for saving person pose
        self.history = np.empty(0)

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
    
    def get_idx_last(keypoints, list_person) -> int:
        """
        Functions that determines if a person is in a list of person depending on the barycenter position
        Args : 
            keypoints : np.ndarray, openpose data output
            list_person : np.ndarray, the list of person
        Ret :
            idx_last : int, index of the person in list_person_last or -1 if None is found
        """
        card = 0.
        rshoulder_x, rshoulder_y    = keypoints[2,:2]
        lshoulder_x, lshoulder_y    = keypoints[5,:2]
        rhip_x, rhip_y              = keypoints[9,:2]
        lhip_x, lhip_y              = keypoints[12,:2]
        if(rshoulder_x != None  and rshoulder_y != None):
            card += 1
        if(lshoulder_x != None  and lshoulder_y != None):
            card += 1
        if(rhip_x != None  and rhip_y != None):
            card += 1
        if(lhip_x != None  and lhip_y != None):
            card += 1
        c = point2D((rshoulder_x+lshoulder_x+rhip_x+lhip_x)/card, (rshoulder_y+lshoulder_y+rhip_y+lhip_y)/card)
        for i, person_last in enumerate(list_person) :
            if(person_last != None):
                dist = point2D.get_dist(c, person_last.barycenter())
                if (dist < TRACKING_RADIUS):
                    return i
        return -1
    
    def get_idx_last_pred(keypoints, list_person) -> int:
        """
        Functions that determines if a person is in a list of person depending on the barycenter position 
        on the previous frames
        Args : 
            keypoints : np.ndarray, openpose data output
            list_person : np.ndarray, the list of person
        Ret :
            idx_last : int, index of the person in list_person_last or -1 if None is found
        """
        p = get_barycenter_from_keypoints(keypoints)
        for i, person in enumerate(list_person):
            # Verifies if the person already exists
            if person == None :
                continue
            dist = point2D.get_dist(p, person.next_pose())
            if (dist < TRACKING_RADIUS): # If a person is found, return the index
                return i
        return -1

    def next_pose(self): 
        if (self.is_lost == 0): # Si la personne n'est pas perdue, on s'attend à se qu'elle soit autour de sa zone précédente
            return self.barycenter()
        else : # Si la personne est perdue, on projette pour essayer de la retrouver
            if(self.history.shape[0] < 4):
                b = self.get_barycenter_from_history(self.history.shape[0])
                x, y = b.get_value()
                x0, y0 = self.barycenter().get_value()
                return point2D(x + (np.abs(x - x0)/self.history.shape[0])*self.is_lost, y + (np.abs(y - y0)/self.history.shape[0])*self.is_lost)
            else:
                b = self.get_barycenter_from_history(4)
                x, y = b.get_value()
                x0, y0 = self.barycenter()
                return point2D(x + (np.abs(x - x0)/4)*self.is_lost, y + (np.abs(y - y0)/4)*self.is_lost)

    def get_barycenter_from_history(self, index : int) -> 'point2D':
        x0, y0 = self.history[index-1][2].get_value()
        x1, y1 = self.history[index-1][5].get_value()
        x2, y2 = self.history[index-1][9].get_value()
        x3, y3 = self.history[index-1][12].get_value()
        card = 4
        if(x0 == 0 and y0 == 0):
            card -= 1
        if(x1 == 0 and y1 == 0):
            card -= 1
        if(x2 == 0 and y2 == 0):
            card -= 1
        if(x3 == 0 and y3 == 0):
            card -= 1
        res_x = (x0 + x1 + x2 + x3)/card
        res_y = (y0 + y1 + y2 + y3)/card
        return point2D(res_x, res_y)

    def tracking(keypoints : np.ndarray, list_person : np.ndarray) -> 'person':
        """
        Function that update list_person with new openpose sample
        Args :
            keypoints : np.ndarray, openpose output data
            list_person : np.ndarray, list of person to be updated
        Ret : 
            person : 'person', new person or person with updated pose
        """
        idx = person.get_idx_last(keypoints, list_person)
        if(idx == -1) : # the person doesnt exist
            list_person[person.nb_person-1] = person(keypoints)
            return list_person[person.nb_person-1]
        else: # the person already exists
            list_person[idx].update_from_array(keypoints)
            return list_person[idx]
        
    def tracking_pred(keypoints : np.ndarray, list_person : np.ndarray) -> 'person':
        """
        Function that update list_person with new openpose sample with prediction of future movements
        Args :
            keypoints : np.ndarray, openpose output data
            list_person : np.ndarray, list of person to be updated
        Ret : 
            person : 'person', new person or person with updated pose
        """
        idx = person.get_idx_last_pred(keypoints, list_person)
        if(idx == -1) : # the person doesnt exist
            list_person[person.nb_person-1] = person(keypoints)
            return list_person[person.nb_person-1]
        else: # the person already exists
            list_person[idx].update_from_array(keypoints)
            return list_person[idx]
        
    def update(self) -> 'person':
        """
        Function that updates a person history
        """
        if((self.history.size == 0)): # The person has no history
            self.history = np.array([self.tab])

        elif((self.tab == self.history[0]).all()): # The person wasn't found
            # Si on veut garder la valeur dans l'historique meme lorsque la personne n'est pas détéctée, décommenter cette ligne 
            # self.history = np.vstack((self.history[0], self.history))
            self.is_lost += 1

        else : # The person was found
            # Add the person's skeleton to it's history
            self.history = np.vstack((self.tab, self.history))
            self.is_tracked += 1
            self.is_lost = 0

            
def get_nb_person() -> None:
    """
    Get the number of person on a frame
    """
    return person.nb_person

def clear_first_column(tab : np.ndarray):
    """
    Create an empty column at the beginnign of an array to save new openpose data
    Args : 
        tab : np.ndarray, the table we want to add a new column in
    """
    for i in range (config.NB_PERSON_MAX):
        tab[i] = np.append(None, tab[i,:4])

def Show_list_person(frame, list_person):
    for i in range (config.NB_PERSON_MAX):
        x, y = list_person[i].tab[0].get_value()
        x, y = int(x), int(y)
        # Affichage des différents paramètres
        frame = cv2.addText(frame, str(list_person[i].is_tracked), (x, y), cv2.FONT_HERSHEY_PLAIN, config.FONT_SIZE, config.TEXT_COLOR, config.FONT_THICKNESS)
    return frame

def get_barycenter_from_keypoints(keypoints : np.ndarray) -> 'point2D':
        """
        Calculate the position of a barycenter with openpose data output
        Args :
            keypoints : np.ndarray, openpose data output for a person
        Ret : 
            Barycenter : point2D : the barycenter of the person
        """
        card = 0.
        rshoulder_x, rshoulder_y    = keypoints[2,:2]
        lshoulder_x, lshoulder_y    = keypoints[5,:2]
        rhip_x, rhip_y              = keypoints[9,:2]
        lhip_x, lhip_y              = keypoints[12,:2]
        if(rshoulder_x != None  and rshoulder_y != None):
            card += 1
        if(lshoulder_x != None  and lshoulder_y != None):
            card += 1
        if(rhip_x != None  and rhip_y != None):
            card += 1
        if(lhip_x != None  and lhip_y != None):
            card += 1
        return point2D((rshoulder_x+lshoulder_x+rhip_x+lhip_x)/card, (rshoulder_y+lshoulder_y+rhip_y+lhip_y)/card)