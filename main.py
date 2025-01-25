from gui.darTTrackerGUI import DarTTrackerGUI 
from PyQt6.QtWidgets import QApplication
import sys
import cv2

#Dev View
dev_view = True

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)  # Use a 4x4 dictionary with 50 unique markers
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

def main():
	app = QApplication(sys.argv)
	window = DarTTrackerGUI(dev_view, detector)
	window.show()
	sys.exit(app.exec())

if __name__ == "__main__":
	main()
