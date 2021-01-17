from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, QRunnable, QThreadPool
import myUI as UI
import sys
import cv2
import numpy as np
import PyCapture2
import time

def rgb_ndarray_to_pixmap(img):
	height, width, channel = img.shape
	bytes_per_line = 3 * width
	qt_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_RGB888)
	pixmap = QPixmap.fromImage(qt_img)
	return pixmap

def grayscale_ndarray_to_pixmap(img):
	height, width = img.shape
	bytes_per_line = width
	qt_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
	pixmap = QPixmap.fromImage(qt_img)
	return pixmap

def print_build_info():
	lib_ver = PyCapture2.getLibraryVersion()
	print('PyCapture2 library version: %d %d %d %d' % (lib_ver[0], lib_ver[1], lib_ver[2], lib_ver[3]))
	print()



class Camera(PyCapture2.Camera):
	def __init__(self):
		super(PyCapture2.Camera, self).__init__()
	# reference: https://github.com/lixiii/PGR-Camera/blob/master/camera.py
	def get_brightness(self):
		return self.getProperty( PyCapture2.PROPERTY_TYPE.BRIGHTNESS ).absValue
	def get_frame_rate(self):
		return self.getProperty( PyCapture2.PROPERTY_TYPE.FRAME_RATE ).absValue
	def get_gain(self):
		return self.getProperty( PyCapture2.PROPERTY_TYPE.GAIN ).absValue
	def get_gamma(self):
		return self.getProperty( PyCapture2.PROPERTY_TYPE.GAMMA ).absValue
	def get_shutter(self):
		return self.getProperty( PyCapture2.PROPERTY_TYPE.SHUTTER ).absValue
	def get_sharpness(self):
		return self.getProperty( PyCapture2.PROPERTY_TYPE.SHARPNESS ).valueA

	# after you call set_*, you need to call empty_capture to really set those values
	def set_brightness(self, absValue):
		self.setProperty(type = PyCapture2.PROPERTY_TYPE.BRIGHTNESS, autoManualMode=False, absValue=absValue)
		return self.get_brightness()
	def set_frame_rate(self, absValue):
		self.setProperty(type = PyCapture2.PROPERTY_TYPE.FRAME_RATE, autoManualMode=False, absValue=absValue)
		return self.get_frame_rate()
	def set_gain(self, absValue):
		self.setProperty(type = PyCapture2.PROPERTY_TYPE.GAIN, autoManualMode=False, absValue=absValue)
		return self.get_gain()
	def set_gamma(self, absValue):
		self.setProperty(type = PyCapture2.PROPERTY_TYPE.GAMMA, autoManualMode=False, absValue=absValue)
		return self.get_gamma()
	def set_shutter(self, absValue):
		self.setProperty(type = PyCapture2.PROPERTY_TYPE.SHUTTER, autoManualMode=False, absValue=absValue)
		return self.get_shutter()
	def set_sharpness(self, valueA):
		self.setProperty(type = PyCapture2.PROPERTY_TYPE.SHARPNESS, autoManualMode=False, valueA=valueA)
		return self.get_sharpness()

	def empty_capture(self):
		self.startCapture()
		self.retrieveBuffer()
		self.stopCapture()

	def print_camera_info(self):
		cam_info = self.getCameraInfo()
		print('\n*** CAMERA INFORMATION ***\n')
		print('Serial number - %d' % cam_info.serialNumber)
		print('Camera model - %s' % cam_info.modelName.decode())
		print('Camera vendor - %s' % cam_info.vendorName.decode())
		print('Sensor - %s' % cam_info.sensorInfo.decode())
		print('Resolution - %s' % cam_info.sensorResolution.decode())
		print('Firmware version - %s' % cam_info.firmwareVersion.decode())
		print('Firmware build time - %s' % cam_info.firmwareBuildTime.decode())
		print('Current brightness - %f' % self.get_brightness())
		print('Current frame rate - %f frame(s) per second' % self.get_frame_rate())
		print('Current gain - %f' % self.get_gain())
		print('Current gamma - %f' % self.get_gamma())
		print('Current sharpness - %d' % self.get_sharpness())
		print('Current shutter - %f ms' % self.get_shutter())
		print()

