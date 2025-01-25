import cv2
import numpy as np
import pickle

######################################GLOBALS######################################
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)  # Use a 4x4 dictionary with 50 unique markers
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
show_dev = True #If true, a dev menu appears
###################################################################################
dst_width, dst_height = 500, 500
dst_points = np.float32([
	[0, 0],
	[dst_width-1, 0],
	[dst_width-1, dst_height-1],
	[0, dst_height-1]
])

dartboard_center = None
circle_axes_values = None
angle_values = None

def SetBoardParams():
	"""
	set the board parameters from pickle file
	"""
	global dartboard_center, circle_axes_values, angle_values
	# Load the saved configuration file
	with open("pickleFiles\\dartboard_config.pkl", "rb") as f:
		config = pickle.load(f)
	# Extract the loaded values
	dartboard_center = config["dartboard_center"]
	circle_axes_values = config["circle_axes_values"]
	angle_values = config["angle_values"]

def DrawDartboardAreas(frame):
	"""
	draw circle areas in given frame
	:param frame: frame to draw in
	"""
	for i, radius in enumerate(circle_axes_values):
		color = (0, 255, 0)
		thickness = 1 
		cv2.circle(frame, tuple(dartboard_center), radius, color, thickness)
          
def PerspectiveCorrection(detector, frame):
    """
    Transforms the frame perspective to a front view of the dartboard
    :param detector: aruco detector
    :param frame: frame to transform
    :return: transformed frame and warp matrix
    """
    # Detect Aruco markers in the frame
    corners, ids, _ = detector.detectMarkers(frame)
    if ids is not None and len(ids) >= 4:
      # Sort the markers based on their IDs or positions to get a consistent order
      ids = ids.flatten()
      marker_corners = {id: corner for id, corner in zip(ids, corners)}

      # Select four specific markers (IDs 0, 1, 2, and 3 as an example)
      if all(id in marker_corners for id in [0, 1, 2, 3]):
        src_points = np.float32([
          marker_corners[0][0][1],  # Top-left marker corner
          marker_corners[1][0][1],  # Top-right marker corner
          marker_corners[3][0][2],  # Bottom-right marker corner
          marker_corners[2][0][2]  # Bottom-left marker corner
        ])
        src_points[0][1] = src_points[1][1]
        src_points[3][1] = src_points[2][1]
        src_points[3][0] = src_points[0][0]
        src_points[1][0] = src_points[2][0]
        print(src_points)

        # Calculate the homography matrix
        warp_matrix = cv2.getPerspectiveTransform(src_points, dst_points)

        # Apply perspective transformation to the entire frame
        transformed_frame = cv2.warpPerspective(frame, warp_matrix, (dst_width, dst_height))

        return transformed_frame, warp_matrix
    else:
      raise Exception(f"Missing Aruco Markers, Only Found: {ids}")


def main():
    SetBoardParams()
    frame = cv2.imread("frames//frame.jpg")
    transformed_frame, warp_matrix = PerspectiveCorrection(detector, frame)
    with open("pickleFiles//adjusted_matrix.pkl", "wb") as f:
      pickle.dump(warp_matrix, f)

    # Mostrar a imagem final
    DrawDartboardAreas(transformed_frame)
    cv2.imshow("Frame", transformed_frame)
    while(True):
      if cv2.waitKey(1) & 0xFF == ord('q'):
           break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
