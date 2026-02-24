;; Auto-generated. Do not edit!


(when (boundp 'jetbot_msgs::SetValue)
  (if (not (find-package "JETBOT_MSGS"))
    (make-package "JETBOT_MSGS"))
  (shadow 'SetValue (find-package "JETBOT_MSGS")))
(unless (find-package "JETBOT_MSGS::SETVALUE")
  (make-package "JETBOT_MSGS::SETVALUE"))
(unless (find-package "JETBOT_MSGS::SETVALUEREQUEST")
  (make-package "JETBOT_MSGS::SETVALUEREQUEST"))
(unless (find-package "JETBOT_MSGS::SETVALUERESPONSE")
  (make-package "JETBOT_MSGS::SETVALUERESPONSE"))

(in-package "ROS")





(defclass jetbot_msgs::SetValueRequest
  :super ros::object
  :slots (_value ))

(defmethod jetbot_msgs::SetValueRequest
  (:init
   (&key
    ((:value __value) 0.0)
    )
   (send-super :init)
   (setq _value (float __value))
   self)
  (:value
   (&optional __value)
   (if __value (setq _value __value)) _value)
  (:serialization-length
   ()
   (+
    ;; float32 _value
    4
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; float32 _value
       (sys::poke _value (send s :buffer) (send s :count) :float) (incf (stream-count s) 4)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; float32 _value
     (setq _value (sys::peek buf ptr- :float)) (incf ptr- 4)
   ;;
   self)
  )

(defclass jetbot_msgs::SetValueResponse
  :super ros::object
  :slots ())

(defmethod jetbot_msgs::SetValueResponse
  (:init
   (&key
    )
   (send-super :init)
   self)
  (:serialization-length
   ()
   (+
    0
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;;
   self)
  )

(defclass jetbot_msgs::SetValue
  :super ros::object
  :slots ())

(setf (get jetbot_msgs::SetValue :md5sum-) "0aca93dcf6d857f0e5a0dc6be1eaa9fb")
(setf (get jetbot_msgs::SetValue :datatype-) "jetbot_msgs/SetValue")
(setf (get jetbot_msgs::SetValue :request) jetbot_msgs::SetValueRequest)
(setf (get jetbot_msgs::SetValue :response) jetbot_msgs::SetValueResponse)

(defmethod jetbot_msgs::SetValueRequest
  (:response () (instance jetbot_msgs::SetValueResponse :init)))

(setf (get jetbot_msgs::SetValueRequest :md5sum-) "0aca93dcf6d857f0e5a0dc6be1eaa9fb")
(setf (get jetbot_msgs::SetValueRequest :datatype-) "jetbot_msgs/SetValueRequest")
(setf (get jetbot_msgs::SetValueRequest :definition-)
      "float32 value
---
")

(setf (get jetbot_msgs::SetValueResponse :md5sum-) "0aca93dcf6d857f0e5a0dc6be1eaa9fb")
(setf (get jetbot_msgs::SetValueResponse :datatype-) "jetbot_msgs/SetValueResponse")
(setf (get jetbot_msgs::SetValueResponse :definition-)
      "float32 value
---
")



(provide :jetbot_msgs/SetValue "0aca93dcf6d857f0e5a0dc6be1eaa9fb")


