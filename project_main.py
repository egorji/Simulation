

import simpy
import matplotlib.pyplot as plt
import random
import numpy as np
from scipy import stats


SIM_TIME=720
GREEN_TIME=30
RED_TIME=60
CAR_LENGTH=4.5

TIME_INTERVAL_RUSH= 2    #rush hours
TIME_INTERVAL_REGULAR= 5  #regular hours

class Driver():

    def __init__(self):
        self.id=0
        self.direction=None
        self.turn1=None
        if random.uniform(0,1) <0.3:     #driver violates the speed limit with 30% chance
            self.violate=True
        else:
            self.violate=False
        if self.violate:
            self.speed=random.uniform(16.66,20)
        else:
            self.speed=16.66
        self.reaction_time=random.uniform(0, 2)
        self.acceleration_rate=6
        self.gas_idle=0
        self.gas_accelr=0
        self.gas_norm=0
        self.wait=0
        self.pass_time=0




class Area():

    def __init__(self,a,b,env):
        self.env=env
        self.A=a
        self.B=b
        self.total_passTime=[]
        self.total_emision_idle=0
        self.total_emision_accelr=0
        self.total_emision_norm=0
        self.waiting_times=[]
        self.A_EW_green=env.event()
        self.A_NS_green=env.event()
        self.A_EW_light=False
        self.A_NS_light=False
        if random.choice([True,False]):
            self.A_EW_green.succeed()
            self.A_EW_green = env.event()
            self.A_EW_light=True
        else:
            self.A_NS_green.succeed()
            self.A_NS_green = env.event()
            self.A_NS_light=True


    def A_changeLight(self,green_time,red_time):
        if self.A_EW_light:
            yield self.env.timeout(random.uniform(0, green_time))
            while True:
                #area.A_EW_green.fail()
                self.A_NS_green.succeed()
                self.A_NS_green=self.env.event()
                self.A_NS_light=True
                self.A_EW_light=False
                yield self.env.timeout(red_time)
                #area.A_NS_green.fail()
                self.A_EW_green.succeed()
                self.A_EW_green=self.env.event()
                self.A_EW_light = True
                self.A_NS_light =False
                yield self.env.timeout(green_time)
        elif self.A_NS_light:
            yield self.env.timeout(random.uniform(0, green_time))
            while True:

                self.A_EW_green.succeed()
                self.A_EW_green=self.env.event()
                self.A_EW_light = True
                self.A_NS_light =False
                yield self.env.timeout(red_time)

                self.A_NS_green.succeed()
                self.A_NS_green=self.env.event()
                self.A_NS_light = True
                self.A_EW_light = False
                yield self.env.timeout(green_time)


def driver_arrive(env,area,timeInterval,A,B,raod_eastbound, road_westbound,distance):
    id=1
    while True:
        yield (env.timeout(random.expovariate(1 / timeInterval)))   #?????
        driver = Driver()
        driver.arrival_time=env.now
        driver.id = id
        intersect=random.uniform(0,1)
        if intersect<=0.467:         #creating a probability of driver intersection according to dataset
            #driver.intersection=A
            print("driver {} received at intersection A.".format(driver.id))
            direction=random.uniform(0,1)
            if direction<=0.225:      #creating a probability of driver direction according to dataset
                driver.direction="north"
            elif 0.225<direction and direction<=0.743:
                driver.direction="east"
            else:
                driver.direction="south"

            turn=random.uniform(0,1)
            if turn<=0.460:
                driver.turn1="straight"
            elif 0.460<turn and turn<=0.716:
                driver.turn1="right"
            else:
                driver.turn1="left"
            env.process(driver_in_A(env,area,driver,A,B,raod_eastbound,distance))

        else:
            #driver.intersection=B
            print("driver {} received at intersection B.".format(driver.id))
            direction = random.uniform(0, 1)
            if direction <= 0.200:  # creating a probability of driver direction according to dataset
                driver.direction = "north"
            elif 0.200 < direction and direction <= 0.680:
                driver.direction = "west"
            else:
                driver.direction = "south"

            turn = random.uniform(0, 1)
            if turn <= 0.420:
                driver.turn1 = "straight"
            elif 0.420 < turn and turn <= 0.752:
                driver.turn1 = "right"
            else:
                driver.turn1 = "left"
            env.process(driver_in_B(env, area, driver,A,B,road_westbound,distance))

        id+=1


