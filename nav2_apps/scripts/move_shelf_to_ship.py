#! /usr/bin/env python3
# Copyright 2021 Samsung Research America
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import math
import time
from geometry_msgs.msg import Twist
from copy import deepcopy

from geometry_msgs.msg import PoseStamped
from rclpy.duration import Duration
import rclpy

from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from std_msgs.msg import String

from rclpy.parameter import Parameter
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
from nav2_apps.change_footprint import Change_Footprint
from rclpy.parameter import Parameter as RosParameter
'''
Basic security route patrol demo. In this demonstration, the expectation
is that there are security cameras mounted on the robots recording or being
watched live by security staff.
'''

'''
# Shelf positions for picking
shelf_positions = {
    "shelf_A": [-3.829, -7.604],
    "shelf_B": [-3.791, -3.287],
    "shelf_C": [-3.791, 1.254],
    "shelf_D": [-3.24, 5.861]}

# Shipping destination for picked products
shipping_destinations = {
    "recycling": [-0.205, 7.403],
    "pallet_jack7": [-0.073, -8.497],
    "conveyer_432": [6.217, 2.153],
    "frieght_bay_3": [-6.349, 9.147]}

'''

#i dont know if I need multiple shipping and multiple loading positions, this is just for future-proofing

shipping_positions = {
    "ship_A": [2.10,0.98]
}

loading_positions = {
    "load_A": [6.5,-0.45]
}




def spin_robot(publisher, angle, speed=0.55):
    
    cmd = Twist()
    cmd.linear.x = 0.0
    cmd.angular.z = speed if angle > 0 else -speed
    
    duration = abs(angle) / speed
    start = time.time()
    
    while time.time() - start < duration:
        publisher.publish(cmd)
        time.sleep(0.1)
    
    
    cmd.angular.z = 0.0
    publisher.publish(cmd)

def move_forward(publisher, speed=0.5):
    cmd = Twist()
    cmd.linear.x = 0.0
    duration = 4.8
    start = time.time()
    cmd.linear.x = speed

    while time.time() - start < duration:
        publisher.publish(cmd)
        time.sleep(0.1)
    cmd.linear.x = 0.0
    publisher.publish(cmd)





def main():

    '''
    request_item_location = 'shelf_C'
    request_destination = 'pallet_jack7'
    
    '''
    rclpy.init()

    navigator = BasicNavigator()
    #temp fix
    navigator.set_parameters([RosParameter('use_sim_time', RosParameter.Type.BOOL, True)])
    
    cmd_vel_pub = navigator.create_publisher(Twist, '/cmd_vel', 10)
    elevator_up_publisher = navigator.create_publisher(String, '/elevator_up', 10)

    # Set your demo's initial pose
    initial_pose = PoseStamped()
    initial_pose.header.frame_id = 'map'
    initial_pose.header.stamp = navigator.get_clock().now().to_msg()
    initial_pose.pose.position.x = 0.01
    initial_pose.pose.position.y = 0.13
    initial_pose.pose.orientation.z = 0.0
    initial_pose.pose.orientation.w = 1.0
    navigator.setInitialPose(initial_pose)


    # Wait for navigation to activate fully
    navigator.waitUntilNav2Active()


    loading_pose = PoseStamped()
    loading_pose.header.frame_id = 'map'
    loading_pose.header.stamp = navigator.get_clock().now().to_msg()
    loading_pose.pose.position.x = loading_positions["load_A"][0]
    loading_pose.pose.position.y = loading_positions["load_A"][1]
    loading_pose.pose.orientation.z = 0.0
    loading_pose.pose.orientation.w = 1.0
    print('moving to loading zone ')
    navigator.goToPose(loading_pose)

    i = 0
    while not navigator.isTaskComplete():
        i = i + 1
        feedback = navigator.getFeedback()
        if feedback and i % 5 == 0:
            print('Estimated time of arrival at' + '{0:.0f}'.format(
                      Duration.from_msg(feedback.estimated_time_remaining).nanoseconds / 1e9)
                  + ' seconds.')

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('success')
        spin_robot(cmd_vel_pub, -((math.pi / 2)+0.3))
        move_forward(cmd_vel_pub)
    elif result == TaskResult.CANCELED:
        print('Task was canceled. Returning to staging point...')
        initial_pose.header.stamp = navigator.get_clock().now().to_msg()
        navigator.goToPose(initial_pose)
    elif result == TaskResult.FAILED:
        print('Task failed!, ink bomb explosion noised')
        exit(-1)
    while not navigator.isTaskComplete():
        pass
    
    #begin moving to shipping
    print('print amcl')
    time.sleep(3)



    msg = String()
    msg.data = ''  # empty string to trigger elevator
    elevator_up_publisher.publish(msg)
    elevator_up_publisher.publish(msg)
    elevator_up_publisher.publish(msg)
    large_footprint = '[[0.45,0.45], [0.45, -0.45], [-0.45, -0.45], [-0.45,0.45]]'
    #change_footprint(navigator, large_footprint)
    print('print amcl')
    time.sleep(3)
    footprint_node = Change_Footprint()
    ok = footprint_node.send_request(large_footprint)
    if not ok:
        print('footprint change failed')



    time.sleep(2)  
    navigator.clearAllCostmaps()
    print('print amcl')
    time.sleep(2)

    


    shipping_pose = PoseStamped()
    shipping_pose.header.frame_id = 'map'
    shipping_pose.header.stamp = navigator.get_clock().now().to_msg()
    shipping_pose.pose.position.x = shipping_positions["ship_A"][0]
    shipping_pose.pose.position.y = shipping_positions["ship_A"][1]
    shipping_pose.pose.orientation.z = 0.0
    shipping_pose.pose.orientation.w = 1.0

    navigator.goToPose(shipping_pose)

    i = 0
    while not navigator.isTaskComplete():
        i = i + 1
        feedback = navigator.getFeedback()
        if feedback and i % 5 == 0:
            print('Estimated time of arrival at' + '{0:.0f}'.format(
                      Duration.from_msg(feedback.estimated_time_remaining).nanoseconds / 1e9)
                  + ' seconds.')

    
    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('success')
        #spin_robot(cmd_vel_pub, -((math.pi / 2)+0.3))
        #move_forward(cmd_vel_pub)
    elif result == TaskResult.CANCELED:
        print('Task was canceled. Returning to staging point...')
        initial_pose.header.stamp = navigator.get_clock().now().to_msg()
        navigator.goToPose(initial_pose)
    elif result == TaskResult.FAILED:
        print('Task failed!, ink bomb explosion noised')
        exit(-1)
    while not navigator.isTaskComplete():
        pass 
    
    exit(0)



    



    


if __name__ == '__main__':
    main()