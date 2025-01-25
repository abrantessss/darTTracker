import cv2
import cv2.aruco as aruco

aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

for id in range(4):
    img = aruco.generateImageMarker(aruco_dict, id=id, sidePixels=140)
    cv2.imshow("Aruco", img)
    cv2.imwrite(f"ArucoID{id}.png", img)
    cv2.waitKey(100)
