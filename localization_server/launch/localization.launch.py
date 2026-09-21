import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution


def generate_launch_description():
   
    nav2_yaml = os.path.join(get_package_share_directory('localization_server'), 'config', 'amcl_config_sim.yaml')
    file_arg = DeclareLaunchArgument('map_file', default_value='warehouse_map_sim.yaml')
    
    map_file = PathJoinSubstitution([
        get_package_share_directory('map_server'),
        'config',
        LaunchConfiguration('map_file')
    ])



    rviz_config = os.path.join(
            get_package_share_directory('localization_server'),
            'rviz',
            'localization.rviz'
        )


    return LaunchDescription([
        file_arg,
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'use_sim_time': True},
                        {'yaml_filename':map_file}]
        ),
           
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[{'use_sim_time': True},
                        {'autostart': True},
                        {'node_names': ['map_server', 'amcl']}]
        ),
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[nav2_yaml]
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen'
        )
    ])
