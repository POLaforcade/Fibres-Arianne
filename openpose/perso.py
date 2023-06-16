import numpy as np
from person import person
tab = np.empty(100, dtype = person)
tab2 = np.empty(100, dtype = person)
keypoints = np.ones([26, 2])
a = person(keypoints)
b = person(keypoints)
c = person(keypoints)
tab[1] = b
tab[0] = a
tab[2] = c
keypoints[2,:2] = 1, 1