def driver_in_A(env,area,driver,A,B,raod_eastbound,distance):

    if driver.direction in ['north', 'south']:
        with A.request() as request:
            if area.A_NS_light==False:
                yield request & area.A_NS_green
            else:
                yield request
            driver.gas_idle=env.now-driver.arrival_time
            driver.wait+=env.now-driver.arrival_time

            if driver.turn1=="straight" or (driver.direction=="north" and driver.turn1=="left")\
                or (driver.direction=="south" and driver.turn1=="right"):  #driver intents to exits the area
                if  env.now-driver.arrival_time>0:  # driver stopped at the intersection
                    yield env.timeout(driver.reaction_time)   #driver reaction time
                    driver.gas_idle+=driver.reaction_time
                    time_release_intersection=distance/1.66    #the time needed for driver to pass and release the intersection
                    yield env.timeout(time_release_intersection)   #passes the intersection with speed 6 km/h
                    driver.gas_accelr+=(5*time_release_intersection)     #5 g per second and 50 g in 10 second

                else:  # driver didn't stop and pass the intersection with constant speed
                    time_release_intersection=distance/16.66
                    yield env.timeout(time_release_intersection)    #passes the intersection with 60km/h and takes around 1 second to pass
                    driver.gas_norm+=(2.5*time_release_intersection)

                driver.pass_time=env.now-driver.arrival_time
                print("driver {} left the area with {} seconds waiting and {} seconds passing time".format(driver.id,driver.wait, driver.pass_time))
                area.total_passTime.append(driver.pass_time)
                area.total_emision_idle+=driver.gas_idle
                area.total_emision_accelr+=driver.gas_accelr
                area.total_emision_norm+=driver.gas_norm
                area.waiting_times.append(driver.wait)
                return

            else:   #driver intends to move toward B
                pass
        with raod_eastbound.request() as road_request:
            yield road_request
            if env.now-driver.arrival_time>0:  # driver stopped at the intersection
                yield env.timeout(driver.reaction_time)
                driver.gas_idle+=driver.reaction_time   #driver reaction time
                time_release_intersection = distance / 1.66
                yield env.timeout(time_release_intersection)   #moves through the intersection with speed 6 km/h
                driver.gas_accelr+=(5*10)     #10 seconds of acceleration in the area
                remaining_time_acceleration=10-time_release_intersection   #the remaining time driver accelerates after releasing the interseciton
                distance_moved_acceleration=remaining_time_acceleration*1.66   #the distance driver moves in acceleration speed after releasing intersection
                remaining_way=450-distance-distance_moved_acceleration   #the remaining way that driver should move to reach B with normal speed

            else:   #diver didn't stop at the intersecion
                time_release_intersection = distance / 16.66
                yield env.timeout(time_release_intersection)
                driver.gas_norm += (2.5*time_release_intersection)
                remaining_way=450-distance

            #considering the width of the intersections is equal to 5, the total way drivers should pass to reach B is 425+5=450
            yield env.timeout(remaining_way/driver.speed)   #time to reach to intersection B with the constant speed 16.66 m/sec
            driver.gas_norm+=2.5*(remaining_way/driver.speed)

        #driver reaches to intersection B
        driver_reach_B=env.now
        with B.request(priority=1) as request:
            yield request
            driver.wait+=env.now-driver_reach_B
            driver.gas_idle+=env.now-driver_reach_B

            if env.now-driver_reach_B==0:    #driver didn't stop at intersection B
                time_release_intersection = distance / 16.66
                yield env.timeout(time_release_intersection)
                driver.gas_norm += (2.5 * time_release_intersection)
            else:    #driver stopped at intersection B
                yield env.timeout(driver.reaction_time)
                driver.gas_idle += driver.reaction_time  # driver reaction time
                time_release_intersection = distance / 1.66
                yield env.timeout(time_release_intersection)  # moves through the intersection with speed 6 km/h
                driver.gas_accelr += (5 * time_release_intersection)

            driver.pass_time=env.now-driver.arrival_time
            print("driver {} left the area with {} seconds waiting and {} seconds passing time".format(driver.id,driver.wait, driver.pass_time))
            area.total_passTime.append(driver.pass_time)
            area.total_emision_idle += driver.gas_idle
            area.total_emision_accelr += driver.gas_accelr
            area.total_emision_norm += driver.gas_norm
            area.waiting_times.append(driver.wait)
    else:
        with A.request() as request:
            if area.A_EW_light==False:
                yield request & area.A_EW_green
            else:
                yield request
            driver.gas_idle = env.now - driver.arrival_time
            driver.wait += env.now - driver.arrival_time
            if driver.turn1 in ["right","left"]:    #driver intends to exit the area
                if env.now - driver.arrival_time > 0:  # driver stopped at the intersection
                    yield env.timeout(driver.reaction_time)   #driver reaction time
                    driver.gas_idle+=driver.reaction_time
                    time_release_intersection = distance / 1.66
                    yield env.timeout(time_release_intersection)  # moves through the intersection with speed 6 km/h
                    driver.gas_accelr += (5 * time_release_intersection)
                else:     #driver didn't stop at the intersection
                    time_release_intersection = distance / 1.66
                    yield env.timeout(time_release_intersection)  # moves through the intersection with speed 6 km/h
                    driver.gas_accelr += (2.5 * time_release_intersection)

                driver.pass_time+=env.now-driver.arrival_time
                print("driver {} left the area with {} seconds waiting and {} seconds passing time".format(driver.id,driver.wait, driver.pass_time))
                area.total_passTime.append(driver.pass_time)
                area.total_emision_idle += driver.gas_idle
                area.total_emision_accelr += driver.gas_accelr
                area.total_emision_norm += driver.gas_norm
                area.waiting_times.append(driver.wait)
                return
            else:    #driver intends to move toward B
                pass
        with raod_eastbound.request() as road_request:
            yield road_request
            if env.now - driver.arrival_time > 0:  # driver stopped at the intersection
                yield env.timeout(driver.reaction_time)
                driver.gas_idle+= driver.reaction_time  # driver reaction time
                time_release_intersection = distance / 1.66
                yield env.timeout(time_release_intersection)  # moves through the intersection with speed 6 km/h
                driver.gas_accelr += (5 * 10)
                remaining_time_acceleration = 10 - time_release_intersection  # the remaining time driver accelerates after releasing the interseciton
                distance_moved_acceleration = remaining_time_acceleration * 1.66  # the distance driver moves in acceleration speed after releasing intersection
                remaining_way = 450 - distance - distance_moved_acceleration

            else:  # diver didn't stop at the intersecion
                time_release_intersection = distance / 16.66
                yield env.timeout(time_release_intersection)
                driver.gas_norm += (2.5 * time_release_intersection)
                remaining_way = 450 - distance

            yield env.timeout(remaining_way / driver.speed)  # time to reach to intersection B with the constant speed 16.66 m/sec
            driver.gas_norm += 2.5 * (remaining_way / driver.speed)

        # driver reaches to intersection B
        driver_reach_B = env.now
        with B.request(priority=1) as request:
            yield request
            driver.wait += env.now - driver_reach_B
            driver.gas_idle += env.now - driver_reach_B

            if env.now - driver_reach_B == 0:  # driver didn't stop at intersection B
                time_release_intersection = distance / 16.66
                yield env.timeout(time_release_intersection)
                driver.gas_norm += (2.5 * time_release_intersection)
            else:  # driver stopped at intersection B
                yield env.timeout(driver.reaction_time)
                driver.gas_idle += driver.reaction_time  # driver reaction time
                time_release_intersection = distance / 1.66
                yield env.timeout(time_release_intersection)  # moves through the intersection with speed 6 km/h
                driver.gas_accelr += (5 * time_release_intersection)

            driver.pass_time = env.now - driver.arrival_time
            print("driver {} left the area with {} seconds waiting and {} seconds passing time".format(driver.id,driver.wait, driver.pass_time))
            area.total_passTime.append(driver.pass_time)
            area.total_emision_idle += driver.gas_idle
            area.total_emision_accelr += driver.gas_accelr
            area.total_emision_norm += driver.gas_norm
            area.waiting_times.append(driver.wait)

