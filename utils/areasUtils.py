import cv2
import math
import pickle

line_length = 400
step_size = 1
num_rings = 6
num_segments = 20

#Text CV2
font                   = cv2.FONT_HERSHEY_COMPLEX_SMALL
bottomLeftCornerOfText = (5,680)
fontScale              = 1.1
fontColor              = (255,255,255)
thickness              = 2
lineType               = 2

def editAreas(frame, center, rings, segments):
	'''
	Edit dartboard areas by hand
	'''
	index = 0
	mode = None
	cv2.namedWindow("Dartboard Areas")
	while(True):
		frame_copy = frame.copy()
		drawRings(frame_copy, rings, center, mode, index)
		drawSegments(frame_copy, segments, center, mode, index)
		drawCenter(frame_copy, center, mode)
		drawText(frame_copy)
		cv2.imshow("Dartboard Areas", frame_copy)
		key = cv2.waitKey(0) & 0xFF
		if(key == ord('q')):
			break;
		elif(key == ord('z')):
			mode = 'center'
			index = 0
		elif(key == ord('x')):
			mode = 'rings'
			index = 0
		elif(key == ord('c')):
			mode = 'segments'
			index = 0
		elif(key == ord('w')):
			if(mode == 'center'):
				center[1] = max(0, center[1] - step_size)
			elif(mode == 'rings'):
				rings[index] = rings[index] + step_size
			elif(mode == 'segments'):
				segments[index] = segments[index] - step_size % 360
		elif(key == ord('s')):
			if(mode == 'center'):
				center[1] = center[1] + step_size
			elif(mode == 'rings'):
				rings[index] = max(0, rings[index] - step_size)
			elif(mode == 'segments'):
				segments[index] = segments[index] + step_size % 360
		elif(key == ord('a')):
			if(mode == 'center'):
				center[0] = max(0, center[0] - step_size)
			elif(mode == 'rings'):
				index = max(0, index-1)
			elif(mode == 'segments'):
				index = max(0, index-1)
		elif(key == ord('d')):
			if(mode == 'center'):
				center[0] = center[0] + step_size
			elif(mode == 'rings'):
				index = min(index+1, num_rings-1)
			elif(mode == 'segments'):
				index = min(index+1, num_segments-1)
	cv2.destroyWindow("Dartboard Areas")
	
	print("Center: ",center)
	print("Rings: ", rings)
	print("Segments: ", segments)
	with open("pickleFiles\\dartboard_config.pkl", "wb") as f:
		pickle.dump({
		"center": center,
		"rings": rings,
		"segments": segments
	}, f)

def drawCenter(frame, center, mode):
	'''
	Draw dartboard's center
	'''
	color = (0,0,255) if (mode == 'center') else (255,255,0)
	thick = 3 if (mode == 'center') else 1
	cv2.drawMarker(frame, center, color, cv2.MARKER_TILTED_CROSS, 2, thick)

def drawRings(frame, rings, center, mode, index):
	'''
	Draw dartboard's rings
	'''
	for i, ring in enumerate(rings):
		color = (0,0,255) if (mode == 'rings' and i == index) else (255,255,0)
		thick = 2 if (mode == 'rings' and i == index) else 1
		cv2.circle(frame, center, ring, color, thick)

def drawSegments(frame, segments, center, mode, index):
	'''
	Draw dartboard's segments
	'''
	for i, segment in enumerate(segments):
		angle_rad = math.radians(segment)
		segment_x = int(center[0] + line_length * math.cos(angle_rad))
		segment_y = int(center[1] + line_length * math.sin(angle_rad))
		point = (segment_x, segment_y)
		color = (0,0,255) if (mode == 'segments' and i == index) else (255,255,0)
		thick = 2 if (mode == 'segments' and i == index) else 1
		cv2.line(frame, center, point, color, thick)

def drawText(frame):
	'''
	Draw Info Text
	'''
	cv2.putText(frame,'Q-Quit  |WASD|  Z-Center | X-Rings | C-Segments', 
		bottomLeftCornerOfText, 
		font, 
		fontScale,
		fontColor,
		thickness,
		lineType
	)