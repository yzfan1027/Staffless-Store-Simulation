#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist
import qwiic_scmd
import math
motor_left_ID = 2
motor_right_ID = 1
max_pwm = 160.0
def set_motor_speed(l,r):
    
    left = l 
    right = r 
    
    lbf = 1
    rbf = 1
    
    if left <0:
        lbf = -1
    
    if right <0:
        rbf = -1
        
    speedL = lbf*int(min(max(abs(left * max_pwm), 0) , max_pwm))
    speedR = rbf*int(min(max(abs(right * max_pwm), 0) , max_pwm))
    print("L: ",speedL," R: ",speedR)
    motor_driver.set_drive(motor_left_ID - 1, 0, speedR)
    motor_driver.set_drive(motor_right_ID - 1, 0, speedL)
    motor_driver.enable()

def callback(data):
    
    velocity = data.linear.x
    omega = data.angular.z
    mm2m = math.pow(10, -3)
    print(velocity , " " ,omega)
        
        
    right_wheel = ((2 * velocity) + (omega * 130.0 * mm2m)) / (2 * (31.5) * mm2m)
    left_wheel = ((2 * velocity) - (omega *130.0* mm2m)) / (2 * (31.5) * mm2m)
    right_wheel *= (1 -0.055) * 80 / 60.0 / 5.0 
    left_wheel *= (1   ) * 80 / 60.0 / 5.0

    if velocity != 0.0:
          right_wheel *=0.6
          left_wheel  *=0.6      
    if velocity == 0.0 and omega !=1.0:
        left_wheel *= 1.3
        right_wheel *=1.3
    if velocity == 0.0 and omega ==1.0:
        left_wheel *= 1.7
        right_wheel *=1.7

    if left_wheel <=0.37 and right_wheel<=0.37:
        left_wheel *= 9
        right_wheel *=9
    elif left_wheel <=0.1 and right_wheel<=0.1:
        left_wheel *= 10
        right_wheel *=10
    elif left_wheel <=0.55 and right_wheel<=0.55:
        left_wheel *= 1.8
        right_wheel *=1.8
    if left_wheel <0.0 and right_wheel<0.0:
        left_wheel *= 0.1
        right_wheel *=0.1 

    print("L: ",left_wheel," R: ",right_wheel)
    set_motor_speed(left_wheel,right_wheel)
    
def on_shutdown():
        set_motor_speed(0,0)
        rospy.loginfo("Close.")
        rospy.loginfo(" shutdown.")
        rospy.sleep(1)
        rospy.is_shutdown = True
        
if __name__ == '__main__':
    motor_driver = qwiic_scmd.QwiicScmd()
    motor_driver.disable()
    rospy.init_node('pid_motor_controller', anonymous=True)
    rospy.Subscriber("/robot1/cmd_vel", Twist, callback)
    print("dke")
    rospy.on_shutdown(on_shutdown)
    rospy.spin()
