import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node # 👈 GUI 노드 실행을 위해 추가

def generate_launch_description():
    # ----------------------------------------------------
    # 1. 시뮬레이션 환경 설정 (기존 코드 유지)
    # ----------------------------------------------------

    # 패키지 경로 설정
    pkg_turtlebot3_gazebo = get_package_share_directory('turtlebot3_gazebo')
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')

    # Launch 인자 설정
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    x_pose = LaunchConfiguration('x_pose', default='-2.0')
    y_pose = LaunchConfiguration('y_pose', default='-0.5')

    # 사용할 Gazebo 월드 파일 경로 설정
    world = os.path.join(
        pkg_turtlebot3_gazebo,
        'worlds',
        'turtlebot3_world.world'
    )

    # Gazebo 서버 실행
    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={'world': world}.items()
    )

    # Gazebo 클라이언트 (GUI) 실행
    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py')
        )
    )

    # 로봇 상태 발행 (URDF/XACRO 파일 로딩 및 토픽 발행)
    robot_state_publisher_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_turtlebot3_gazebo, 'launch', 'robot_state_publisher.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # 터틀봇 모델을 Gazebo에 소환
    spawn_turtlebot_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_turtlebot3_gazebo, 'launch', 'spawn_turtlebot3.launch.py')
        ),
        launch_arguments={
            'x_pose': x_pose,
            'y_pose': y_pose
        }.items()
    )

    # ----------------------------------------------------
    # 2. GUI 노드 추가 (핵심)
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
    # 3. LaunchDescription에 모든 액션 추가
    # ----------------------------------------------------

    ld = LaunchDescription()

    ld.add_action(gzserver_cmd)
    ld.add_action(gzclient_cmd)
    ld.add_action(robot_state_publisher_cmd)
    ld.add_action(spawn_turtlebot_cmd)
    ld.add_action(gui_node_cmd) # 👈 GUI 노드 추가

    return ld
