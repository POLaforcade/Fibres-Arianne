import numpy as np
from person import person

list_person = np.empty(20, dtype=person)

tab = np.ones([26, 2])
p1 = person(tab)
list_person[0] = p1

tab.fill(200)
p2 = person(tab)
list_person[1] = p2

tab.fill(200)
p3 = person(tab)
list_person[2] = p3

for Person in list_person:
    if Person == None:
        continue
    Person.update()

keypoints = np.ones([26, 2])
keypoints[2] = np.array([2 ,2])
person.tracking(keypoints, list_person)

for Person in list_person:
    if Person == None:
        continue
    Person.update()