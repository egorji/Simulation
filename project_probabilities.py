
""" calculating distributions and probabilities of the intersection area dataset
to be used for intersection area simulation"""

import pandas as pd
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt
import math
import statistics
import numpy as np
from distfit import distfit

data=pd.read_excel(r"BDA450 W22 Project - Traffic Data.xlsx")

# drivers arriving at intersection A from out of the area
A=data[(data.Intersection=="A") & (data.Direction.isin(["Northbound","Southbound","Eastbound"]))]

# drivers arriving at intersection B from out of the area
B=data[(data.Intersection=="B") & (data.Direction.isin(["Northbound","Southbound","Westbound"]))]

# drivers arriving from out of the area
out=A.append(B)

# drivers arriving from out of the area in rush hours
rush=out[((4<=out.Hour)& (out.Hour<=7)) | ((13<=out.Hour)&(out.Hour<=21))]
# drivers arriving from out of the area in regular hours
regular=out[~(((4<=out.Hour)& (out.Hour<=7)) | ((13<=out.Hour)&(out.Hour<=21)))]


# distribution of drivers arriving from out of the area in both intersections in rush hours is foldcauchy(c=0.979331)
# dist_rush=distfit(distr="full")
# dist_rush.fit_transform(rush.Count)
# print(dist_rush.summary)
# print(dist_rush.model)
# dist_rush.plot_summary()
# dist_rush.plot()
# plt.show()

# distribution of drivers arriving from out of the area in both intersections in rush hours is johnsonsu(a=-1.88816, b=0.867589)
# dist_regular=distfit(distr="full")
# dist_regular.fit_transform(regular.Count)
# print(dist_regular.summary)
# print(dist_regular.model)
# dist_regular.plot_summary()
# dist_regular.plot()
# plt.show()





#probability of drivers arriving from out of the area arrive in A/B
P_arrive_A=A.Count.sum()/out.Count.sum()
P_arrive_B=B.Count.sum()/out.Count.sum()
print("p of arriving in A: {} , p of arriving in B: {}".format(P_arrive_A,P_arrive_B))



#the probability of drivers arriving to A from out of the area moving northbound
A_northbound=A[A.Direction=="Northbound"]
p_A_northbound=A_northbound.Count.sum()/A.Count.sum()
print("A northbound: ", p_A_northbound)

#the probability of people arriving to A from out of the area moving eastbound
A_eastbound=A[A.Direction=="Eastbound"]
p_A_eastbound=A_eastbound.Count.sum()/A.Count.sum()
print("A eastbound: ", p_A_eastbound)

#the probability of people arriving to A from out of the area moving southbound
A_southbound=A[A.Direction=="Southbound"]
p_A_southbound=A_southbound.Count.sum()/A.Count.sum()
print("A southbound: ", p_A_southbound)

#the probability of people arriving to A from out of the area of Turning Straight
A_straight=A[A.Turn=="Straight"]
p_A_straight=A_straight.Count.sum()/A.Count.sum()
print("A and straight: ", p_A_straight)

#the probability of people arriving to A from out of the area of Turning right
A_right=A[A.Turn=="Right turn"]
p_A_right=A_right.Count.sum()/A.Count.sum()
print("A and right: ", p_A_right)

#the probability of people arriving to A from out of the area of Turning left
A_left=A[A.Turn=="Left turn"]
p_A_left=A_left.Count.sum()/A.Count.sum()
print("A and left: ", p_A_left)

#the probability of people arriving to B from out of the area moving northbound
B_northbound=B[B.Direction=="Northbound"]
p_B_northbound=B_northbound.Count.sum()/B.Count.sum()
print("B northbound: ", p_B_northbound)

#the probability of people arriving to B from out of the area moving westbound
B_westbound=B[B.Direction=="Westbound"]
p_B_westbound=B_westbound.Count.sum()/B.Count.sum()
print("B westbound: ", p_B_westbound)

#the probability of people arriving to B from out of the area moving southbound
B_southbound=B[B.Direction=="Southbound"]
p_B_southbound=B_southbound.Count.sum()/B.Count.sum()
print("B southbound: ", p_B_southbound)

#the probability of people arriving to B from out of the area of Turning Straight
B_straight=B[B.Turn=="Straight"]
p_B_straight=B_straight.Count.sum()/B.Count.sum()
print("B and straight: ", p_B_straight)

#the probability of people arriving to B from out of the area of Turning right
B_right=B[B.Turn=="Right turn"]
p_B_right=B_right.Count.sum()/B.Count.sum()
print("B and right: ", p_B_right)

#the probability of people arriving to B from out of the area of Turning left
B_left=B[B.Turn=="Left turn"]
p_B_left=B_left.Count.sum()/B.Count.sum()
print("B and left: ", p_B_left)



# r = st.foldcauchy.rvs(c=0.979331,size=100)
# print("rush avg: " ,np.mean(r))     # rush avg:  2.2060077000016225
#
# r2=st.johnsonsu.rvs(a=-1.88816, b=0.867589,size=100)
# print("regular avg: ", np.mean(r2))     # regular avg:  5.934531175026409
