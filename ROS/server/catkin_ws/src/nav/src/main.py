#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
import actionlib
from actionlib_msgs.msg import GoalStatus
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import time
import pak
import random
import subprocess
from multiprocessing import Process			

class Car():
    def __init__(self):
        self.tally_car = list() #{carID:[itemID]} , dictionary list
        self.send_car = list()
        self.sql = pak.cars()

    def schedule(self):
        """"""
        first_state = pak.takeTask(self.sql)
        while  True:
            if first_state == "success" or first_state == "no remaining station":
                print("break")
                break
            time.sleep(5)
            first_state = pak.takeTask(self.sql) #get data from db
            print('no car need to schedule ',first_state)
            
        has_empty_station = False
        while True:
            print("current data:  ")
            print("merchans : ",self.sql.merchans)
            print("carids : ",self.sql.carids)
            print("taskid : ",self.sql.taskid)
            print("accomodates : ",self.sql.accomodates)
            print("cartypes : ",self.sql.cartypes)

            rospy.sleep(0.1)
            status = pak.takeTask(self.sql)
                
            if status == "no remaining car" or status == "no remaining task" :
                rospy.loginfo('end of searching')
                break
            elif status == "no remaining station":
                if has_empty_station:  # if there still has a station but can't assign for every task
                    break
                rospy.loginfo('no station need to assign')
                rospy.sleep(5)
            elif status == "success":
                has_empty_station = True
                rospy.loginfo('success')
                
            
        sql1 = list()
        for i in range(len(self.sql.carids)):
            sql1.append({str(self.sql.carids[i]):(int(self.sql.taskid[i]),int(self.sql.accomodates[i]),int(self.sql.cartypes[i]))})
        sql2 = list()
        for i in range(len(self.sql.merchans)):
            tasks = list()
            for j in range(len(self.sql.merchans[i])):
                tasks.append((int(self.sql.merchans[i][j][0]),int(self.sql.merchans[i][j][1])))
            sql2.append({int(self.sql.taskid[i]):tasks})
        #print("sql2 : ",sql2 )
        #print("sql1 : ",sql1 )
        if len(sql1) != 0:
            #sql2 = [{1:(0,2)}] #get taskID:itemID,weight
            for idx,car in enumerate(sql1):
                #print("middle car : ",car)
                temp = list()
                mid = list(car.values())[0]
                max = 9999  
                itemID = list(sql2[idx].keys())[0]
                items = sorted(list(sql2[idx].values())[0])
                for item in items :
                    #print("middle task : ",itemID," ",item)
                    if mid[0] == itemID and max >= int(item[1]):
                        temp.append(item[0])
                        max -= int(item[1])
                if mid[2] == 0:
                    self.tally_car.append({list(car.keys())[0]:[temp,itemID]})
            #print('push to tally_car:',self.tally_car)
        
        #self.tally_car = [{'0':[[0,1],0]},{'1':[[2],0]}]
        #self.sql.stationid = ['0','0']
        #self.sql.taskid = ['0','0']
        #pak.launchMerchan(self.sql,1)
        #pak.carArrive(self.sql,1)
        print("final : ",self.tally_car)
        print("station : ",self.sql.stationid)
    def get_car(self):
        return self.tally_car,self.send_car
    
