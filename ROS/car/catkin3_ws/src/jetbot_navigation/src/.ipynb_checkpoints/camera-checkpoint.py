#!/usr/bin/env python3

import torch
import cv2
from jetbot import Camera
import numpy as np
import rospy
from std_msgs.msg import String
import pandas as pd
import time
flag = False
result = 0
ROBOT = 'robot2'
def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=640,
    display_height=640,
    framerate=21,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


#model = torch.hub.load('yolov5-python3.6.9-jetson','custom','yolov5-python3.6.9-jetson/best.pt',source="local",autoshape=True)
#model.cuda()
#model.conf = 0.55
#camera = Camera.instance(width=640, height=640,capture_width=640,capture_height=640)
camera = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)
#imgs = [cv2.imread(f'./{i}.jpeg') for i in range(2,4)]
#imgs = [cv2.resize(img,(224,224)) for img in imgs]
def call(data):
	#Yolo detect
    global flag,result,model,camera
    rospy.loginfo(data.data)
    detail = data.data.split(',')
    name = detail[1]
    stats = detail[0]
    result += 1
    count = 0
    if stats == '1':  # 1-> success

        detected = False
        while not detected:
            img = camera.value#imgs[count]
            results = model(img,size=224)
            df = results.pandas().xyxy[0]
            detects = df.values.tolist()
            print(detects)
            for detect in detects:
                if detect[6] == name:
                    results.show()
                    rospy.loginfo('item detected')
                    detected = True
            time.sleep(1)
            count += 1
            if count == 2:
                print('no item detected')
                break
                    
    elif stats == '2':
        cv2.namedWindow("hi", cv2.WINDOW_AUTOSIZE)
        while True:
            ret,img = camera.read()
            print("if none : ",img)
            cv2.imshow("hi",img)
            key = cv2.waitKey(90)
            if key == ord('q'):
                break
        cv2.destroyAllWindows()
        result = 0
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