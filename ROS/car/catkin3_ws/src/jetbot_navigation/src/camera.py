#!/usr/bin/env python3

import torch
import cv2
import numpy as np
import rospy
from std_msgs.msg import String
import pandas as pd
import time
import matplotlib as np
flag = False
result = 0
ROBOT = 'robot1'
np.use('Agg')
def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=640,
    display_height=640,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), format=NV12, width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


model = torch.hub.load('yolov5-python3.6.9-jetson','custom','yolov5-python3.6.9-jetson/best.pt',source="local")
model.cuda()
#model.conf = 0.55
camera = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)

def call(data):
	#Yolo detect
	global flag,result,model,camera
	rospy.loginfo(data.data)
	detail = data.data.split(',')
	name = detail[1]
	stats = detail[0]
	result = 1
	count = 0
	if stats == '1':  # 1-> success

		detected = False
		while not detected:
			ret,img = camera.read()#imgs[count]
			results = model(img)
			df = results.pandas().xyxy[0]
			detects = df.values.tolist()
			print(detects)
			for detect in detects:
				if detect[6] == name:
					results.show()
					rospy.loginfo('item detected')
					detected = True
					break
			
	time.sleep(5)
	flag = True

def talker():
    global flag,result
    print("first pass")
    pub = rospy.Publisher(f'/{ROBOT}/next_action',String,queue_size=10)
    sub = rospy.Subscriber(f'/{ROBOT}/arrive',String,call)
    rospy.init_node(f'{ROBOT}_camera')
    rate = rospy.Rate(5)
    while not rospy.is_shutdown():
        if flag:
            s = ROBOT+','+str(result) #J1 finish result-1 , and willing to get result's item
            rospy.loginfo(s)
            pub.publish(s)
            flag = False
        rate.sleep()
    camera.release()
if __name__=='__main__':
	try:
		talker()
	except rospy.ROSInterruptException:
		pass
