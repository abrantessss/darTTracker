from time import time
import cv2
import numpy as np
import pickle

dst_width = 700 
dst_height = 700

dst_points = np.float32([
	[0, 0],
	[dst_width-1, 0],
  [0, dst_height-1],
	[dst_width-1, dst_height-1]
])

# Initialize the camera
st_time = time()
cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
ed_time = time()
cap.set(cv2.CAP_PROP_FPS, 30.0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M','J','P','G'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
print(f"elapsed time: {ed_time - st_time}")

def ajustCamera(detector):
  """
    Ajusts camera angle
    :param detector: arUco detector
    :return: None
  """
  while cap.isOpened():
    # Capture each frame from the camera
    ret, frame = cap.read()
    if not ret:
        print("Ret: False")
        break
    
    if frame is not None:
       # Save the current frame as a JPG file, overwriting previous one
        #cv2.imwrite('frames\\frame.jpg', frame)
        frame = cv2.imread('frames\\frame.jpg')
        cv2.imwrite('frames\\frame.jpg', frame)
        cv2.imwrite('frames\\background.jpg', frame)

    # Detect Aruco markers in the frame
    corners, ids, _ = detector.detectMarkers(frame)

    # Display the original frame with detected markers and middle point
    cv2.aruco.drawDetectedMarkers(frame, corners, ids)
    cv2.namedWindow("Frame with Detected Markers", cv2.WINDOW_NORMAL)

    if ids is not None and len(ids) >= 4:
       # Sort the markers based on their IDs or positions to get a consistent order
      ids = ids.flatten()
      marker_corners = {id: corner for id, corner in zip(ids, corners)}

      # Select four specific markers (IDs 0, 1, 2, and 3 as an example)
      if all(id in marker_corners for id in [0, 1, 2, 3]):
        src_points = np.int32([
          marker_corners[0][0][1],  # Top-left marker corner
          marker_corners[1][0][1],  # Top-right marker corner
          marker_corners[2][0][2],  # Bottom-right marker corner
          marker_corners[3][0][2]  # Bottom-left marker corner
        ])

      middle_point = np.int32(np.mean(src_points, axis=0))
      cv2.drawMarker(frame, tuple(src_points[0]), (255, 255, 0), thickness=3)
      cv2.drawMarker(frame, tuple(src_points[1]), (255, 255, 0), thickness=3)
      cv2.drawMarker(frame, tuple(src_points[2]), (255, 255, 0), thickness=3)
      cv2.drawMarker(frame, tuple(src_points[3]), (255, 255, 0), thickness=3)
      cv2.drawMarker(frame, tuple(middle_point), (0, 0, 255), thickness=2)

    cv2.imshow("Frame with Detected Markers", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        if ids is not None and len(ids) >= 4:
          warp_matrix = cv2.getPerspectiveTransform(np.float32(src_points), dst_points)
          with open("pickleFiles//adjusted_matrix.pkl", "wb") as f:
            pickle.dump(warp_matrix, f)
        break
  cv2.destroyWindow("Frame with Detected Markers")

def set_frame():
    '''
    set new frame
    '''
    _, frame = cap.read()
    if frame is not None:
        # Save the current frame as a JPG file, overwriting previous one
        cv2.imwrite('frame\\frame.jpg', frame)
