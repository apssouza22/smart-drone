import math
from math import degrees, atan2, hypot

import cv2


def distance(A, B):
	"""
		Calculate the square of the distance between points A and B
	"""
	length = hypot(B[0] - A[0], B[1] - A[1])
	return int(length)


def angle(A, B, C):
	"""
		Calculate the angle between segment(A,p2) and segment (p2,p3)
	"""
	if A is None or B is None or C is None:
		return None
	return degrees(atan2(C[1] - B[1], C[0] - B[0]) - atan2(A[1] - B[1], A[0] - B[0])) % 360


def vertical_angle(img, p1, p2, p3, draw=False):
	"""
		Calculate the angle between segment(A,B) and vertical axe
	"""
	x1, y1 = p1[0], p1[1]
	x2, y2 = p2[0], p2[1]
	x3, y3 = p3[0], p3[1]
	# Calculate the Angle
	radius = math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2)
	angle = math.degrees(radius)
	if angle < 0:
		angle += 360
	# print(angle)

	if draw:
		cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
		cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
		cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
		cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)
		cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
		cv2.circle(img, (x2, y2), 15, (0, 0, 255), 2)
		cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
		cv2.circle(img, (x3, y3), 15, (0, 0, 255), 2)
		cv2.putText(img, str(int(angle)), (x2 - 50, y2 + 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

	return int(angle)


class PoseChecker(object):

	def __init__(self, controller):
		self.controller = controller
		self.load_limbs(controller)
		self.shoulders_width = None
		if self.r_shoulder and self.l_shoulder:
			self.shoulders_width = distance(self.r_shoulder, self.l_shoulder)
			controller.shoulders_width = self.shoulders_width

	def get_pose(self, frame):
		"""
			Check if we detect a pose in the body detected by Openpose
		"""
		left_hand_up = self.neck and self.l_wrist and self.l_wrist[1] < self.neck[1]
		right_hand_up = self.neck and self.r_wrist and self.r_wrist[1] < self.neck[1]

		if right_hand_up and left_hand_up:
			pose = self.get_both_arms_pose()
			if pose:
				return pose

			pose = self.get_both_hands_pose(self.controller)
			if pose:
				return pose

		if right_hand_up and not left_hand_up:
			shoulder_wrist_angle_right = vertical_angle(frame, self.r_shoulder, self.r_elbow, self.r_wrist, True)
			pose = self.get_right_arm_pose(self.controller, shoulder_wrist_angle_right)
			if pose:
				return pose

			pose = self.get_right_hand_pose(self.controller)
			if pose:
				return pose

		if not right_hand_up and left_hand_up:
			shoulder_wrist_angle_left = vertical_angle(frame, self.l_shoulder, self.l_elbow, self.l_wrist, True)
			pose = self.get_left_arm_pose(self.controller, shoulder_wrist_angle_left)
			if pose:
				return pose

			pose = self.get_left_hand_pose(self.controller)
			if pose:
				return pose

		# Both wrists under the neck
		if self.neck and self.shoulders_width and self.r_wrist and self.l_wrist:
			near_dist = self.shoulders_width / 3
			if distance(self.r_wrist, self.neck) < near_dist and distance(self.l_wrist, self.neck) < near_dist:
				return "HANDS_ON_NECK"
		return None

	def get_left_arm_pose(self, controller, vert_angle_left_arm):
		return None
		# Left ear and left hand on the same side
		if self.l_ear and (self.l_ear[0] - self.neck[0]) * (self.l_wrist[0] - self.neck[0]) > 0:
			if vert_angle_left_arm:
				if vert_angle_left_arm < 50:
					return "LEFT_ARM_UP_CLOSED"
				if 80 < vert_angle_left_arm < 110:
					return "LEFT_ARM_UP_OPEN"
		elif self.r_ear and self.shoulders_width and distance(self.l_wrist, self.r_ear) < self.shoulders_width / 4:
			# Left hand close to right ear
			return "LEFT_HAND_ON_RIGHT_EAR"
		return None

	def get_right_arm_pose(self, controller, vert_angle_right_arm):
		return None
		# Right ear and right hand on the same side
		if self.r_ear and (self.r_ear[0] - self.neck[0]) * (self.r_wrist[0] - self.neck[0]) > 0:
			if vert_angle_right_arm:
				if vert_angle_right_arm < 290 and vert_angle_right_arm > 260:
					return "RIGHT_ARM_UP_OPEN"
				if 15 < vert_angle_right_arm > 320:
					return "RIGHT_ARM_UP_CLOSED"
		elif self.l_ear and self.shoulders_width and distance(self.r_wrist, self.l_ear) < self.shoulders_width / 4:
			# Right hand close to left ear
			return "RIGHT_HAND_ON_LEFT_EAR"

		return None

	def get_both_arms_pose(self):
		return None
		# Both hands up
		# Check if both hands are on the ears
		if self.r_ear and self.l_ear:
			ear_dist = distance(self.r_ear, self.l_ear)
			if distance(self.r_wrist, self.r_ear) < ear_dist / 3 and distance(self.l_wrist, self.l_ear) < ear_dist / 3:
				return "HANDS_ON_EARS"

		# Check if boths hands are closed to each other and above ears
		# (check right hand is above right ear is enough since hands are closed to each other)
		if self.shoulders_width and self.r_ear:
			near_dist = self.shoulders_width / 3
			if self.r_ear[1] > self.r_wrist[1] and distance(self.r_wrist, self.l_wrist) < near_dist:
				return "CLOSE_HANDS_UP"

		return None

	def load_limbs(self, controller):
		self.neck = controller.pose_detector.get_body_kp("neck")
		self.r_wrist = controller.pose_detector.get_body_kp("right_wrist")
		self.l_wrist = controller.pose_detector.get_body_kp("left_wrist")
		self.r_elbow = controller.pose_detector.get_body_kp("right_elbow")
		self.l_elbow = controller.pose_detector.get_body_kp("left_elbow")
		self.r_shoulder = controller.pose_detector.get_body_kp("right_shoulder")
		self.l_shoulder = controller.pose_detector.get_body_kp("left_shoulder")
		self.r_ear = controller.pose_detector.get_body_kp("right_ear")
		self.l_ear = controller.pose_detector.get_body_kp("left_ear")

	def get_left_hand_pose(self, controller):
		if len(controller.pose_detector.left_hand_kps) == 0:
			return None

		fingers = self.get_finger_counts(controller.pose_detector.left_hand_kps)
		return "LEFT_HAND_FINGERS_UP_{}".format(fingers)

	def get_right_hand_pose(self, controller):
		if len(controller.pose_detector.right_hand_kps) == 0:
			return None

		fingers = self.get_finger_counts(controller.pose_detector.right_hand_kps, True)
		return "RIGHT_HAND_FINGERS_UP_{}".format(fingers)

	@staticmethod
	def get_finger_counts(hand_kps, right=False):
		fingers = []
		# fingers tips ids [thumb, indicator...]
		finger_tip_ids = [4, 8, 12, 16, 20]
		# Thumb
		thumb_bottom = 2
		if len(hand_kps) < 1:
			return -1

		finger_position = hand_kps[finger_tip_ids[0]]

		if len(finger_position) > 1:
			if right:
				thumbs_up = finger_position[1] > hand_kps[thumb_bottom][1]
			else:
				thumbs_up = finger_position[1] < hand_kps[thumb_bottom][1]

		if thumbs_up:
			fingers.append(1)
		else:
			fingers.append(0)
		# 4 Fingers
		for id in range(1, 5):
			if hand_kps[finger_tip_ids[id]][2] < hand_kps[finger_tip_ids[id] - 2][2]:
				fingers.append(1)
			else:
				fingers.append(0)
		return fingers.count(1)

	def get_both_hands_pose(self, controller):
		if len(controller.pose_detector.right_hand_kps) == 0:
			return None

		fingers_right = self.get_finger_counts(controller.pose_detector.right_hand_kps, True)
		fingers_left = self.get_finger_counts(controller.pose_detector.left_hand_kps, False)
		if fingers_right != fingers_left:
			return None

		return "BOTH_HAND_FINGERS_UP_{}".format(fingers_right)