def driver_in_B(env, area, driver,A,B,road_westbound,distance):

    if driver.direction in ['north','south']:
        #driver.priority_id=2
        with B.request(priority=2) as request:
            yield request
            driver.wait=env.now-driver.arrival_time
            driver.gas_idle+=driver.wait

            if driver.turn1=="straight" or (driver.direction=="north" and driver.turn1=="right")\
                or (driver.direction=="south" and driver.turn1=="left"):      #driver intents to exit the area

                if env.now-driver.arrival_time==0:    #driver didn't stop at intersection
                    time_release_intersection = distance / 16.66
                    yield env.timeout(time_release_intersection)
                    driver.gas_norm += (2.5 * time_release_intersection)
                else:    #driver stopped at the intersection
                    yield env.timeout(driver.reaction_time)
                    driver.gas_idle+=driver.reaction_time
                    time_release_intersection = distance / 1.66
                    yield env.timeout(time_release_intersection)  # moves through the intersection with speed 6 km/h
                    driver.gas_accelr += (5 * time_release_intersection)

                driver.pass_time = env.now - driver.arrival_time
                print("driver {} left the area with {} seconds waiting and {} seconds passing time".format(driver.id,driver.wait, driver.pass_time))
                area.total_passTime.append(driver.pass_time)
                area.total_emision_idle += driver.gas_idle
                area.total_emision_accelr += driver.gas_accelr
                area.total_emision_norm += driver.gas_norm
                area.waiting_times.append(driver.wait)
                return

            else:    # driver intends to move toward A
                pass
        with road_westbound.request() as road_request:
            yield road_request
            if env.now-driver.arrival_time > 0:  # driver stopped at the intersection
                yield env.timeout(driver.reaction_time)
                driver.gas_idle+= driver.reaction_time  # driver reaction time
                time_release_intersection = distance / 1.66
                yield env.timeout(time_release_intersection)  # moves through the intersection with speed 6 km/h
                driver.gas_accelr += (5 * 10)
                remaining_time_acceleration = 10 - time_release_intersection  # the remaining time driver accelerates after releasing the interseciton
                distance_moved_acceleration = remaining_time_acceleration * 1.66  # the distance driver moves in acceleration speed after releasing intersection
                remaining_way = 450 - distance - distance_moved_acceleration

            else:  # diver didn't stop at the intersecion
                time_release_intersection = distance / 16.66
                yield env.timeout(time_release_intersection)
                driver.gas_norm += (2.5 * time_release_intersection)
                remaining_way = 450 - distance

            yield env.timeout(remaining_way / driver.speed)  # time to reach to intersection A with the constant speed 16.66 m/sec
            driver.gas_norm += 2.5 * (remaining_way / driver.speed)

        #driver reaches to A
        driver_reach_A=env.now
        with A.request() as request:
            if area.A_EW_light==False:
                yield request & area.A_EW_green
            else:
                yield request
            driver.wait += env.now - driver_reach_A
            driver.gas_idle += env.now - driver_reach_A
            if env.now - driver_reach_A==0:    #driver didn't stop at the intersection
                time_release_intersection = distance / 16.66
                yield env.timeout(time_release_intersection)
                driver.gas_norm += (2.5 * time_release_intersection)
            else:        #driver stopped at intersection
                yield env.timeout(driver.reaction_time)
                driver.gas_idle+=driver.reaction_time
                time_release_intersection = distance / 1.66
                yield env.timeout(time_release_intersection)  # moves through the intersection with speed 6 km/h
                driver.gas_accelr += (5 * time_release_intersection)

            driver.pass_time = env.now - driver.arrival_time
            print("driver {} left the area with {} seconds waiting and {} seconds passing time".format(driver.id,driver.wait, driver.pass_time))
            area.total_passTime.append(driver.pass_time)
            area.total_emision_idle += driver.gas_idle
            area.total_emision_accelr += driver.gas_accelr
            area.total_emision_norm += driver.gas_norm
            area.waiting_times.append(driver.wait)
            return

    else:      #driver direction is westbound
        with B.request(priority=1) as request:
            yield request
            driver.wait += env.now - driver.arrival_time
            driver.gas_idle += env.now - driver.arrival_time
            if driver.turn1 in ["left","right"]:      #driver intends to exit the area
                if env.now-driver.arrival_time==0:   #didn't stop at the intersection
                    time_release_intersection = distance / 16.66
                    yield env.timeout(time_release_intersection)
                    driver.gas_norm += (2.5 * time_release_intersection)
                else:
                    yield env.timeout(driver.reaction_time)
                    driver.gas_idle+=driver.reaction_time
                    time_release_intersection = distance / 1.66
                    yield env.timeout(time_release_intersection)  # moves through the intersection with speed 6 km/h
                    driver.gas_accelr += (5 * time_release_intersection)

                driver.pass_time = env.now - driver.arrival_time
                print("driver {} left the area with {} seconds waiting and {} seconds passing time".format(driver.id,driver.wait, driver.pass_time))
                area.total_passTime.append(driver.pass_time)
                area.total_emision_idle += driver.gas_idle
                area.total_emision_accelr += driver.gas_accelr
                area.total_emision_norm += driver.gas_norm
                area.waiting_times.append(driver.wait)
                return
            else:    #driver intends to move toward A
                pass
        with road_westbound.request() as road_request:
            yield road_request

            if env.now - driver.arrival_time == 0:  # didn't stop at the intersection
                time_release_intersection = distance / 16.66
                yield env.timeout(time_release_intersection)
                driver.gas_norm += (2.5 * time_release_intersection)
                remaining_way = 450 - distance
            else:
                yield env.timeout(driver.reaction_time)
                driver.gas_idle += driver.reaction_time
                time_release_intersection = distance / 1.66
                yield env.timeout(time_release_intersection)  # moves through the intersection with speed 6 km/h
                driver.gas_accelr += (5 * 10)
                remaining_time_acceleration = 10 - time_release_intersection  # the remaining time driver accelerates after releasing the interseciton
                distance_moved_acceleration = remaining_time_acceleration * 1.66  # the distance driver moves in acceleration speed after releasing intersection
                remaining_way = 450 - distance - distance_moved_acceleration

            yield env.timeout(remaining_way / driver.speed)  # time to reach to intersection A with the constant speed 16.66 m/sec
            driver.gas_norm += 2.5 * (remaining_way / driver.speed)

            # driver reaches to A
            driver_reach_A = env.now
            with A.request() as request:
                if area.A_EW_light==False:
                    yield request & area.A_EW_green
                else:
                    yield request
                driver.wait += env.now - driver_reach_A
                driver.gas_idle += env.now - driver_reach_A
                if env.now - driver_reach_A == 0:  # driver didn't stop at the intersection
                    time_release_intersection = distance / 16.66
                    yield env.timeout(time_release_intersection)
                    driver.gas_norm += (2.5 * time_release_intersection)
                else:  # driver stopped at intersection
                    yield env.timeout(driver.reaction_time)
                    driver.gas_idle += driver.reaction_time
                    yield env.timeout(driver.reaction_time)
                    driver.gas_idle += driver.reaction_time
                    time_release_intersection = distance / 1.66
                    yield env.timeout(time_release_intersection)  # moves through the intersection with speed 6 km/h
                    driver.gas_accelr += (5 * time_release_intersection)

                driver.pass_time = env.now - driver.arrival_time
                print("driver {} left the area with {} seconds waiting and {} seconds passing time".format(driver.id,driver.wait, driver.pass_time))
                area.total_passTime.append(driver.pass_time)
                area.total_emision_idle += driver.gas_idle
                area.total_emision_accelr += driver.gas_accelr
                area.total_emision_norm += driver.gas_norm
                area.waiting_times.append(driver.wait)


