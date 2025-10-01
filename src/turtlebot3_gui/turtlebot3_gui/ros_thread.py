# ros_thread.py
from PySide6.QtCore import QThread, Signal # PySide6.QtCore 대신 PySide6.QtCore을 사용해야 함
import rclpy
from rclpy.executors import SingleThreadedExecutor
from .turtlebot3_node import TurtleBotNode

class RclpyThread(QThread):
    """
    QThread를 상속받아 ROS 2 통신(rclpy.spin)을 처리하는 별도의 쓰레드입니다.
    GUI의 응답성을 유지하면서 ROS 2 메시지를 처리할 수 있게 합니다.
    """

    # GUI (main_window.py)의 lw_log 위젯으로 로그/데이터를 전달하기 위한 시그널
    # str 타입의 데이터를 보냅니다.
    log_signal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # 1. ROS 2 노드 및 Executor 준비
        self.executor = SingleThreadedExecutor()
        # 이전에 정의한 TurtleBotNode 클래스의 인스턴스 생성
        self.node = TurtleBotNode()
        self.executor.add_node(self.node)

        # 2. 노드에 로그 전달 콜백 연결 (핵심)
        # TurtleBotNode가 로그 메시지를 emit하도록 RclpyThread의 시그널 연결
        self.node.set_log_callback(self.log_signal.emit)

    def run(self):
        """
        QThread가 시작될 때 호출되며, ROS 2의 메시지 처리를 담당하는 메인 루프입니다.
        """
        self.log_signal.emit(f"ROS Thread started. Node: {self.node.get_name()}")
        try:
            # 쓰레드 내에서 blocking spin을 실행하여 모든 ROS 2 콜백(Publisher, Subscriber, Timer) 처리
            self.executor.spin()
        except Exception as e:
            self.log_signal.emit(f"ROS Thread Error: {e}")
        finally:
            self.log_signal.emit("ROS Thread finished.")

    # =================================================================
    #                       GUI에서 호출할 메서드 (노드 제어)
    # =================================================================

    def forward_task(self):
        """GUI 버튼 클릭 -> 전진 명령"""
        self.node.move_forward()

    def backward_task(self):
        """GUI 버튼 클릭 -> 후진 명령"""
        self.node.move_backward()

    def left_task(self):
        """GUI 버튼 클릭 -> 좌회전 명령"""
        self.node.turn_left()

    def right_task(self):
        """GUI 버튼 클릭 -> 우회전 명령"""
        self.node.turn_right()

    def stop_task(self):
        """GUI 버튼 클릭 -> 정지 명령"""
        self.node.halt_robot()

    def stop(self):
        """GUI 종료 시 ROS 2 쓰레드와 노드를 안전하게 종료"""
        self.log_signal.emit("Attempting to stop ROS Thread...")

        # Executor에게 종료를 요청하고, spin()을 종료시킴
        # rclpy.spin()이 종료된 후, run() 함수도 자연스럽게 종료됩니다.
        self.executor.shutdown()
        self.node.destroy_node()

        # QThread가 완전히 끝날 때까지 대기
        self.wait()
