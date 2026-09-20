#!/usr/bin/env python3
import rclpy
import time
from rclpy.node import Node
from drone_interfaces.msg import UavStatus

class SafetyMonitor(Node): # MODIFY node name

    def __init__(self):
        super().__init__('safety_monitor')
        self.uav1_x_ = 0.00
        self.uav1_y_ = 0.00
        self.uav2_x_ = 0.00
        self.uav2_y_ = 0.00
        self.uav1_subscriber_ = self.create_subscription(UavStatus, "/uav1/status", self.uav1_callback, 10)
        self.uav2_subscriber_ = self.create_subscription(UavStatus, "/uav2/status", self.uav2_callback, 10)
        self.timer_ = self.create_timer(1.0, self.safe_distance)

    def uav1_callback(self, msg: UavStatus):
        self.uav1_x_= msg.x
        self.uav1_y_ = msg.y

    def uav2_callback(self, msg: UavStatus):
        self.uav2_x_= msg.x
        self.uav2_y_ = msg.y    

    def safe_distance(self):
        d = ((self.uav1_x_ - self.uav2_x_)**2 + (self.uav1_y_ - self.uav2_y_)**2)**0.5

        if d < 3.0:
            self.get_logger().warn(f"UAVs too close! \n Distance: {d}")

def main(args=None):
    rclpy.init(args=args)
    #My node
    node = SafetyMonitor() # MODIFY node name
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()