def runsim(time_interval, hour,distance):

    env=simpy.Environment()
    A=simpy.Resource(env, capacity=1)
    B=simpy.PriorityResource(env, capacity=1)
    road_eastbound=simpy.Resource(env, capacity=int(425/(CAR_LENGTH+distance)))   #assumptions made by the standard car length and the distance between intersections
    road_westbound=simpy.Resource(env, capacity=int(425/(CAR_LENGTH+distance)))

    area=Area(A,B,env)
    env.process(area.A_changeLight(GREEN_TIME,RED_TIME))
    env.process(driver_arrive(env, area, time_interval,A,B,road_eastbound,road_westbound,distance))
    env.run(until=SIM_TIME)
    print("="*40)
    if hour=="rush":
        steady_num=150
    else:
        steady_num=10
    steady_waiting_times=area.waiting_times[steady_num:]
    steady_pass_times=area.total_passTime[steady_num:]
    print("distance between cars: ",distance)
    print("Area average waiting times in {} hours: {:5.3f}".format(hour,np.mean(steady_waiting_times)))
    print("waiting time statistics:")
    print("standard deviation: {:5.3f}".format(np.std(steady_waiting_times)))
    print("minimum waiting time: {:5.3f}    maximum waiting time: {:5.3f}".format(np.min(steady_waiting_times),np.max(steady_waiting_times)))
    print("Quantiles:   Q1={:5.3f}    Q2={:5.3f}     Q3={:5.3f}".format(np.quantile(steady_waiting_times,.25),\
                                                                        np.quantile(steady_waiting_times,.5),\
                                                                        np.quantile(steady_waiting_times,.75)))
    print()
    print("Area average passing times in {} hours: {:5.3f}".format(hour,np.mean(steady_pass_times)))
    print("Area total pullution emitted due to cars idling in {} hours: {:6.3f}".format(hour,area.total_emision_idle))
    print("Area total pullution emitted due to cars accelerating in {} hours: {:6.3f}".format(hour,area.total_emision_accelr))
    print("Area total pullution emitted due to cars moving in normal speed in {} hours: {:7.3f}".format(hour,area.total_emision_norm))


    plt.figure("passing times")
    plt.plot(steady_pass_times)
    plt.figure("waiting times")
    plt.plot(steady_waiting_times)
    plt.show()
    #return area.waiting_times, area.total_passTime     #used for finding the steady state


