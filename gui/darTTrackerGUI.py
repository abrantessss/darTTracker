from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QSizePolicy, QHeaderView, QTableWidget, QTableWidgetItem, QFrame, QHBoxLayout, QLabel, QVBoxLayout, QPushButton, QComboBox
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
		self.in_dev_option = False #True if dev button is pressed
		self.detector = detector
		self.dst_width = dst_width
		self.dst_height = dst_height
		self.num_players = 1 #Default
		self.game_type = 301 #Default
		self.game_round = 1 #Default

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

		self.left_layout = QVBoxLayout(left_frame)
		self.left_layout.setContentsMargins(0,0,0,0)
		self.left_layout.setSpacing(0)
		title_frame = QFrame(left_frame)
		title_frame.setFixedHeight(80)
		self.left_layout.addWidget(title_frame)

		self.createMainFrame()

		self.addTitle(title_frame)
		self.bottomButtons(self.left_layout, left_frame)
		if(self.dev_view):
			self.devButtons(self.left_layout, left_frame)
		
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
	
	def addTitle(self, title_frame):
		"""
		Title design
		"""
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

	def createMainFrame(self):
		"""
		Define main frame windows
		Pre game window
		In game window
		Post game window (to do)
		"""
		self.pre_game_frame = QWidget()
		pre_game_layout = QVBoxLayout(self.pre_game_frame)
		pre_game_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
		title_num_players = QLabel("Players")
		font = QFont("Roboto", 12, QFont.Weight.Bold)
		title_num_players.setFont(font)
		title_num_players.setStyleSheet("color: white;")
		pre_game_layout.addWidget(title_num_players)
		self.combo_num_players = QComboBox()
		self.combo_num_players.setStyleSheet("""			
				background-color: #976e65;
				color: white;
				border-style: outset;
				border-width: 1px;
				border-color: black;
				font-size: 12px;
		""")
		self.combo_num_players.addItems(['1','2','3','4','5','6'])
		pre_game_layout.addWidget(self.combo_num_players)
		pre_game_layout.addSpacing(20)

		title_game = QLabel("Game")
		title_game.setFont(font)
		title_game.setStyleSheet("color: white;")
		self.combo_num_players.currentIndexChanged.connect(self.onNumPlayers)
		pre_game_layout.addWidget(title_game)
		self.combo_type_game = QComboBox()
		self.combo_type_game.setStyleSheet("""			
				background-color: #976e65;
				color: white;
				border-style: outset;
				border-width: 1px;
				border-color: black;
				font-size: 12px;
		""")
		self.combo_type_game.addItems(['301','501','701'])
		self.combo_type_game.currentIndexChanged.connect(self.onGameType)
		pre_game_layout.addWidget(self.combo_type_game)
		pre_game_layout.addSpacing(35)

		startButton = QPushButton("Start")
		startButton.setFont(font)
		startButton.setFixedSize(80,25)
		startButton.setStyleSheet("""
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
		startButton.setCursor(Qt.CursorShape.PointingHandCursor)
		startButton.clicked.connect(self.onStartButtonClick)
		pre_game_layout.addWidget(startButton)
		self.left_layout.addWidget(self.pre_game_frame)
	
	def onNumPlayers(self, index):
		"""
		Num players callback
		"""
		self.num_players = int(self.combo_num_players.itemText(index))
		print(f"Number of Players: {self.num_players}")

	def onGameType(self, index):
		"""
		Game type callback
		"""
		self.game_type = int(self.combo_type_game.itemText(index))
		print(f"Game Type: {self.game_type}")

	def onStartButtonClick(self):
		print(f"Start Game | Player: {self.num_players} | Game: {self.game_type}")
		self.game_round = 1 #Restart game round
		
		self.in_game_frame = QWidget()
		in_game_layout = QVBoxLayout(self.in_game_frame)
		in_game_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
		
		# Game label
		game_label = QLabel(f"Game: {self.game_type}                              Round: {self.game_round}")
		font = QFont("Roboto", 12, QFont.Weight.Bold)
		game_label.setFont(font)
		game_label.setStyleSheet("color: white;")
		game_label.setContentsMargins(10, 10, 0, 0)
		in_game_layout.addWidget(game_label)

		# Table
		self.table = QTableWidget()
		self.table.setColumnCount(5)
		self.table.setHorizontalHeaderLabels(["Player", "Throw 1", "Throw 2", "Throw 3", "Score"])
		self.table.setFixedSize(320, self.table.verticalHeader().defaultSectionSize() * (self.num_players + 1) + 20)
		self.table.setRowCount(self.num_players)
		for row in range(self.num_players):
				player_item = QTableWidgetItem(f"{row + 1}")
				player_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
				self.table.setItem(row, 0, player_item)
		self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
		self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
		self.table.verticalHeader().setVisible(False)
		self.table.setStyleSheet("""
				QTableWidget {
						background-color: #976e65;
						color: white;
						font: Roboto;
						font-weight: bold;
						font-size: 12px;
						padding: 1px;
						border: 2px solid black;
				}
				QHeaderView::section {
						background-color: #976e65;
						color: white;
						font: Roboto;
						font-weight: bold;
						font-size: 14px;
						padding: 1px;
				}
		""")
		in_game_layout.addWidget(self.table, alignment=Qt.AlignmentFlag.AlignCenter)

		# Buttons layout
		button_layout = QHBoxLayout()
		button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
		button_font = QFont("Roboto")
		# Leave button
		leave_button = QPushButton("Leave Game")
		leave_button.setFont(button_font)
		leave_button.setFixedSize(100, 25)
		leave_button.setStyleSheet("""
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
		leave_button.setCursor(Qt.CursorShape.PointingHandCursor)
		leave_button.clicked.connect(self.onLeaveButton)
		button_layout.addWidget(leave_button)

		# Failed Dart button
		failed_dart_button = QPushButton("Failed Dart")
		failed_dart_button.setFont(button_font)
		failed_dart_button.setFixedSize(100, 25)
		failed_dart_button.setStyleSheet(leave_button.styleSheet())
		failed_dart_button.setCursor(Qt.CursorShape.PointingHandCursor)
		failed_dart_button.clicked.connect(self.onFailedDartButton)
		button_layout.addWidget(failed_dart_button)

		# Next Player button
		next_player_button = QPushButton("Next Player")
		next_player_button.setFont(button_font)
		next_player_button.setFixedSize(100, 25)
		next_player_button.setStyleSheet(leave_button.styleSheet())
		next_player_button.setCursor(Qt.CursorShape.PointingHandCursor)
		next_player_button.clicked.connect(self.onNextPlayerButton)
		button_layout.addWidget(next_player_button)

		in_game_layout.addLayout(button_layout)

		# Replace the pre-game frame with the in-game frame
		self.left_layout.replaceWidget(self.pre_game_frame, self.in_game_frame)
		self.pre_game_frame.hide()
		self.in_game_frame.show()

	def onLeaveButton(self):
		"""
		Leave Game button callback
		"""
		print("Leave Game, Back to Main Menu")
		self.left_layout.replaceWidget(self.in_game_frame, self.pre_game_frame)
		self.in_game_frame.hide()
		self.pre_game_frame.show()

	def onFailedDartButton(self):
		"""
		Failed Dart callback
		"""
		print("To do")
	
	def onNextPlayerButton(self):
		"""
		Next Player callback
		"""
		print("To do")

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
		print("Quit App")
		cv2.destroyAllWindows()
		camera.cap.release()
		QApplication.quit()

	def onCamButtonClick(self):
		"""
		Dev camera button callback
		"""
		print("Adjust Camera")
		self.in_dev_option = True
		camera.ajustCamera(self.detector)
		with open("pickleFiles\\adjusted_matrix.pkl", "rb") as f:
			self.perspectiveMatrix = pickle.load(f)
		self.in_dev_option = False

	def onAreasButtonClick(self):
		"""
		Dev areas button callback
		"""
		print("Adjust Areas")
		self.in_dev_option = True
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
		self.in_dev_option = False

	def onTestButtonClick(self):
		"""
		Test button callback
		"""
		print("Test Detection")
		self.in_dev_option = True
		print("To do")
		#Apenas permite lançar um dado de cada vez, deteta e coloca no alvo da app
		#No frame CV2 texto com Q-Quit | R-Reset
		#Mostra os diversos frames: Mascaras e Frame com o dardo detetado
		#Print da pontução do dardo no Frame
		self.in_dev_option = False