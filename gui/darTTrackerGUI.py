from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QIcon, QPixmap, QFont
from PyQt6.QtCore import Qt

from utils import cameraUtils as camera
from utils import areasUtils as areas

import pickle
import cv2
import numpy as np
import os

class DarTTrackerGUI(QMainWindow):
	def __init__(self, dev_view, detector, dst_width=camera.dst_width, dst_height=camera.dst_height):
		super().__init__()
		self.dev_view = dev_view
		self.detector = detector
		self.dst_width = dst_width
		self.dst_height = dst_height

		if os.path.isfile("pickleFiles\\adjusted_matrix.pkl"):
			with open("pickleFiles\\adjusted_matrix.pkl", "rb") as f:
				self.perspectiveMatrix = pickle.load(f)
		else:
			self.perspectiveMatrix = None
			print("Warning: Perspective Matrix doesn't exist.")
		
		if os.path.isfile("pickleFiles\\dartboard_config.pkl"):
			with open("pickleFiles\\dartboard_config.pkl", "rb") as f:
				config = pickle.load(f)
				self.center = config["center"] #Center of the dartboard
				self.rings = config["rings"] #Rings' areas
				self.segments = config["segments"] #Segments angles
		else:
			self.center, self.rings, self.segments = [350,350], [5,5,5,5,5,5], [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
			print("Warning: Dartboard Areas don't exist.")

		self.initUI()

	def initUI(self):
		self.setFixedSize(1000, 530)
		self.setWindowTitle("darTTracker")
		self.setWindowIcon(QIcon("icons//dartIcon.png"))

		central_widget = QWidget(self)
		self.setCentralWidget(central_widget)

		layout = QHBoxLayout(central_widget)
		layout.setContentsMargins(0, 0, 0, 0) 
		layout.setSpacing(0)

		#Left Side Frame
		left_frame = QFrame(self)
		left_frame.setFixedSize(350, 530) 
		left_frame.setStyleSheet("background-color: #5f4942;")
		layout.addWidget(left_frame)

		left_layout = QVBoxLayout(left_frame)
		left_layout.setContentsMargins(0,0,0,0)
		left_layout.setSpacing(0)
		title_frame = QFrame(left_frame)
		title_frame.setFixedHeight(80)
		table_frame = QFrame(left_frame)
		left_layout.addWidget(title_frame)
		left_layout.addWidget(table_frame)
		
		self.bottomButtons(left_layout, left_frame)

		if(self.dev_view):
			self.devButtons(left_layout, left_frame)

		title_layout = QHBoxLayout(title_frame)
		title_layout.setContentsMargins(35,0, 35, 0)
		title_layout.setSpacing(10)

		title_label = QLabel("darTTracker")
		title_font = QFont("Bauhaus 93", 28, QFont.Weight.Bold)
		title_label.setFont(title_font)
		title_label.setStyleSheet("color: white;")

		icon = QPixmap("icons//dartIcon.png")
		icon_label = QLabel()
		icon_label.setPixmap(icon.scaled(52, 52))  

		title_layout.addWidget(icon_label)
		title_layout.addWidget(title_label)
		title_layout.setAlignment(icon_label, title_layout.alignment())
		title_layout.setAlignment(title_label, title_layout.alignment())
		title_frame.setLayout(title_layout)
		
		#Right Side Frame
		right_frame = QFrame(self)
		right_frame.setFixedSize(650, 530) 
		right_frame.setStyleSheet("background-color: #628178;")
		layout.addWidget(right_frame)
		
		right_layout = QVBoxLayout(right_frame)
		dartboard = QPixmap("icons//dartBoard.png")
		dartboard_label = QLabel(right_frame)
		dartboard_label.setPixmap(dartboard.scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio))
		right_layout.addWidget(dartboard_label)
		right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
	
	def bottomButtons(self, layout, frame):
		"""
		Bottom buttons
		"""
		bottom_frame = QFrame(frame)
		bottom_frame.setFixedHeight(40)
		layout.addWidget(bottom_frame)
		bottom_layout = QHBoxLayout(bottom_frame)
		bottom_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
		bottom_layout.setContentsMargins(10,5,10,5)
		font = QFont("Roboto")
		quitButton = QPushButton("Quit")
		quitButton.setFont(font)
		quitButton.setFixedSize(80,25)
		quitButton.setStyleSheet("""
			QPushButton {				
				background-color: #976e65;
				color: white;
				border-style: outset;
				border-width: 1px;
				border-color: black;
				border-radius: 5px;
				font-size: 16px;
			}
			QPushButton:hover {
				background-color: #C19A8D;									           
			}
			QPushButton:pressed {
				background-color: #A5837C; 
			}
		""")
		quitButton.setCursor(Qt.CursorShape.PointingHandCursor)
		quitButton.clicked.connect(self.onQuitButtonClick)
		bottom_layout.addWidget(quitButton)

	def devButtons(self, layout, frame):
		"""
		Dev buttons
		"""
		dev_title = QLabel("Dev Menu")
		title_font = QFont("Roboto", 15, QFont.Weight.Bold)
		dev_title.setFont(title_font)
		dev_title.setStyleSheet("color: white; background-color: #533D36;")
		dev_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
		dev_title.setFixedHeight(30)
		layout.addWidget(dev_title)
		dev_frame = QFrame(frame)
		dev_frame.setFixedHeight(45)
		dev_frame.setStyleSheet("background-color: #533D36;")
		layout.addWidget(dev_frame)
		dev_layout = QHBoxLayout(dev_frame)
		font = QFont("Roboto")
		camButton = QPushButton("Camera")
		camButton.setFont(font)
		camButton.setFixedSize(80,25)
		camButton.setStyleSheet("""
			QPushButton {				
				background-color: #976e65;
				color: white;
				border-style: outset;
				border-width: 1px;
				border-color: black;
				border-radius: 5px;
				font-size: 16px;
			}
			QPushButton:hover {
				background-color: #C19A8D;									           
			}
			QPushButton:pressed {
				background-color: #A5837C; 
			}
		""")
		camButton.setCursor(Qt.CursorShape.PointingHandCursor)
		camButton.clicked.connect(self.onCamButtonClick)
		dev_layout.addWidget(camButton)

		areasButton = QPushButton("Areas")
		areasButton.setFont(font)
		areasButton.setFixedSize(80,25)
		areasButton.setStyleSheet("""
			QPushButton {				
				background-color: #976e65;
				color: white;
				border-style: outset;
				border-width: 1px;
				border-color: black;
				border-radius: 5px;
				font-size: 16px;
			}
			QPushButton:hover {
				background-color: #C19A8D;									           
			}
			QPushButton:pressed {
				background-color: #A5837C; 
			}
		""")
		areasButton.setCursor(Qt.CursorShape.PointingHandCursor)
		areasButton.clicked.connect(self.onAreasButtonClick)
		dev_layout.addWidget(areasButton)

		testButton = QPushButton("Test")
		testButton.setFont(font)
		testButton.setFixedSize(80,25)
		testButton.setStyleSheet("""
			QPushButton {				
				background-color: #976e65;
				color: white;
				border-style: outset;
				border-width: 1px;
				border-color: black;
				border-radius: 5px;
				font-size: 16px;
			}
			QPushButton:hover {
				background-color: #C19A8D;									           
			}
			QPushButton:pressed {
				background-color: #A5837C; 
			}
		""")
		testButton.setCursor(Qt.CursorShape.PointingHandCursor)
		testButton.clicked.connect(self.onTestButtonClick)
		dev_layout.addWidget(testButton)


	def onQuitButtonClick(self):
		"""
		Quit button callback
		"""
		camera.cap.release()
		QApplication.quit()

	def onCamButtonClick(self):
		"""
		Dev camera button callback
		"""
		camera.ajustCamera(self.detector)
		with open("pickleFiles\\adjusted_matrix.pkl", "rb") as f:
			self.perspectiveMatrix = pickle.load(f)

	def onAreasButtonClick(self):
		"""
		Dev areas button callback
		"""
		if(self.perspectiveMatrix.all() != None):
			frame = cv2.imread('frames\\frame.jpg')
			transformed_frame = cv2.warpPerspective(frame, self.perspectiveMatrix, (self.dst_width, self.dst_height))
			areas.editAreas(transformed_frame, self.center, self.rings, self.segments)
			with open("pickleFiles\\dartboard_config.pkl", "rb") as f:
				config = pickle.load(f)
				self.center = config["center"]
				self.rings = config["rings"]
				self.segments = config["segments"]
		else:
			print("Error: Perspective Matrix doesn't exist")

	def onTestButtonClick(self):
		print("To do")