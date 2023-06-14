import numpy as np

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
    
    def __init__(self, keypoints) -> None:
        self.tab = np.empty(26, dtype=point2D)
        for i, keypoint in enumerate(keypoints):
            self.tab[i] = point2D.from_array(keypoint)

    def barycenter(self) -> 'point2D':
        rshoulder = point2D.get_array(self.tab[2])
        lshoulder = point2D.get_array(self.tab[5])
        rhip      = point2D.get_array(self.tab[9])
        lhip      = point2D.get_array(self.tab[12])
        res_x = (rshoulder[0] + lshoulder[0] + rhip[0] + lhip[0])/4.0
        res_y = (rshoulder[1] + lshoulder[1] + rhip[1] + lhip[1])/4.0
        return point2D(res_x, res_y)

    def update_keypoints(self, keypoints) -> None:
        for i, keypoint in enumerate(keypoints):
            del self.tab[i]
            self.tab[i] = point2D.from_array(keypoint)

    def Show(self) -> None:
        for label, keypoint in zip(skeleton.labels, self.tab):
            print(label, " : ", end='')
            keypoint.Show()

class person(skeleton):
    nb_person = 0
    def __init__(self, keypoints) -> None:
        skeleton.__init__(self, keypoints)
        person.nb_person += 1
        self.id = person.nb_person
        self.start_time = 0

    def set_start_time(self, time : float) -> None:
        self.start_time = time
   
    def get_time_from_start(self, time : float) -> float:
        return time - self.start_time
    
    def get_time_with_reset(self, time : float) -> float:
        res = time - self.start_time
        self.set_start_time(time)
        return res
    
    # A mettre à jour
    def detect_pose_last(self, pose_keypoints_last) -> int:
        #process new bbox data
        for hemi,bbox in zip(bbox_hemis, bbox_data):
            is_known_hand = False
            pos = np.array([ (bbox[0]+bbox[2])/2, (bbox[1]+bbox[3])/2 ])

            # check if data corresponds to hand that is already being tracked
            for hand in tracked_hands:
                if hand.scheduled_for_removal or hemi != hand.hemi:
                    continue

                dist = np.linalg.norm(hand.position-pos)
                if dist < config.tracking_radius:
                    is_known_hand = True
                    hand.add_pos_to_history(pos, t)
                    break

            # otherwise, create a new hand and keep track of it
            if not is_known_hand:
                tracked_hands.append(TrackedHand(next_hand_id, t, pos, hemi))
                next_hand_id += 1

    def update_last_frame(self, pose_keypoints_last, threshold : float) -> bool:
        """Class method from person that determines where a person was on previous frame and updates the new pose
            Args :
                pose_keypoints_last : array with persons detected on last frame
                thershold : the probablility required to say a person is the same on previous iteration
            Ret :
                bool : True if a person was detected on last iteration
        """
        idx_last, proba = self.detect_pose_last(self, pose_keypoints_last)
        if(proba > threshold):
            self.update_keypoints(pose_keypoints_last[idx_last])
            return True
        else :
            return False       

    def __del__(self) -> None:
        person.nb_person -= 1

def get_nb_person() -> None:
    return person.nb_person
