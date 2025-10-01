# turtlebot_node.py
import math
import numpy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, qos_profile_sensor_data
from typing import Callable
import time

# Custom Node for TurtleBot communication
class TurtleBotNode(Node):
    def __init__(self):
        # ROS 2 노드 초기화. 이름은 'turtlebot_gui_node'로 설정
        super().__init__('turtlebot_gui_node')

        # GUI 쓰레드에 로그를 전달하기 위한 콜백 함수 (ros_thread에서 연결됨)
        self.log_callback: Callable[[str], None] = None

        # --- 1. Publisher (주행 명령 발행) 설정 ---
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.twist_msg = Twist()
        self.timer_ = None

        # --- 2. Subscriber (LaserScan 수신) 설정 (Move_turtle 코드 참고) ---
        self.scan_ranges = []
        self.scan_sub = self.create_subscription(
            LaserScan,
            'scan',
            self.scan_callback,
            qos_profile=qos_profile_sensor_data # 센서 데이터에 적합한 QoS 사용
        )

        # --- 3. Subscriber (Odometry 수신) 설정 (TurtlebotPose 코드 참고) ---
        odom_qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        self.last_pose_x = 0.0
        self.last_pose_y = 0.0
        self.last_pose_theta = 0.0
        self.odom_sub = self.create_subscription(
            Odometry,
            'odom',
            self.odom_callback,
            odom_qos_profile
        )
        self.odom_log_count = 0 # 로그 출력 주기를 위한 카운터

        self.is_obstacle_present = False
        self.obstacle_detection_threshold = 0.5 # 장애물 감지 임계값 (미터)

    # =================================================================
    #                           Subscriber Callbacks
    # =================================================================

    def scan_callback(self, msg: LaserScan):
        """LaserScan 데이터 수신 시 호출"""
        self.scan_ranges = msg.ranges
        front_area_ranges = [r for r in self.scan_ranges[150:211] if not math.isinf(r) and r > 0.0]
        if front_area_ranges:
            front_min_distance = min(front_area_ranges)

        current_time = self.get_clock().now()

        # --- 장애물 감지 로직 ---
        new_obstacle_state = False
        if front_min_distance < self.obstacle_detection_threshold:
            new_obstacle_state = True

        # 장애물 감지 상태가 변경되었을 때만 로그를 출력하여 중복 메시지를 방지합니다.
        if new_obstacle_state and not self.is_obstacle_present:
            # 장애물이 새로 감지된 경우
            if self.log_callback:
                self.log_callback(f"SCAN: !!! OBSTACLE DETECTED !!! Min dist: {front_min_distance:.2f} m")
            # 로봇 움직임을 제어하는 로직은 여기에 추가하지 않습니다.
            # (예: self.halt_robot() 또는 다른 움직임 명령)

        elif not new_obstacle_state and self.is_obstacle_present:
            # 장애물이 사라진 경우
            if self.log_callback:
                self.log_callback(f"SCAN: OBSTACLE CLEARED. Min dist: {front_min_distance:.2f} m")

        self.is_obstacle_present = new_obstacle_state # 현재 장애물 상태 업데이트
        # 장애물 감지 로직을 여기에 추가할 수 있음
        min_distance = min(self.scan_ranges[0:30] + self.scan_ranges[330:360]) # 전방 60도 범위

        if self.log_callback:
            # 5초에 한 번만 출력하도록 변경
            # 너무 자주 출력되면 로그창이 빠르게 스크롤될 수 있습니다.
            # 예시: 5초마다 출력 (5 * 10^9 나노초)
            if current_time.nanoseconds % (1 * 10**9) < rclpy.duration.Duration(seconds=0.1).nanoseconds: # 약 0.1초 윈도우
                self.log_callback(f"SCAN: Current Min Front Dist={front_min_distance:.2f} m")

    def odom_callback(self, msg: Odometry):
        """Odometry 데이터 수신 시 호출 (TurtlebotPose 코드 참고)"""
        self.last_pose_x = msg.pose.pose.position.x
        self.last_pose_y = msg.pose.pose.position.y
        _, _, self.last_pose_theta = self.euler_from_quaternion(msg.pose.pose.orientation)

        self.odom_log_count += 1
        if self.odom_log_count > 20: # 약 1초에 한 번 (odom이 20Hz 발행된다 가정)
            if self.log_callback:
                self.log_callback(f"ODOM: X={self.last_pose_x:.2f}, Y={self.last_pose_y:.2f}, Yaw={self.last_pose_theta:.2f} rad")
            self.odom_log_count = 0

    # =================================================================
    #                       Publisher & Control Methods
    # =================================================================

    def set_log_callback(self, callback: Callable[[str], None]):
        """ros_thread에서 GUI로 로그를 전달할 함수 연결"""
        self.log_callback = callback

    def publish_twist(self):
        """주기적으로 Twist 메시지를 발행하는 타이머 콜백"""
        self.publisher_.publish(self.twist_msg)

    def start_publishing_timer(self):
        """주행 타이머 시작 또는 업데이트"""
        if self.timer_ is None:
            # 50ms 간격으로 publish_twist 함수 호출 (20Hz)
            self.timer_ = self.create_timer(0.05, self.publish_twist)
            if self.log_callback:
                 self.log_callback('PUB: Timer started for /cmd_vel.')

    def stop_publishing_timer(self):
        """타이머 중지 및 정지 메시지 발행"""
        if self.timer_ is not None:
            self.timer_.cancel()
            self.timer_ = None

            # 정지 메시지 발행
            self.twist_msg.linear.x = 0.0
            self.twist_msg.angular.z = 0.0
            self.publisher_.publish(self.twist_msg)

            if self.log_callback:
                self.log_callback('PUB: Timer stopped and robot halted.')

    def set_and_start_motion(self, linear_x, angular_z):
        """버튼 이벤트로 호출되는 실제 주행 명령 설정 함수"""
        self.twist_msg.linear.x = linear_x
        self.twist_msg.angular.z = angular_z
        self.start_publishing_timer() # 타이머 시작/유지
        if self.log_callback:
             self.log_callback(f'PUB: Set V={linear_x:.1f}, W={angular_z:.1f}')

    # --- GUI 버튼 연결 함수 ---
    def move_forward(self):
        self.set_and_start_motion(0.2, 0.0)

    def move_backward(self):
        self.set_and_start_motion(-0.2, 0.0)

    def turn_left(self):
        self.set_and_start_motion(0.0, 0.5)

    def turn_right(self):
        self.set_and_start_motion(0.0, -0.5)

    def halt_robot(self):
        self.stop_publishing_timer()

    # =================================================================
    #                           Utility (Pose)
    # =================================================================

    def euler_from_quaternion(self, quat):
        """오도메트리에서 자세(Yaw)를 얻기 위한 쿼터니언 변환 (TurtlebotPose 코드 참고)"""
        x, y, z, w = quat.x, quat.y, quat.z, quat.w

        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = numpy.arctan2(sinr_cosp, cosr_cosp)

        sinp = 2 * (w * y - z * x)
        pitch = numpy.arcsin(sinp)

        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = numpy.arctan2(siny_cosp, cosy_cosp)

        return roll, pitch, yaw
