#!/usr/bin/env python
import rospy

#program for navigating car to determined position
import actionlib
from std_msgs.msg import String
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from actionlib_msgs.msg import GoalStatus
from geometry_msgs.msg import Pose, Point, Quaternion
from tf.transformations import quaternion_from_euler
import argparse
import random
class MoveBaseSeq():
    def call(self,data):
        msg = data.data.split(',')
        if msg[0] == self.name and len(msg) == 2:
            self.go_ahead = True
            self.minus_or_state = int(msg[1])
        elif msg[1] == '1' and msg[0] == 'robot'+self.name:
            self.go_ahead = True
            

    def __init__(self,route,name,item,priority):
        self.go_ahead = False
        self.minus_or_state = 0
        self.item = item
        rospy.init_node('move_base_sequence_'+name)
        self.name = str(int(name)+1)
        self.pose_seq = list()
        self.route = route
        self.goal_cnt = 0
        self.priority = priority
        self.minus_constant = 0.45
        self.pub = rospy.Publisher('/can_go_pool',String,queue_size=10)
        self.sub = rospy.Subscriber('/can_go',String,self.call)
        self.cam_pub = rospy.Publisher('/robot'+self.name+'/arrive',String,queue_size=10)
        self.cam_sub = rospy.Subscriber('/robot'+self.name+'/next_action',String,self.call)
        #Create action client
        for r in self.route: #change route to Pose information in order to use navigation
            temp = Pose(Point(r[0],r[1],0.0),Quaternion(0.0,0.0,r[2],r[3]))
            self.pose_seq.append(temp)
        self.client = actionlib.SimpleActionClient('/robot'+self.name+'/move_base',MoveBaseAction)
        rospy.loginfo("Waiting for move_base action server...")
        wait = self.client.wait_for_server()
        while not wait:
            pass
        rospy.loginfo("Connected to move base server")
        rospy.loginfo("Starting goals achievements ...")
        self.movebase_client()
    
    def movebase_client(self):
        try:
            collection_area_forward = False
            previous = '-1'
            for i in range(len(self.pose_seq)):
                goal = MoveBaseGoal()
                goal.target_pose.header.frame_id = "map"
                goal.target_pose.header.stamp = rospy.Time.now() 
                goal.target_pose.pose = self.pose_seq[self.goal_cnt]
                rospy.loginfo("Car "+self.name+" Sending goal pose "+str(self.goal_cnt+1)+" to Action Server")
                rospy.loginfo(str(self.pose_seq[self.goal_cnt]))
                self.client.send_goal(goal)
                rospy.sleep(random.randint(1,5))
                wait = self.client.wait_for_result()
                current_state = self.client.get_state()
                
                if not wait:
                    rospy.logerr("Action server not available!")
                    rospy.signal_shutdown("Action server not available!")
                    #error detect 
                    return None
                elif current_state == GoalStatus.SUCCEEDED: #if goal is reached
                    
                    self.goal_cnt += 1
                    rospy.loginfo("Car "+self.name+" Goal pose "+str(self.goal_cnt)+" reached")
                    if self.go_ahead:  #car discharges the item
                        rospy.loginfo("Car "+self.name+" is Discharging at "+previous)
                        self.go_ahead = False
                        rospy.sleep(1)
                    
                    #pak.launchMerchant(self.item)

                    if self.goal_cnt == len(self.pose_seq):
                        rospy.loginfo("Car "+self.name+"All goals reached!")
                        rospy.signal_shutdown("Car "+self.name+"All goals reached!")
                        return 3
                    elif self.item[self.goal_cnt] == 'wait':  # is going to waiting place
                        rospy.loginfo("Car "+self.name+" is taking item : "+self.item[self.goal_cnt-1])
                        
                        self.cam_pub.publish("1,"+self.item[self.goal_cnt-1]) #state,item_id
                        while not self.go_ahead:
                            rospy.sleep(2)
                        self.go_ahead = False
                        self.pub.publish(self.name+",t") #car_id,item_id,taking
                        rospy.sleep(0.1)
                        msg = self.name+","+str(self.priority)+',p'
                        for i in range(self.goal_cnt+2,len(self.pose_seq)-1):
                            msg += ","+self.item[i]
                        self.pub.publish(msg)   # car_id,priority,item_collection_areas
                        rospy.loginfo("Car "+self.name+" Forwarding to waiting area")
                    elif self.item[self.goal_cnt] == 'queue':  # is going to park place
                        self.pub.publish(self.name+",l")  #lock the queue area
                        while not self.go_ahead:
                            rospy.loginfo("Car "+self.name+" Waiting for the block")
                            rospy.sleep(random.random()*2.0)
                        self.go_ahead = False
                        rospy.loginfo("Car "+self.name+" need to minus : "+str(self.minus_or_state))
                        self.pose_seq[self.goal_cnt].position.y += self.minus_or_state*self.minus_constant   # make the car wait in a queue
                        rospy.loginfo("Car "+self.name+" is Queueing")
                        collection_area_forward = True

                    elif self.goal_cnt == len(self.pose_seq)-1:   # is going to initial place
                        self.pub.publish(self.name+","+previous+",1") # for last collection area
                        rospy.loginfo("Car "+self.name+" collecting area reached")
                        #pak.carArrived(self.name)
                        rospy.sleep(0.1)
                        self.pub.publish(self.name+",f") #car_id,fin
                    elif collection_area_forward:  # can enter the collection area
                        while not self.go_ahead:
                            self.pub.publish(self.name+","+self.item[self.goal_cnt]+",0") #car_id,item_id,not_fin
                            rospy.loginfo("Car "+self.name+" Waiting for the block")
                            rospy.sleep(random.random()*2.0)
                        
                        if previous != '-1': # is now in one of the collection area
                                             # need to release the previous one
                            self.pub.publish(self.name+","+previous+",1") #car_id,item_id,fin
                        previous = self.item[self.goal_cnt]
                    else:
                        rospy.loginfo("Car "+self.name+" is taking item : "+self.item[self.goal_cnt-1])
                        
                        self.cam_pub.publish("1,"+self.item[self.goal_cnt-1]) #state,item_id
                        while not self.go_ahead:
                            rospy.sleep(2)
                        self.go_ahead = False
                        """"""
                        self.pub.publish(self.name+",t") #car_id,item_id,taking

                elif current_state == GoalStatus.ABORTED:  #if goal is rejected

                    rospy.logerr("Goal pose "+str(self.goal_cnt)+" rejected")
                    return -1


        except rospy.ROSInterruptException:
            rospy.logerr("Ctrl-C caught. Quitting")

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser() #parameters  are passed by main.py for navigation
        parser.add_argument('-p1',nargs="+",type=float) #position
        parser.add_argument('-p2',nargs="+",type=float)
        parser.add_argument('-p3',nargs="+",type=float)
        parser.add_argument('-p4',nargs="+",type=float)
        parser.add_argument('-p5',nargs="+",type=float)
        parser.add_argument('-p6',nargs="+",type=float)
        parser.add_argument('-p7',nargs="+",type=float)
        parser.add_argument('-p8',nargs="+",type=float)
        parser.add_argument('-p9',nargs="+",type=float)
        parser.add_argument('-p10',nargs="+",type=float)
        parser.add_argument('-pname',type=str)  #car id
        parser.add_argument('-pdata',nargs="+",type=str) #desired item
        parser.add_argument('-pri',type=int) #priority
        args = parser.parse_args()
        temp = list() #list of arg value
        i = 0
        for arg in sorted(vars(args)):
            i+=1
            if i == 10:
                break
            if getattr(args,arg) is not None:
                temp.append(getattr(args,arg))
        MoveBaseSeq(temp,args.pname,args.pdata,args.pri)
    except rospy.ROSInterruptException:
        rospy.loginfo("Navigation finished.")
