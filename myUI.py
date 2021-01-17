# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'myUI.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1005, 798)
        MainWindow.setWindowOpacity(1.0)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.image = QtWidgets.QLabel(self.centralwidget)
        self.image.setText("")
        self.image.setObjectName("image")
        self.horizontalLayout.addWidget(self.image)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.msg = QtWidgets.QLabel(self.centralwidget)
        self.msg.setMinimumSize(QtCore.QSize(0, 110))
        self.msg.setMaximumSize(QtCore.QSize(16777215, 110))
        self.msg.setText("")
        self.msg.setObjectName("msg")
        self.verticalLayout_3.addWidget(self.msg)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btn_long_cam_shutter = QtWidgets.QPushButton(self.centralwidget)
        self.btn_long_cam_shutter.setMaximumSize(QtCore.QSize(160, 16777215))
        self.btn_long_cam_shutter.setObjectName("btn_long_cam_shutter")
        self.horizontalLayout_3.addWidget(self.btn_long_cam_shutter)
        self.btn_short_cam_shutter = QtWidgets.QPushButton(self.centralwidget)
        self.btn_short_cam_shutter.setMaximumSize(QtCore.QSize(160, 16777215))
        self.btn_short_cam_shutter.setObjectName("btn_short_cam_shutter")
        self.horizontalLayout_3.addWidget(self.btn_short_cam_shutter)
        self.btn_capture = QtWidgets.QPushButton(self.centralwidget)
        self.btn_capture.setMaximumSize(QtCore.QSize(100, 16777215))
        self.btn_capture.setObjectName("btn_capture")
        self.horizontalLayout_3.addWidget(self.btn_capture, 0, QtCore.Qt.AlignLeft)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1005, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.toolBar_2 = QtWidgets.QToolBar(MainWindow)
        self.toolBar_2.setObjectName("toolBar_2")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_2)
        self.toolBar_3 = QtWidgets.QToolBar(MainWindow)
        self.toolBar_3.setObjectName("toolBar_3")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_3)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MyImageCaptureTools"))
        self.btn_long_cam_shutter.setText(_translate("MainWindow", "Long Camera Shutter"))
        self.btn_short_cam_shutter.setText(_translate("MainWindow", "Short Camera Shutter"))
        self.btn_capture.setText(_translate("MainWindow", "Capture"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.toolBar_2.setWindowTitle(_translate("MainWindow", "toolBar_2"))
        self.toolBar_3.setWindowTitle(_translate("MainWindow", "toolBar_3"))