class CameraController():
	def __init__(self):
		# Print PyCapture2 Library Information
		print_build_info()
		# Ensure sufficient cameras are found
		self.bus = PyCapture2.BusManager()
		self.num_cams = self.bus.getNumOfCameras()
		print('Number of cameras detected: %d' % self.num_cams)
		if self.num_cams <= 0:
			print('Insufficient number of cameras. Exiting...')
			exit()

	def connect(self):
		self.cams = {}
		for i in range(self.num_cams):
			self.cams[i] = Camera()
			self.cams[i].connect(self.bus.getCameraFromIndex(i))
			self.cams[i].print_camera_info()
		self.idx_to_sn = {}
		self.sn_to_idx = {}
		for i in range(self.num_cams):
			cam_info = self.cams[i].getCameraInfo()
			self.idx_to_sn[i] = cam_info.serialNumber
			self.sn_to_idx[cam_info.serialNumber] = i

	def disconnect(self):
		for i in range(self.num_cams):
			self.cams[i].disconnect()

	def capture_images(self):
		images = {i:[] for i in range(self.num_cams)}
		for i in range(self.num_cams):
			self.cams[i].startCapture()
		for i in range(self.num_cams):
			image = self.cams[i].retrieveBuffer()
			img = image.getData().reshape([image.getCols(),image.getRows()]).astype(np.uint8)
			images[i] = img
		for i in range(self.num_cams):
			self.cams[i].stopCapture()
		return images

# class RealTimeImageUpdateWorker(QRunnable):
# 	def run(self):
# 		self.can_update = False
# 		self.keep_running = True
# 		self.update_period = 1.0
# 		while self.keep_running:
# 			time.sleep(self.update_period)
# 			if self.can_update:
# 				self.update()
# 		print("RealTimeImageUpdateWorker stopped")
# 		return
# 	def update(self):
# 		print("image update")
# 		return

class MainWindow(QtWidgets.QMainWindow):
	def __init__(self, CameraControllerObject):
		self.cc = CameraControllerObject
		self.cc.connect()
		super(MainWindow, self).__init__()
		self.ui = UI.Ui_MainWindow()
		self.ui.setupUi(self)
		self.ui.btn_capture.clicked.connect(self.btn_capture)
		self.ui.btn_long_cam_shutter.clicked.connect(self.btn_long_cam_shutter)
		self.ui.btn_short_cam_shutter.clicked.connect(self.btn_short_cam_shutter)
		self.timer=QTimer(self)
		self.timer.timeout.connect(self.update)
		self.timer.start(200)

		self.threadpool = QThreadPool()
		print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
		# self.rtiuw = RealTimeImageUpdateWorker()
		# self.threadpool.start(self.rtiuw)

	def btn_long_cam_shutter(self):
		for i in range(self.cc.num_cams):
			self.cc.cams[i].set_brightness(5.5)
			self.cc.cams[i].set_gain(10.0)
			self.cc.cams[i].set_sharpness(1024)
			self.cc.cams[i].set_gamma(1.0)
			self.cc.cams[i].set_shutter(10.0)
			self.cc.cams[i].empty_capture() # save settings
		return

	def btn_short_cam_shutter(self):
		for i in range(self.cc.num_cams):
			self.cc.cams[i].set_brightness(5.5)
			self.cc.cams[i].set_gain(10.0)
			self.cc.cams[i].set_sharpness(1024)
			self.cc.cams[i].set_gamma(1.0)
			self.cc.cams[i].set_shutter(1.0)
			self.cc.cams[i].empty_capture() # save settings
		return
	
	def btn_capture(self):

		return

	def display_images(self):
		view_img_shape = (600,600)
		imgs = []
		for i in range(len(self.images)):
			img = self.images[i]
			img = cv2.resize(img, view_img_shape)
			imgs.append(img)
		merged = np.concatenate(imgs, axis=0)
		qt_pixmap_merged = grayscale_ndarray_to_pixmap(merged)
		self.ui.image.setPixmap(qt_pixmap_merged)

	def update(self):
		self.images = self.cc.capture_images()
		self.display_images()
		return
	


	def __del__(self):
		print('stopping')
		self.cc.disconnect()
		print('disconnected')




if __name__ == '__main__':
	cc = CameraController()

	app = QtWidgets.QApplication([])
	window = MainWindow(cc)
	window.show()
	sys.exit(app.exec_())