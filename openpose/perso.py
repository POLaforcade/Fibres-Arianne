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