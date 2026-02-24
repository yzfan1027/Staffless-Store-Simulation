
(cl:in-package :asdf)

(defsystem "jetbot_msgs-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils :std_msgs-msg
)
  :components ((:file "_package")
    (:file "BoolStamped" :depends-on ("_package_BoolStamped"))
    (:file "_package_BoolStamped" :depends-on ("_package"))
    (:file "Twist2DStamped" :depends-on ("_package_Twist2DStamped"))
    (:file "_package_Twist2DStamped" :depends-on ("_package"))
    (:file "WheelsCmd" :depends-on ("_package_WheelsCmd"))
    (:file "_package_WheelsCmd" :depends-on ("_package"))
  ))