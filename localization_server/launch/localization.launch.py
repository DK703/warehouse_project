import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.substitutions import FindPackageShare
from launch_ros.descriptions import ParameterValue

def generate_launch_description():

    file_arg = DeclareLaunchArgument('map_file', default_value='warehouse_map_keepout_sim.yaml')
    map_file_cfg = LaunchConfiguration('map_file')

   
    bool_checker = PythonExpression(["'", map_file_cfg, "' == 'warehouse_map_keepout_sim.yaml'"])
    proper_time_arg = ParameterValue(bool_checker, value_type=bool)



    map_file = PathJoinSubstitution([
        get_package_share_directory('map_server'),
        'config',
        "warehouse_map_sim.yaml"
    ])


    path_pkg_share_localization = FindPackageShare("localization_server")
    path_config_dir_localization = PathJoinSubstitution([path_pkg_share_localization, 'config'])


    nav2_yaml = PathJoinSubstitution([path_config_dir_localization, PythonExpression(["'amcl_config_sim.yaml' if (", bool_checker, ") else 'amcl_config_real.yaml'"])])

    rviz_config = os.path.join(
        get_package_share_directory('localization_server'),
        'rviz',
        'localization.rviz'
    )

    nav2_map_node = Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'use_sim_time': proper_time_arg},
                        {'yaml_filename': map_file}]
        )
    nav2_amcl_node = Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[nav2_yaml, {'use_sim_time': proper_time_arg}]
        )

    nav2_lifecycle_manager_node = Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[{'use_sim_time': proper_time_arg},
                        {'autostart': True},
                        {'node_names': ['map_server', 'amcl']}]
        )

    rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen'
        )

    return LaunchDescription([file_arg, nav2_map_node, nav2_amcl_node, nav2_lifecycle_manager_node])