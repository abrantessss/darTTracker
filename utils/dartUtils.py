import numpy as np
import cv2

from utils import utils

def compareMasks(mask1, mask2, threshold=0.998):
		"""
		Compare two binary masks and check if they are almost identical.
		:return: True if the masks are almost identical, False otherwise.
		"""
		identical_pixels = np.sum(mask1 == mask2)
		total_pixels = mask1.size
		similarity = identical_pixels / total_pixels
		#print(f"Similarity: {similarity*100}%")
		return similarity >= threshold

def findDartTip(contour, thresholdMin=10):
	"""
	choose the probable dart tip based on a threshold distance
	"""
	left_point_tip, right_point_tip, top_point_tip, bottom_point_tip = extremePoints(contour)
	triangle_point_tip, triangle_points = triangleMethod(contour)
	distanceLeft = np.linalg.norm(left_point_tip-triangle_point_tip)
	distanceRight = np.linalg.norm(right_point_tip-triangle_point_tip)
	distanceTop = np.linalg.norm(top_point_tip-triangle_point_tip)
	distanceBot = np.linalg.norm(bottom_point_tip-triangle_point_tip)
	distances = [distanceLeft, distanceRight, distanceTop, distanceBot]
	if any(d <= thresholdMin for d in distances):
		#Used most of the times
		if(utils.debug):
			print("Debug | Triangle Method")
		dart_tip = triangle_point_tip.astype(np.int32)
	elif(distanceLeft <= thresholdMin*1.5):
		if(utils.debug):
			print("Debug | Triangle Method Left Side")
		dart_tip = triangle_point_tip.astype(np.int32)
	elif(distanceLeft <= thresholdMin*3):
		if(utils.debug):
			print("Debug | Left Point Method")
		dart_tip = left_point_tip.astype(np.int32)
	else:
		if(utils.debug):
			print("Debug | Centroid Method")
		centroide_x = int(np.mean(contour[:, 0, 0]))
		centroide_y = int(np.mean(contour[:, 0, 1]))
		dart_tip = np.array([centroide_x, centroide_y], dtype=np.int32)

	return dart_tip, triangle_points
	
def extremePoints(contour):
	"""
	find the the tip of the dart by finding the most left point of the contour
	"""
	extLeft = np.array(contour[contour[:, :, 0].argmin()][0], dtype=np.int32)
	extRight = np.array(contour[contour[:, :, 0].argmax()][0], dtype=np.int32)
	extTop = np.array(contour[contour[:, :, 1].argmin()][0], dtype=np.int32)
	extBot = np.array(contour[contour[:, :, 1].argmax()][0], dtype=np.int32)
	return extLeft, extRight, extTop, extBot

def triangleMethod(contour):
	"""
	find the tip of the dart by finding the point with the largest distance to the other two points
	then ajusts it by a factor
	"""
	triangle = cv2.minEnclosingTriangle(contour)
	triangle_points = np.int32(triangle[1].reshape(3,2))

	dart_point = triangle_points[0]
	rest_pts = [triangle_points[1], triangle_points[2]]
	dist_1_2 = np.linalg.norm(triangle_points[0] - triangle_points[1])
	dist_1_3 = np.linalg.norm(triangle_points[0] - triangle_points[2])
	dist_2_3 = np.linalg.norm(triangle_points[1] - triangle_points[2])

	if dist_1_2 > dist_1_3 and dist_2_3 > dist_1_3:
		dart_point = triangle_points[1]
		rest_pts = [triangle_points[0], triangle_points[2]]
	elif dist_1_3 > dist_1_2 and dist_2_3 > dist_1_2:
		dart_point = triangle_points[2]
		rest_pts = [triangle_points[0], triangle_points[1]]

	dart_point = dart_point.ravel()
	pt1, pt2 = rest_pts[0].ravel(), rest_pts[1].ravel()

	center = (pt1 + pt2) / 2
	center = center.astype(np.int32)
	k = -0.21  # scaling factor for position adjustment of dart tip
	vect = (dart_point - center)
	dart_tip = dart_point + k * vect

	return dart_tip, triangle_points

def drawDetectedDart(dart_point, triangle, frame):   
		"""
		Draw the detected darts on the threshold image as triangle and a dot indicating the dart tip
		"""
		# Display the Dart point
		cv2.circle(frame, dart_point.astype(np.int32), 4, (0, 155, 255), -1)
		# Display the triangles
		cv2.line(frame, triangle[0].ravel(), triangle[1].ravel(), (255, 0, 255), 2)
		cv2.line(frame, triangle[1].ravel(), triangle[2].ravel(), (255, 0, 255), 2)
		cv2.line(frame, triangle[2].ravel(), triangle[0].ravel(), (255, 0, 255), 2)


def getPolarCoords(dart_tip, center):
	"""
	Convert dart tip point to polar coordinates relative to the center point.
	"""
	# Extract coordinates
	x_c, y_c = center
	x, y = dart_tip
	
	# Calculate radius (distance from center)
	r = np.sqrt((x - x_c)**2 + (y - y_c)**2)
	
	# Calculate angle in radians
	theta = np.arctan2(y - y_c, x - x_c)
	theta_deg = np.degrees(theta)
	if theta_deg < 0:
		theta_deg += 360

	return r, theta_deg

def evaluateThrow(radius, angle, rings, segments):
	"""
	Evaluate the value of the thrown dart 
	"""
	list_fields = {
		(0.0001, segments[0]): 6,
		(segments[0]+0.0001, segments[1]): 10,
		(segments[1]+0.0001, segments[2]): 15,
		(segments[2]+0.0001, segments[3]): 2,
		(segments[3]+0.0001, segments[4]): 17,
		(segments[4]+0.0001, segments[5]): 3,
		(segments[5]+0.0001, segments[6]): 19,
		(segments[6]+0.0001, segments[7]): 7,
		(segments[7]+0.0001, segments[8]): 16,
		(segments[8]+0.0001, segments[9]): 8,
		(segments[9]+0.0001, segments[10]): 11,
		(segments[10]+0.0001, segments[11]): 14,
		(segments[11]+0.0001, segments[12]): 9,
		(segments[12]+0.0001, segments[13]): 12,
		(segments[13]+0.0001, segments[14]): 5,
		(segments[14]+0.0001, segments[15]): 20,
		(segments[15]+0.0001, segments[16]): 1,
		(segments[16]+0.0001, segments[17]): 18,
		(segments[17]+0.0001, segments[18]): 4,
		(segments[18]+0.0001, segments[19]): 13,
		(segments[19]+0.0001, 360+0.0001): 6
	}
	multiplier = 1
	score_point = 0
	if radius < rings[5]:
		for limits in list_fields:
			if limits[0] <= angle <= limits[1]:
				score_point = list_fields[limits]

	if radius <= rings[0]:
		score_point = 50 #inner bull
	elif radius <= rings[1]:
		score_point = 25 #outer bull
	elif radius <= rings[2]:
		multiplier = 1
	elif radius <= rings[3]:
		multiplier = 3
	elif radius <= rings[4]:
		multiplier = 1
	elif radius <= rings[5]:
		multiplier = 2

	score_point = score_point*multiplier

	return score_point

def getPoints(dart_tip, center, rings, segments):
	radius, deg = getPolarCoords(dart_tip, center)
	score_point = evaluateThrow(radius, deg, rings, segments)
	return score_point, [radius, deg]
