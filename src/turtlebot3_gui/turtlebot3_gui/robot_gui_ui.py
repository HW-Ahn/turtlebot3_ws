# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'robot_gui.ui'
##
## Created by: Qt User Interface Compiler version 6.9.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QListWidget, QListWidgetItem,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.btn_forward = QPushButton(self.centralwidget)
        self.btn_forward.setObjectName(u"btn_forward")
        self.btn_forward.setGeometry(QRect(110, 90, 95, 25))
        self.btn_left = QPushButton(self.centralwidget)
        self.btn_left.setObjectName(u"btn_left")
        self.btn_left.setGeometry(QRect(10, 130, 95, 25))
        self.btn_stop = QPushButton(self.centralwidget)
        self.btn_stop.setObjectName(u"btn_stop")
        self.btn_stop.setGeometry(QRect(110, 130, 95, 25))
        self.btn_right = QPushButton(self.centralwidget)
        self.btn_right.setObjectName(u"btn_right")
        self.btn_right.setGeometry(QRect(210, 130, 95, 25))
        self.btn_backward = QPushButton(self.centralwidget)
        self.btn_backward.setObjectName(u"btn_backward")
        self.btn_backward.setGeometry(QRect(110, 170, 95, 25))
        self.lw_msg = QListWidget(self.centralwidget)
        self.lw_msg.setObjectName(u"lw_msg")
        self.lw_msg.setGeometry(QRect(20, 260, 291, 291))
        self.lw_log = QListWidget(self.centralwidget)
        self.lw_log.setObjectName(u"lw_log")
        self.lw_log.setGeometry(QRect(370, 90, 361, 461))
        self.lbl_msg = QLabel(self.centralwidget)
        self.lbl_msg.setObjectName(u"lbl_msg")
        self.lbl_msg.setGeometry(QRect(120, 230, 67, 17))
        self.lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_move = QLabel(self.centralwidget)
        self.lbl_move.setObjectName(u"lbl_move")
        self.lbl_move.setGeometry(QRect(120, 30, 67, 17))
        self.lbl_move.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_log = QLabel(self.centralwidget)
        self.lbl_log.setObjectName(u"lbl_log")
        self.lbl_log.setGeometry(QRect(520, 40, 67, 17))
        self.lbl_log.setAlignment(Qt.AlignmentFlag.AlignCenter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 27))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.btn_forward.setText(QCoreApplication.translate("MainWindow", u"forward", None))
        self.btn_left.setText(QCoreApplication.translate("MainWindow", u"left turn", None))
        self.btn_stop.setText(QCoreApplication.translate("MainWindow", u"stop", None))
        self.btn_right.setText(QCoreApplication.translate("MainWindow", u"right turn", None))
        self.btn_backward.setText(QCoreApplication.translate("MainWindow", u"backward", None))
        self.lbl_msg.setText(QCoreApplication.translate("MainWindow", u"message", None))
        self.lbl_move.setText(QCoreApplication.translate("MainWindow", u"move", None))
        self.lbl_log.setText(QCoreApplication.translate("MainWindow", u"log", None))
    # retranslateUi

