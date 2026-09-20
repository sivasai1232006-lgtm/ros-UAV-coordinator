from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction


def generate_launch_description():

    uav1 = Node(
        package='drone_controller',
        executable='uav1_node',
        name='uav1',
        output='screen'
    )

    uav2 = Node(
        package='drone_controller',
        executable='uav2_node',
        name='uav2',
        output='screen'
    )

    safety_monitor = Node(
        package='drone_controller',
        executable='safety_monitor',
        name='safety_monitor',
        output='screen'
    )

    coordinator = Node(
        package='drone_controller',
        executable='coordinator',
        name='coordinator',
        output='screen'
    )

    delayed_coordinator = TimerAction(
        period=2.0,
        actions=[coordinator]
    )

    return LaunchDescription([
        uav1,
        uav2,
        safety_monitor,
        delayed_coordinator
    ])