import numpy as np
import config
import random
import cv2

TRACKING_RADIUS = config.TRACKING_RADIUS

class point2D:
    def __init__(self, x = 0, y = 0) -> None:
        self.x = x
        self.y = y

    @classmethod
    def from_array(cls, values) -> None:
        return cls(values[0], values[1])

    def set_from_array(self, keypoint: np.ndarray) -> None:
        self.x = keypoint[0]
        self.y = keypoint[1]

    def set_from_value(self, x, y) -> None:
        self.x = x
        self.y = y

    def get_value(self) -> None:
        return self.x, self.y
    
    def get_array(self) -> None:
        return np.array([self.x, self.y])
    
    def Show(self) -> None:
        if(self.x == 0 and self.y == 0):
            print("Pas d'infos sur le point")
        else :
            print(self.x,";",self.y)

    def get_dist(p1 : 'point2D', p2 : 'point2D') -> float:
        return np.sqrt((p1.x - p2.x)**2+(p1.y - p2.y)**2)


class skeleton:
    labels = (  "nose"              , "neck"            , "Right Shoulder"  , "Right Elbow"     , \
                "Right Wrist"       , "Left Shoulder"   , "Left Elbow"      , "Left Wrist"      , \
                "Middle Hip"        , "Right Hip"       , "Right Knee"      , "Right Ankle"     , \
                "Left Hip"          , "Left Knee"       , "Left Ankle"      , "Right Eye"       , \
                "Left Eye"          , "Right Ear"       , "Left Ear"        , "Left Big Toe"    , \
                "Left Small Toe"    , "Left Heel"       , "Right Big Toe"   , "Right Small Toe" , \
                "Right Heel"        , "Background")
    
    def __init__(self, keypoints = None) -> None:
        if(keypoints != None) : 
            self.tab = np.empty(26, dtype=point2D)
            for i in range (25):
                self.tab[i] = point2D(keypoints[i][0], keypoints[i][1])

    def barycenter(self) -> 'point2D':
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
        for i, keypoint in enumerate(keypoints):
            self.tab[i] = point2D.from_array(keypoint)

    def Show(self) -> None:
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
    nb_person = 0
    def __init__(self, keypoints =  None) -> None:
        skeleton.__init__(self, keypoints)
        person.nb_person += 1 
        self.id = random.randint(0, 100)
        self.start_time = 0

    def __del__(self) -> None:
        person.nb_person -= 1

    def set_start_time(self, time : float) -> None:
        self.start_time = time
   
    def get_time_from_start(self, time : float) -> float:
        return time - self.start_time
    
    def get_time_with_reset(self, time : float) -> float:
        res = time - self.start_time
        self.set_start_time(time)
        return res
    
    def get_idx_last(keypoints, list_person_last) -> int:
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
        idx = person.get_idx_last(keypoints, list_person_last)
        if(idx == -1) : # the person doesnt exist
            list_person[person.nb_person-1] = person(keypoints)
            return list_person[person.nb_person-1]
        else: # the person already exists
            list_person[idx] = list_person_last[idx]
            list_person[idx].update_from_array(keypoints)
            return list_person[idx]
            

def get_nb_person() -> None:
    return person.nb_person
