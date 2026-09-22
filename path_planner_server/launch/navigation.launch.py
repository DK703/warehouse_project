import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

def generate_launch_description():

    time_arg = DeclareLaunchArgument('use_sim_time', default_value='True')

    time_arg_cfg = LaunchConfiguration('use_sim_time')

    

    rviz_config = os.path.join(
            get_package_share_directory('path_planner_server'),
            'rviz',
            'navigation.rviz'
        )
    controller_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'controller_sim.yaml')
    bt_navigator_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'bt_navigator_sim.yaml')
    planner_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'planner_sim.yaml')
    recovery_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'recoveries_sim.yaml')
   
   
    nav2_yaml = os.path.join(get_package_share_directory('localization_server'), 'config', 'amcl_config_sim.yaml')
    map_file = os.path.join(get_package_share_directory('map_server'), 'config', 'warehouse_map_sim.yaml')

    #file_arg = DeclareLaunchArgument('map_file', default_value='warehouse_map_sim.yaml')

    

    map_server_node = Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'use_sim_time': True}, 
                        {'yaml_filename': map_file} 
                       ])
    nav2_amcl_node = Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[nav2_yaml]
        )

    #path planner stuff
    controller_node = Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[controller_yaml])
    nav2_planner_node = Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[planner_yaml])
    behavior_node = Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='recoveries_server',
            parameters=[recovery_yaml],
            output='screen')
    nav2_bt_navigator_node = Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[bt_navigator_yaml])
    nav2_lifecycle_manager_node = Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_pathplanner',
            output='screen',
            parameters=[{'autostart': True},
                        {'node_names': ['map_server',
                                        'amcl',
                                        'planner_server',
                                        'controller_server',
                                        'recoveries_server',
                                        'bt_navigator']}])
    rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen'
        )


   
    return LaunchDescription([time_arg, map_server_node, nav2_amcl_node, controller_node, nav2_planner_node,behavior_node, nav2_bt_navigator_node, nav2_lifecycle_manager_node, rviz_node])
