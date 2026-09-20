#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from drone_interfaces.srv import CheckBattery
from drone_interfaces.action import GoToWaypoint
from functools import partial

class CoordinatorNode(Node): 

    def __init__(self):
        super().__init__('coordinator')
        self.waypoints = [(5.0,5.0),
                          (10.0,0.0),
                          (0.0,10.0),
                          (10.0,10.0)
                          ] 
        self.uav1_waypoint_index_ = 0
        self.uav2_waypoint_index_ = 1
        self.uav1_battery_percent_ = 0.00
        self.uav1_status_ = False  
        self.uav2_battery_percent_ = 0.00
        self.uav2_status_ = False 

        self.uav1_action_client_ = ActionClient(self, GoToWaypoint, "/uav1/reach_target")
        self.uav2_action_client_ = ActionClient(self, GoToWaypoint, "/uav2/reach_target")

        self.start_timer_ = self.create_timer(2.0, self.start_mission)

    def start_mission(self):
        self.start_timer_.cancel()
        
        self.get_logger().info("Starting UAV coordinator")

        self.uav1_check_battery_client()
        self.uav2_check_battery_client()

    def uav1_check_battery_client(self):
        client = self.create_client(CheckBattery, "uav1/check_battery")
        while not client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for server...") 

        request = CheckBattery.Request()

        future = client.call_async(request).add_done_callback(partial(self.callback_check_battery_uav1))

    def callback_check_battery_uav1(self, future):
        try:
            response = future.result()
        except Exception as e:
            self.get_logger().error("Service call failed: %r" % (e,))
            return

        self.uav1_battery_percent_ = response.battery_percent
        self.uav1_status_ = response.ready_for_task

        if self.uav1_status_:
            self.get_logger().info("UAV1 is ready to be sent")
            self.uav1_send_goal(self.waypoints[self.uav1_waypoint_index_][0], self.waypoints[self.uav1_waypoint_index_][1])
        else:
            self.get_logger().warn("Battery is too low!!!")

    def uav2_check_battery_client(self):
        client = self.create_client(CheckBattery, "uav2/check_battery")
        while not client.wait_for_service(1.0):
            self.get_logger().warn("Waiting for server...") 
    
        request = CheckBattery.Request()
    
        future = client.call_async(request).add_done_callback(partial(self.callback_check_battery_uav2))
    
    def callback_check_battery_uav2(self, future):
        try:
            response = future.result()
        except Exception as e:
            self.get_logger().error("Service call failed: %r" % (e,))
            return

        self.uav2_battery_percent_ = response.battery_percent
        self.uav2_status_ = response.ready_for_task

        if self.uav2_status_:
            self.get_logger().info("UAV2 is ready to be sent")
            self.uav2_send_goal(self.waypoints[self.uav2_waypoint_index_][0], self.waypoints[self.uav2_waypoint_index_][1])
        else:
            self.get_logger().warn("Battery is too low!!!")

        
    def uav1_send_goal(self, target_x, target_y):
        self.uav1_action_client_.wait_for_server(1.0)

        goal = GoToWaypoint.Goal()
        goal.target_x = target_x
        goal.target_y = target_y

        self.get_logger().info("Sending goal")

        goal_future = self.uav1_action_client_.send_goal_async(goal)
        goal_future.add_done_callback(self.uav1_goal_response_callback)

    def uav1_goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error("UAV1 goal rejected")
            return

        self.get_logger().info("UAV1 goal accepted")

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.uav1_result_callback)

    def uav1_result_callback(self, future):
        result = future.result().result

        if result.success:
            self.get_logger().info(f'UAV1 reached waypoint ({result.final_x}, {result.final_y})')

            self.uav1_waypoint_index_ += 2
            if self.uav1_waypoint_index_ < len(self.waypoints):
                self.uav1_send_goal(self.waypoints[self.uav1_waypoint_index_][0], self.waypoints[self.uav1_waypoint_index_][1])
            else:
                self.get_logger().info("UAV1 completed all waypoints")
        else:
            self.get_logger().error("UAV1 failed to reach waypoint")

    def uav2_send_goal(self, target_x, target_y):
        self.uav2_action_client_.wait_for_server(1.0)
        
        goal = GoToWaypoint.Goal()
        goal.target_x = target_x
        goal.target_y = target_y
        
        self.get_logger().info("Sending goal")

        goal_future = self.uav2_action_client_.send_goal_async(goal)
        goal_future.add_done_callback(self.uav2_goal_response_callback)   

    def uav2_goal_response_callback(self, future):
        goal_handle = future.result()
    
        if not goal_handle.accepted:
            self.get_logger().error("UAV2 goal rejected")
            return
    
        self.get_logger().info("UAV2 goal accepted")
    
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.uav2_result_callback)
    
    def uav2_result_callback(self, future):
        result = future.result().result
    
        if result.success:
            self.get_logger().info(f'UAV2 reached waypoint ({result.final_x}, {result.final_y})')
    
            self.uav2_waypoint_index_ += 2
            if self.uav2_waypoint_index_ < len(self.waypoints):
                self.uav2_send_goal(self.waypoints[self.uav2_waypoint_index_][0], self.waypoints[self.uav2_waypoint_index_][1])
            else:
                self.get_logger().info("UAV2 completed all waypoints")
        else:
            self.get_logger().error("UAV2 failed to reach waypoint")

def main(args=None):
    rclpy.init(args=args)
    node = CoordinatorNode() 
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()