def main():
    print("Intersection area simulation:")
    option=int(input("enter 1 for rush hours and 2 for regular hours: "))
    if option== 1:
        time_interval=TIME_INTERVAL_RUSH
        hour="rush"

    else:
        time_interval=TIME_INTERVAL_REGULAR
        hour="regular"

    #run a single time
    runsim(time_interval, hour,distance=4)

if __name__=="__main__":
    main()


# def elementwise_average(lists):
#     shortest_length = min([len(l) for l in lists])
#     averages = [sum([l[timestep] for l in lists])/len(lists) for timestep in range(shortest_length)]
#     return averages


### Steady State
# running the simulation for numurus times to find the steady state for the rush hours
## after running the program 200 times, we observe that the system reaches to a steady state after around 150 drivers passed\
# through the area in rush hours or 10 drivers passed thruogh the area in regular hours .
## Thus, we will ignore the 150 first drivers in calculating the statistics for passing and waiting times.
# numurus=200
# passTimeLists=[]
# waitTimeLists=[]
# for i in range (numurus):
#     waitTime, passTime = runsim(TIME_INTERVAL_RUSH, "rush", 4)
#     #waitTime , passTime=runsim(TIME_INTERVAL_REGULAR, "regular",4)
#     passTimeLists.append(passTime)
#     waitTimeLists.append(waitTime)
#     passAverages = elementwise_average(passTimeLists)
#     waitAverages=elementwise_average(waitTimeLists)
#
# plt.figure("pass times")
# plt.plot(passAverages)
#
# plt.figure("wait times")
# plt.plot(waitAverages)
# plt.show()


### calibration on distance between cars
# for distance in range(3,7):
#     runsim(2, "rush", distance)

# for distance in range(3,7):
#     runsim(5, "regular", distance)
















