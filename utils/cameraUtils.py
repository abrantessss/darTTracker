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
  """
  while cap.isOpened():
    # Capture each frame from the camera
    
    ret, frame = cap.read()
    if not ret:
        print("Ret: False")
        break
    
    if frame is not None:
       # Save the current frame as a JPG file, overwriting previous one
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
          marker_corners[0][0][0],  # Top-left marker corner
          marker_corners[1][0][1],  # Top-right marker corner
          marker_corners[2][0][3],  # Bottom-right marker corner
          marker_corners[3][0][2]  # Bottom-left marker corner
        ])

      #Hard coded for better perspective adjustment | TO DO: Create algoritm to adjust based on the angle of the camera
      src_points[0][0] = src_points[0][0] + 5 
      src_points[2][0] = src_points[2][0] + 5 

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
          cv2.destroyWindow("Frame with Detected Markers")
        break

def setFrame():
  '''
  set new frame
  '''
  _, frame = cap.read()
  if frame is not None:
      # Save the current frame as a JPG file, overwriting previous one
      cv2.imwrite('frames\\frame.jpg', frame)

def maskDifferences(frame, background, perspective_matrix, frame_size, triangle=13):
  '''
  get a mask of the difference between two frames
  '''
  transformed_frame = cv2.warpPerspective(frame, perspective_matrix, frame_size)
  transformed_background = cv2.warpPerspective(background, perspective_matrix, frame_size)

  difference = cv2.absdiff(transformed_background, transformed_frame)
  blur = cv2.GaussianBlur(difference, (5, 5), 0)
  for _ in range(10):
      blur = cv2.GaussianBlur(blur, (9, 9), 1)
  blur = cv2.bilateralFilter(blur, 9, 75, 75)
  _ , thresh = cv2.threshold(blur, triangle, 255, 0)
  gray = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
  # Ensure that the image is binary with only black and white pixels
  mask = cv2.threshold(gray, 254, 255, cv2.THRESH_BINARY)[1]
  mask = cv2.erode(mask, None, iterations=2)
  mask = cv2.dilate(mask, None, iterations=2)
  return mask, transformed_frame, transformed_background


