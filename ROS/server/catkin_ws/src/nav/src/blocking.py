#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from geometry_msgs.msg import PoseWithCovarianceStamped
import random

#considering priority and car_id in queue.
#change to list

class Blocking():
    base_line = [2.1600964324603282,1.1857574319683621,0.17597047619320583]
    current_pose = [0.0,0.0,0.0]
    arrive_queue = [False for _ in range(3)]
    working = [False for _ in range(3)]
    def call(self,data):
        msg = data.data.split(',')
        n = len(msg)
        msg[0] = str(int(msg[0])-1)
        if n==3:
            cid = int(msg[0])
            place = int(msg[1])
            state = int(msg[2])
            idx = 0
            for i in range(len(self.car)):
                if self.car[i][0] == cid:
                    idx = i
                    break
            can_go = True
            can_go2 = True
            if cid == self.car[0][0] and state == 0:
                rospy.loginfo("Car : "+str(cid+1)+" is going to collection area "+str(place))
                self.pub.publish(str(cid+1)+',1')
                self.working[cid] = True
            elif int(cid) == self.planning[place][0] and state == 0:
                for plan in range(0,place):
                    if len(self.planning[plan]) != 0:
                        can_go = False
                        break
                for id in range(idx):
                    if self.working[id] == False:
                        can_go2 = False
                        break
                if can_go and can_go2:
                    self.working[cid] = True
                    rospy.loginfo("Car : "+str(cid+1)+" is going to collection area "+str(place))
                    self.pub.publish(str(cid+1)+',1')
            elif  state == 1:
                rospy.loginfo("Car : "+str(cid+1)+" is leaving collection area "+str(place))
                self.planning[place].pop(0)
        elif n==2:
            if msg[1] == 'l':
                rospy.loginfo("locking car : "+str(int(msg[0])+1))
                for idx,car in enumerate(self.car):
                    if car[0] == int(msg[0]):
                        self.car[idx][2] = 1
                        self.start_blocking = True
                        break
            if msg[1] == 'f':
                rospy.loginfo("freeing car : "+str(int(msg[0])+1)) 
                for idx,car in enumerate(self.car):
                    if car[0] == int(msg[0]):
                        self.arrive_queue[car[0]] = False
                        self.car.pop(idx)
                        break
            
        else:
            self.planning = [[] for _ in range(3)]
            self.car.append([int(msg[0]),int(msg[1]),0])
            self.area.update({int(msg[0]):[int(place) for place in msg[3:]]})
            fixed = []
            index = []
            for i in range(len(self.car)):
                if self.car[i][2] == 1:
                    fixed.append(self.car[i])
                    index.append(i)
            without_fixed = [i for i in self.car if i not in fixed]
            without_fixed = sorted(without_fixed, key=lambda x: (-x[1], x[0]))
            for i in range(len(index)):
                without_fixed.insert(index[i],fixed[i])
            self.car = without_fixed
            for i in range(len(self.car)):
                for j in self.area[self.car[i][0]]:
                    self.planning[j].append(self.car[i][0])
            rospy.loginfo("Car : "+str(int(msg[0])+1)+" is added to queue")
            #rospy.loginfo("Current queue : "+str(self.car))
            #rospy.loginfo("Current planning : "+str(self.planning))
    def pose1_call(self,data):
        temp = data.pose.pose.position.x
        self.current_pose[0] = data.pose.pose.position.y
        #rospy.loginfo("Robot1 position: "+str(temp))            
    def pose2_call(self,data):
        temp = data.pose.pose.position.x
        self.current_pose[1] = data.pose.pose.position.y
        #rospy.loginfo("Robot2 position: "+str(temp))
    def pose3_call(self,data):
        temp = data.pose.pose.position.x
        self.current_pose[2] = data.pose.pose.position.y
        #rospy.loginfo("Robot3 position: "+str(temp))
    def __init__(self):
        self.start_blocking = False
        self.car = []
        self.area = {}
        self.planning = [[] for _ in range(3)]
        self.waiting_car = [False for _ in range(3)]
        self.pub = rospy.Publisher('/can_go',String,queue_size=10)
        self.sub = rospy.Subscriber('/can_go_pool',String,self.call)
        self.pose1 = rospy.Subscriber('/robot1/amcl_pose',PoseWithCovarianceStamped,self.pose1_call)
        self.pose2 = rospy.Subscriber('/robot2/amcl_pose',PoseWithCovarianceStamped,self.pose2_call)
        self.pose3 = rospy.Subscriber('/robot3/amcl_pose',PoseWithCovarianceStamped,self.pose3_call)
        
        while not rospy.is_shutdown():
            flag = False
            if self.start_blocking: #keep for wait->queue route
                for minu , car in enumerate(self.car):
                    if car[2] == 1 and self.arrive_queue[car[0]] == False:
                        flag = True
                        """self.arrive_queue[car[0]] = True
                        rospy.sleep(random.randint(1,5))
                        rospy.loginfo("Car : "+str(car[0])+" is goining to collection area. Since no car is blocking")
                        """
                        if abs(self.base_line[car[0]]-self.current_pose[(car[0]+1)%3]) >= 0.5+(0.2*minu) and abs(self.base_line[car[0]]-self.current_pose[(car[0]+2)%3]) >= 0.5+(0.2*minu):
                            rospy.loginfo("Car : "+str(car[0]+1)+" is goining to collection area. Since no car is blocking") 
                            self.arrive_queue[car[0]] = True
                            self.pub.publish(str(car[0]+1)+',-'+str(minu))
                            break
                        else:
                            rospy.loginfo("Car : "+str(car[0]+1)+" need to wait")
                            rospy.sleep(rospy.Duration(0.15))
                if not flag:
                    self.start_blocking = False
            rospy.sleep(rospy.Duration(0.3))
        


if __name__ == '__main__':
    rospy.init_node('blocking')
    Blocking()
