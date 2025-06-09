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

        self.current_yaw = 0.0
        self.last_yaw = None

        self.odom_sub = rospy.Subscriber('/odom', Odometry, self.odom_callback)
        self.vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        self.service = rospy.Service('/rotate_robot', Rotate, self.rotate_robot)
        rospy.loginfo("Service Ready")

    def odom_callback(self, msg):
        orientation_q = msg.pose.pose.orientation
        _, _, yaw = tf.transformations.euler_from_quaternion([
            orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w
        ])
        self.current_yaw = yaw

    def normalize_angle(self, angle):
        """Keep angle in [-pi, pi]"""
        return math.atan2(math.sin(angle), math.cos(angle))

    def rotate_robot(self, request):
        rospy.loginfo(f"Service Requested: Rotate {request.degrees} degrees")

        target_angle_rad = math.radians(request.degrees)
        direction = -1 if target_angle_rad > 0 else 1

        fast_speed = 4.0
        slow_speed = 2.0

        twist = Twist()
        rate = rospy.Rate(50)

        turned_angle = 0.0
        self.last_yaw = self.current_yaw

        while not rospy.is_shutdown():
            delta = self.normalize_angle(self.current_yaw - self.last_yaw)
            turned_angle += delta
            self.last_yaw = self.current_yaw

            progress = abs(turned_angle) / abs(target_angle_rad)
            remaining_deg = math.degrees(abs(target_angle_rad) - abs(turned_angle))
            rospy.loginfo_throttle(0.2, f"Remaining: {remaining_deg:.2f}°")

            if progress >= 1.0:
                break

            if progress < 0.8:
                twist.angular.z = direction * fast_speed
            else:
                twist.angular.z = direction * slow_speed

            self.vel_pub.publish(twist)
            rate.sleep()

        twist.angular.z = 0.0
        self.vel_pub.publish(twist)

        rospy.loginfo(f"Rotation Completed: turned {math.degrees(turned_angle):.2f}°")
        return RotateResponse(f"Requested: {request.degrees} deg, Rotated: {math.degrees(turned_angle):.2f} deg")


if __name__ == "__main__":
    try:
        server = RotateServiceServer()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
