# main_window.py
import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow

import rclpy # ROS 2 통신 라이브러리 추가
from .robot_gui_ui import Ui_MainWindow # ui_test.py -> ui_robot_gui.py 이름 변경 가정
from .ros_thread import RclpyThread # 이전에 작성한 ROS 2 쓰레드 import

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # 1. ROS 2 시스템 초기화 (rclpy.init)
        if not rclpy.ok():
            rclpy.init(args=None)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 2. ROS 2 쓰레드 인스턴스 생성 및 시작
        self.ros_thread = RclpyThread(self)
        self.ros_thread.start()

        # 3. 로그 시그널을 lw_log 위젯과 연결
        # lw_log의 objectName은 lw_log로 가정하고, log_signal은 ros_thread.py에 정의되어 있음.
        self.ros_thread.log_signal.connect(self.update_log_widget)

        # 4. 버튼 이벤트와 ROS 2 명령 연결
        self.ui.btn_forward.clicked.connect(self.btn_forward_clicked)
        self.ui.btn_left.clicked.connect(self.btn_left_clicked)
        self.ui.btn_right.clicked.connect(self.btn_right_clicked)
        self.ui.btn_backward.clicked.connect(self.btn_backward_clicked)
        self.ui.btn_stop.clicked.connect(self.btn_stop_clicked)

    # 5. 주행 버튼 클릭 시: lw_msg 출력 + ROS 2 쓰레드에 명령 전달
    def btn_forward_clicked(self):
        self.ui.lw_msg.addItem("GUI: Move forward command issued.")
        self.ui.lw_msg.scrollToBottom()
        self.ros_thread.forward_task()

    def btn_left_clicked(self):
        self.ui.lw_msg.addItem("GUI: Turn left command issued.")
        self.ui.lw_msg.scrollToBottom()
        self.ros_thread.left_task()

    def btn_right_clicked(self):
        self.ui.lw_msg.addItem("GUI: Turn right command issued.")
        self.ui.lw_msg.scrollToBottom()
        self.ros_thread.right_task()

    def btn_backward_clicked(self):
        self.ui.lw_msg.addItem("GUI: Move backward command issued.")
        self.ui.lw_msg.scrollToBottom()
        self.ros_thread.backward_task()

    def btn_stop_clicked(self):
        self.ui.lw_msg.addItem("GUI: Stop command issued.")
        self.ui.lw_msg.scrollToBottom()
        self.ros_thread.stop_task()

    # 6. ROS 2 로그 수신 슬롯
    def update_log_widget(self, message):
        """ROS 2 쓰레드에서 넘어온 로그(오도메트리, 스캔 등)를 lw_log에 추가"""
        self.ui.lw_log.addItem(message)
        self.ui.lw_log.scrollToBottom()

    # 7. 종료 이벤트 처리 (필수)
    def closeEvent(self, event):
        """GUI 종료 시 ROS 2 쓰레드 및 노드 안전 종료"""
        # ros_thread 내의 executor.shutdown()과 node.destroy_node() 호출
        self.ros_thread.stop()
        # ROS 2 시스템 전체 종료
        rclpy.shutdown()
        super().closeEvent(event)


def main(args=None):
    # 이전에 if __name__ == "__main__": 블록 안에 있던 내용입니다.
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
