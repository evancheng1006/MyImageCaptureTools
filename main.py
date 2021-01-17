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

# https://stackoverflow.com/questions/5998245/get-current-time-in-milliseconds-in-python
def current_milli_time():
	return round(time.time() * 1000)



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
	def get_temperature(self):
		# 3132 -> 313.2 K
		return self.getProperty( PyCapture2.PROPERTY_TYPE.TEMPERATURE ).absValue
	def get_temperature_str(self):
		raw_temperature = self.get_temperature()
		t_k = float(raw_temperature) * 100.0
		t_c = t_k - 273.15
		t_f = 1.8*t_c + 32
		ret = '%.1fK/%.1fC/%.1fF' % (t_k, t_c, t_f)
		return ret

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

	def camera_info_to_str(self):
		cam_info = self.getCameraInfo()
		ret = ''
		ret += '\n*** CAMERA INFORMATION ***\n'
		ret += 'Serial number - %d\n' % cam_info.serialNumber
		ret += 'Camera model - %s\n' % cam_info.modelName.decode()
		ret += 'Camera vendor - %s\n' % cam_info.vendorName.decode()
		ret += 'Sensor - %s\n' % cam_info.sensorInfo.decode()
		ret += 'Resolution - %s\n' % cam_info.sensorResolution.decode()
		ret += 'Firmware version - %s\n' % cam_info.firmwareVersion.decode()
		ret += 'Firmware build time - %s\n' % cam_info.firmwareBuildTime.decode()
		ret += 'Current brightness - %f\n' % self.get_brightness()
		ret += 'Current frame rate - %f frame(s) per second\n' % self.get_frame_rate()
		ret += 'Current gain - %f\n' % self.get_gain()
		ret += 'Current gamma - %f\n' % self.get_gamma()
		ret += 'Current sharpness - %d\n' % self.get_sharpness()
		ret += 'Current shutter - %f ms\n' % self.get_shutter()
		ret += 'Camera temperature - %s\n' % self.get_temperature_str()
		return ret

	def print_camera_info(self):
		print(self.camera_info_to_str())


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

	def dark_current_test(self):
		num_images = 25
		data = []
		ret = 'dark current test, unit: grayscale value (0-255)\n'
		for i in range(self.num_cams):
			temperature_str = self.cams[i].get_temperature_str()
			self.cams[i].startCapture()
			for j in range(num_images):
				image = self.cams[i].retrieveBuffer()
				data.append(image.getData())
			pxs = np.concatenate(data, axis=0)
			ret += 'Camera %d (sn:%d) temperature:%s, pixel max=%d, min=%d, median=%d, mean=%f, std=%f\n' % \
			(i, self.idx_to_sn[i], temperature_str, np.max(pxs), np.min(pxs), np.median(pxs), np.mean(pxs), np.std(pxs))
			self.cams[i].stopCapture()
		return ret

	def noise_test(self):
		num_images = 25
		data = []
		ret = 'noise test, unit: grayscale value (0-255)\n'
		for i in range(self.num_cams):
			temperature_str = self.cams[i].get_temperature_str()
			self.cams[i].startCapture()
			for j in range(num_images):
				image = self.cams[i].retrieveBuffer()
				data.append(image.getData())
			pxs = np.stack(data, axis=1)
			pxs_stds = np.std(data, axis=0, ddof=1)
			pxs_std = np.mean(pxs_stds)
			#print(pxs.shape)
			#print(pxs_stds.shape)
			ret += 'Camera %d (sn:%d)  temperature:%s, noise std=%f\n' % (i,
				self.idx_to_sn[i], temperature_str, pxs_std)
			self.cams[i].stopCapture()
		return ret

	def cam_config_to_str(self):
		ret = ''
		for i in range(self.num_cams):
			cam_info = self.cams[i].getCameraInfo()
			ret += 'Camera %d (sn:%d)\n' % (i, cam_info.serialNumber)
			ret += 'Current brightness - %f\n' % self.cams[i].get_brightness()
			ret += 'Current frame rate - %f frame(s) per second\n' % self.cams[i].get_frame_rate()
			ret += 'Current gain - %f\n' % self.cams[i].get_gain()
			ret += 'Current gamma - %f\n' % self.cams[i].get_gamma()
			ret += 'Current sharpness - %d\n' % self.cams[i].get_sharpness()
			ret += 'Current shutter - %f ms\n' % self.cams[i].get_shutter()
			ret += 'Camera temperature - %s\n' % self.cams[i].get_temperature_str()
		return ret

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
		self.ui.btn_tag_test.clicked.connect(self.btn_tag_test)
		self.ui.btn_tag_calib_extrinsic.clicked.connect(self.btn_tag_calib_extrinsic)
		self.ui.btn_dark_current_test.clicked.connect(self.btn_dark_current_test)
		self.ui.btn_noise_test.clicked.connect(self.btn_noise_test)
		self.ui.msg.setText(self.cc.cam_config_to_str())
		self.timer=QTimer(self)
		self.timer.timeout.connect(self.update)
		self.timer.start(200)

		# self.threadpool = QThreadPool()
		# print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
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
		self.ui.msg.setText(self.cc.cam_config_to_str())
		return

	def btn_short_cam_shutter(self):
		for i in range(self.cc.num_cams):
			self.cc.cams[i].set_brightness(5.5)
			self.cc.cams[i].set_gain(10.0)
			self.cc.cams[i].set_sharpness(1024)
			self.cc.cams[i].set_gamma(1.0)
			self.cc.cams[i].set_shutter(1.0)
			self.cc.cams[i].empty_capture() # save settings
		self.ui.msg.setText(self.cc.cam_config_to_str())
		return
	
	def btn_capture(self):
		self.images = self.cc.capture_images()
		# print(dir(self.ui.plainTextEdit_Tag))
		tag = self.ui.plainTextEdit_Tag.toPlainText();
		timestamp = current_milli_time()

		msg = 'capture:\n'
		msg += 'tag = %s\n' % tag
		msg += 'timestamp = %s\n' % timestamp
		for i in range(self.cc.num_cams):
			sn = self.cc.idx_to_sn[i]
			fn_img_basename = 'image-%s-%s.pgm' % (sn,timestamp)
			fn_txt_basename = 'image-%s-%s_prop.txt' % (sn,timestamp)
			img_dir = 'images/'
			fn_img = img_dir + '/' + fn_img_basename
			fn_txt = img_dir + '/' + fn_txt_basename
			msg += 'saving image to %s\n' % fn_img
			msg += 'saving image property to %s\n' % fn_txt
			prop = ''
			prop += '%s\n' % fn_img_basename
			prop += 'tag = %s\n' % tag
			prop += 'brightness = %f percent\n' % self.cc.cams[i].get_brightness()
			prop += 'gain = %f dB\n' % self.cc.cams[i].get_gain()
			prop += 'sharpness = %d\n' % self.cc.cams[i].get_sharpness()
			prop += 'gamma = %f\n' % self.cc.cams[i].get_gamma()
			prop += 'shutter = %f ms\n' % self.cc.cams[i].get_shutter()	
			#print(prop)
			with open(fn_txt, 'w') as f:
				f.write(prop)
			cv2.imwrite(fn_img, self.images[i])
		self.ui.msg.setText(msg)
		QtWidgets.qApp.processEvents()
		return

	def btn_tag_test(self):
		self.ui.plainTextEdit_Tag.setPlainText('test')
		return

	def btn_tag_calib_extrinsic(self):
		self.ui.plainTextEdit_Tag.setPlainText('calib_extrinsic')
		return

	def btn_dark_current_test(self):
		msg = self.cc.dark_current_test()
		self.ui.msg.setText(msg)
		return

	def btn_noise_test(self):
		msg = self.cc.noise_test()
		self.ui.msg.setText(msg)
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

	def save_images(self):
		return

	def update(self):
		# print('image update')
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