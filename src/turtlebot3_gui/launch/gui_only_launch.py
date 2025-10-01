import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node # ROS 2 노드 실행을 위해 필요

def generate_launch_description():

    # 시뮬레이션 시간 사용 설정 (필요에 따라)
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # ----------------------------------------------------
    # 1. GUI 노드 설정 및 실행
    # ----------------------------------------------------

    # 저희가 만든 Python GUI 노드 실행
    # entry_points에 등록한 'my_gui_node'를 실행합니다.
    gui_node_cmd = Node(
        package='turtlebot3_gui',        # 저희가 만든 패키지 이름
        executable='my_gui_node',        # setup.py의 console_scripts에 등록한 이름
        name='turtlebot_gui_controller', # ROS 2 노드 이름 설정
        output='screen',                 # 노드의 로그를 터미널에 출력
        parameters=[{'use_sim_time': use_sim_time}] # 시뮬레이션 시간 사용 설정
    )

    # ----------------------------------------------------
    # 2. LaunchDescription에 액션 추가
    # ----------------------------------------------------

    ld = LaunchDescription()
    ld.add_action(gui_node_cmd) # 👈 GUI 노드만 추가

    return ld
