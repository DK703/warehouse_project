import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():



    rviz_config = os.path.join(
        get_package_share_directory('cartographer_slam'),
        'rviz',
        'cartographer.rviz'
    )
    cartographer_config_dir = os.path.join(
    get_package_share_directory('cartographer_slam'), 'config')

    time_arg = DeclareLaunchArgument('use_sim_time', default_value='True')
    #cartographer_real.lua  cartographer.lua
    configuration_basename = "cartographer_real.lua"

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        arguments=['-d', rviz_config]
    )

    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        arguments=['-configuration_directory', cartographer_config_dir,
                   '-configuration_basename', configuration_basename]
    )

    occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        output='screen',
        name='occupancy_grid_node',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        arguments=['-resolution', '0.05', '-publish_period_sec', '1.0'])

    return LaunchDescription([time_arg, cartographer_node, occupancy_grid_node, rviz_node])