class Nav():
    # position data
    initial_place = [
	  # do not use
	  [0.5895287368630184,1.9000875830678288,-0.05744066848786845,0.9983489217721762] ,
	  [0.4201565167342714,1.0383956565977317,-0.014980046402196995,0.9998877928096672],	
	  [0.016035294778452423,-0.0035577143435607146,8.560345123093146e-05,0.9999999963360245]
	]
    item_position = [
    	[0.7341217947748327,1.9073793519205422,0.49577000347788797,0.868453858101589],
    	[1.1398319689169147,2.040839271487419,0.5978894215180562,0.8015785923019677],
    	[0.7593705163130792,1.1423676484214649,0.496744268591124,0.8678969591039418],
    	[1.163481858773432,1.00556929841036,0.6276954052745638,0.778459040796111],
    	[0.5525260612491719,0.030803656989628808,0.3487649601560062,0.9372102232516349],
    	[1.0151656502593644,0.05888813915947721,0.715123943319666,0.698997672164172]
    ]
    queue_position = [2.402425875584643,2.497733987859967,0.5936654900685363,0.8047119272768887]
    park_position = [
        [1.9869690649332121,3.6323470872617665,0.9990037112703443,0.04462717633996788],  # do not use
        [1.1590134774541148,3.7220960537943824,-0.9981668136557191,0.0605228231032633],
        [0.12399449888856964,3.545056315872953,-0.6841881612496301,0.729305532685616]
    ]

    waiting_position = [
          [1.6246154205660488,2.1600964324603282,0.05815816453997793,0.9983073814699263],
        [1.419611376790349,1.1857574319683621,0.16649911982464113,0.9860416031271804],
      
        [1.4208189084445662,0.17597047619320583,-0.0075582891887431,0.9999714357243107]
    ]
    name = ["banana","cucumber","chicken","egg","papaya",""]
    def __init__(self):
        self.car = Car()
        rospy.init_node('nav_planner', anonymous=True)
        self.sub = rospy.Subscriber('/can_go_pool',String,self.callback)
 
    def callback(self,data): #print stats from camera.py
        log = data.data.split(',')
        if len(log) == 2:
            if log[1] == 't':
                print("launching car : ",(int(log[0])-1))
                pak.launchMerchan(self.car.sql,(int(log[0])-1))
            elif log[1] == 'f':
                print("car arrived : ",(int(log[0])-1))
                pak.carArrive(self.car.sql,(int(log[0])-1))

    def start(self):
        self.car.schedule()
        cid = list()
        for car in self.car.tally_car:
            cid.append(list(car.keys())[0])
        for car in self.car.send_car:
            cid.append(list(car.keys())[0])
        

    def move(self,cmd): #multithreading
        args = cmd.split(" ")
        proc = subprocess.Popen(args)
        proc.wait() #thread will wait untill the subprocess dead
        print("ENDSSSS")
            
    def navigating(self):
        tally_car,send_car = self.car.get_car()
        send_thread = list()
        # car = {carID:[[itemID],collection_area]}
        for car in tally_car:  #2 tally car, plan route 
            route = list()
            cid = int(list(car.keys())[0])
            points = ""
            data = ""
            plans = list(car.values())[0]   #plans = [[itemID],collection_area]
            idx = self.car.sql.taskid.index(str(plans[1]))
            station = self.car.sql.stationid[idx]
            print("plans : ",plans)
            for plan in plans[0]:
                name_coor = pak.MTrans(plan)  # name with coordinate [name,x,y,z,w]
                route.append(name_coor[1:]) #name_coor[1:]
                data += name_coor[0]+" " #name_coor[0]
                rospy.sleep(0.1)
            data += "wait queue "+station+" init"  # target name
            self.data_list = data
            route.append(self.waiting_position[cid])
            route.append(self.queue_position)
            route.append(self.park_position[int(station)])
            route.append(self.initial_place[cid])
            for _,i in enumerate(route):
                temp = "-p"+str((_+1))+" "
                for j in i:
                    temp += str(j)+" "
                points+= temp
            points += ("-pname "+str(cid))
            points += (" -pdata "+data)
            points += (" -pri 1")
            cmd = 'rosrun nav plan.py '+points
            send_thread.append( Process(target=self.move,args=(cmd,)) )
            print(cmd)
        for send in send_thread:
            send.start()
	
        for send in send_thread:
            send.join()
        print("END PROS")
        time.sleep(2)
def main():
    while True:
        navigation = Nav()
        navigation.start() #get data from db and schedule cars
        
        
        navigation.navigating() #start navigation
        print('finish')

        if rospy.is_shutdown():
            break

if __name__ == '__main__':
    main()
    
    
    
