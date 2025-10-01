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

    # =================================================================
    #                           Subscriber Callbacks
    # =================================================================

    def scan_callback(self, msg: LaserScan):
        """LaserScan 데이터 수신 시 호출"""
        self.scan_ranges = msg.ranges

        # 장애물 감지 로직을 여기에 추가할 수 있음
        min_distance = min(self.scan_ranges[0:30] + self.scan_ranges[330:360]) # 전방 60도 범위

        if self.log_callback:
            # GUI의 lw_log에 실시간으로 로그를 전달 (5초에 한 번만 출력)
            if self.get_clock().now().nanoseconds % (5 * 10**9) < 1 * 10**8:
                self.log_callback(f"SCAN: Min Dist={min_distance:.2f} m")

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
