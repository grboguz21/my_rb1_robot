#!/usr/bin/env python

import rospy
import math
import tf
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from my_rb1_ros.srv import Rotate, RotateResponse

class RotateServiceServer:
    def __init__(self):

        rospy.init_node('rotate_service_server')

        self.service = rospy.Service('/rotate_robot', Rotate, self.rotate_robot)

        self.vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.odom_sub = rospy.Subscriber('/odom', Odometry, self.odom_callback)

        self.current_yaw = 0.0


        rospy.loginfo("Service Ready")


    def odom_callback(self, msg):
        orientation_q = msg.pose.pose.orientation
        _, _, yaw = tf.transformations.euler_from_quaternion(
            [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w])
        self.current_yaw = yaw  


    def rotate_robot(self, request):
        rospy.loginfo("Service Requested")
        # rospy.loginfo(f"Received rotation request: {request.degrees} degrees!")

        target_angle = math.radians(request.degrees)
        start_yaw = self.current_yaw

        twist_msg = Twist()
        angular_speed = 0.5 

        # turn left or right
        if target_angle > 0:
            twist_msg.angular.z = angular_speed
        else:
            twist_msg.angular.z = -angular_speed

        rate = rospy.Rate(10) 


        while not rospy.is_shutdown():
            current_angle = self.current_yaw - start_yaw

            if abs(current_angle) >= abs(target_angle):
                break

            self.vel_pub.publish(twist_msg)
            rate.sleep()


        twist_msg.angular.z = 0
        self.vel_pub.publish(twist_msg)

        rospy.loginfo("Service Completed")
        # return RotateResponse(f"Rotation of {request.degrees} degrees completed successfully.")
        return RotateResponse("Service Completed")

if __name__ == "__main__":
    server = RotateServiceServer()
    rospy.spin()
