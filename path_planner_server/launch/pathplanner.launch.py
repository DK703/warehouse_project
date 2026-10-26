import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.substitutions import FindPackageShare
from launch_ros.descriptions import ParameterValue

def generate_launch_description():

    filters_yaml = os.path.join(get_package_share_directory(
        'path_planner_server'), 'config', 'filters.yaml')

    
    time_arg = DeclareLaunchArgument('use_sim_time', default_value='True')

    time_arg_cfg = LaunchConfiguration('use_sim_time')

    bool_checker = PythonExpression(["'", time_arg_cfg, "' == 'True'" ])
    proper_time_arg = ParameterValue(bool_checker, value_type = bool)

    rviz_config = os.path.join(
            get_package_share_directory('path_planner_server'),
            'rviz',
            'navigation.rviz'
        )


    #dynamic path selection

    path_pkg_share = FindPackageShare("path_planner_server")
    path_config_dir = PathJoinSubstitution([path_pkg_share, 'config'])

    #dynamic path selection for the proper map

    path_pkg_share_map = FindPackageShare("map_server")
    path_config_dir_map = PathJoinSubstitution([path_pkg_share_map, 'config'])


    #dyanmic path selection for the localization

    path_pkg_share_localization = FindPackageShare("localization_server")
    path_config_dir_localization = PathJoinSubstitution([path_pkg_share_localization, 'config'])

    controller_yaml = PathJoinSubstitution([path_config_dir,PythonExpression(["'controller_sim.yaml' if (", bool_checker, ") else 'controller_real.yaml'" ])])

    #controller_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'controller_sim.yaml')
    bt_navigator_yaml = PathJoinSubstitution([path_config_dir,PythonExpression(["'bt_navigator_sim.yaml' if (", bool_checker, ") else 'bt_navigator_real.yaml'"])])

    #bt_navigator_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'bt_navigator_sim.yaml')

    planner_yaml = PathJoinSubstitution([path_config_dir,PythonExpression(["'planner_sim.yaml' if (", bool_checker, ") else 'planner_real.yaml'"])])

    #planner_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'planner_sim.yaml')
    
    recovery_yaml = PathJoinSubstitution([path_config_dir,PythonExpression(["'recoveries_sim.yaml' if (", bool_checker, ") else 'recoveries_real.yaml'"])])

    #recovery_yaml = os.path.join(get_package_share_directory('path_planner_server'), 'config', 'recoveries_sim.yaml')
   
    nav2_yaml = PathJoinSubstitution([path_config_dir_localization,PythonExpression(["'amcl_config_sim.yaml' if (", bool_checker, ") else 'amcl_config_real.yaml'" ])])
    #nav2_yaml = os.path.join(get_package_share_directory('localization_server'), 'config', 'amcl_config_sim.yaml')
    
    #map_file = os.path.join(get_package_share_directory('map_server'), 'config', 'warehouse_map_sim.yaml')
    map_file = PathJoinSubstitution([path_config_dir_map,PythonExpression(["'warehouse_map_sim.yaml' if (", bool_checker, ") else 'warehouse_map_real.yaml'"])])
    #file_arg = DeclareLaunchArgument('map_file', default_value='warehouse_map_sim.yaml')

    # footprint: '[[0.325, 0.325], [0.325, -0.325], [-0.325, -0.325], [-0.325, 0.325]]'

    '''map_server_node = Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'use_sim_time': proper_time_arg}, 
                        {'yaml_filename': map_file} 
                       ])
    nav2_amcl_node = Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[nav2_yaml, {'use_sim_time': proper_time_arg}]
        )'''

    #path planner stuff
    controller_node = Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[controller_yaml, {'use_sim_time': proper_time_arg}])
    nav2_planner_node = Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[planner_yaml, {'use_sim_time': proper_time_arg}])
    behavior_node = Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='recoveries_server',
            parameters=[recovery_yaml, {'use_sim_time': proper_time_arg}],
            output='screen')
    nav2_bt_navigator_node = Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[bt_navigator_yaml, {'use_sim_time': proper_time_arg}])

    filter_mask_node = Node(
    package='nav2_map_server',
    executable='map_server',
    name='filter_mask_server',
    output='screen',
    emulate_tty=True,
    parameters=[filters_yaml, {'use_sim_time': proper_time_arg}])

    costmap_filter_node = Node(
    package='nav2_map_server',
    executable='costmap_filter_info_server',
    name='costmap_filter_info_server',
    output='screen',
    emulate_tty=True,
    parameters=[filters_yaml, {'use_sim_time': proper_time_arg}])

    nav2_lifecycle_manager_node = Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_pathplanner',
            output='screen',
            parameters=[{'autostart': True},
                        {'node_names': [
                                        'planner_server',
                                        'controller_server',
                                        'recoveries_server',
                                        'bt_navigator','filter_mask_server',
                                        'costmap_filter_info_server',
]}, 
                        {'use_sim_time': proper_time_arg}])
    rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen'
        )





   
    return LaunchDescription([time_arg, controller_node, nav2_planner_node,behavior_node, nav2_bt_navigator_node, nav2_lifecycle_manager_node, rviz_node,filter_mask_node,costmap_filter_node])
