#!/usr/bin/env python3
import rclpy
import time
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse
from rclpy.action.server import ServerGoalHandle
from drone_interfaces.msg import UavStatus
from drone_interfaces.srv import CheckBattery
from drone_interfaces.action import GoToWaypoint

class UAV1Node(Node): # MODIFY node name

    def __init__(self):
        super().__init__('uav1')
        self.x_ = 0.00
        self.y_ = 0.00
        self.battery_ = 100.00
        self.state_ = "IDLE"
        self.status_pub_ = self.create_publisher(UavStatus, "/uav1/status", 10)
        self.check_battery_server_ = self.create_service(CheckBattery, 'uav1/check_battery', self.check_battery_callback)
        self.action_server_ = ActionServer(self, 
                                           GoToWaypoint, 
                                           "/uav1/reach_target", 
                                           execute_callback=self.reach_target_callback,
                                           goal_callback=self.goalrequest_callback)
        self.get_logger().info("Node has been started")

    def send_status_callback(self):
        msg = UavStatus()
        msg.x = self.x_
        msg.y = self.y_
        msg.battery_percent = self.battery_
        msg.state = self.state_
        self.status_pub_.publish(msg)

    def check_battery_callback(self, request, response):
        response = CheckBattery.Response()
        response.battery_percent = self.battery_
        if self.battery_ >= 20:
            response.ready_for_task = True
        else:
            response.ready_for_task = False

        return response

    def reach_target_callback(self, goal_handle: ServerGoalHandle):
        # Receive goal
        target_x =  goal_handle.request.target_x
        target_y = goal_handle.request.target_y

        #Execute the action
        self.get_logger().info("Executing the goal")

        current_x = self.x_
        current_y = self.y_

        feedback_msg = GoToWaypoint.Feedback()
        feedback_msg.position = [current_x, current_y]
        percent = 0

        dx = target_x - current_x
        dy = target_y - current_y
        d = (dx**2 + dy**2)**0.5

        step_size = 1.0

        while d > 0:
            dx = target_x - current_x
            dy = target_y - current_y
            d = (dx**2 + dy**2)**0.5

            if d < 1e-6:
                break

            if d <= step_size:
                current_x = target_x
                current_y = target_y
            else:
                step_x = (dx/d) * step_size
                step_y = (dy/d) * step_size

                current_x += step_x
                current_y += step_y
                if (target_x - current_x) < step_size:
                    current_x = target_x
                if (target_y - current_y) < step_size:
                   current_y = target_y

            self.x_ = current_x
            self.y_ = current_y
            self.state_ = "EN_ROUTE"
            self.send_status_callback()

            current_dist = ((target_x - current_x)**2 + (target_y - current_y)**2)**0.5
            percent = (1-(current_dist/d))*100

            feedback_msg.position = [current_x, current_y]
            feedback_msg.percent_complete = percent

            goal_handle.publish_feedback(feedback_msg)

            self.get_logger().info(f'Current Position: ({current_x}, {current_y}), Percent Complete: {percent}%')

            if current_x == target_x and current_y == target_y:
                break

            time.sleep(1)

        self.state_ = "ARRIVED"
        self.battery_ = self.battery_ - 20
        self.send_status_callback()

        #Set state as success
        goal_handle.succeed()

        result = GoToWaypoint.Result()
        result.final_x = feedback_msg.position[0]
        result.final_y = feedback_msg.position[1]
        result.success = True
        return result


    def goalrequest_callback(self, goal_request):
        self.get_logger().info(
            f'Received goal: ({goal_request.target_x} and {goal_request.target_y})'
        )

        return GoalResponse.ACCEPT

               

def main(args=None):
    rclpy.init(args=args)
    #My node
    node = UAV1Node() # MODIFY node name
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()