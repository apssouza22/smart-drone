import cv2
import mediapipe as mp
import time
import math


class PoseDetector:

	def __init__(self, mode=False, upBody=False, smooth=True, detectionCon=0.75, trackCon=0.5):

		self.right_hand_positions = []
		self.left_hand_positions = []
		self.pose_positions = []
		self.mode = mode
		self.upBody = upBody
		self.smooth = smooth
		self.detectionCon = detectionCon
		self.trackCon = trackCon

		self.mpDraw = mp.solutions.drawing_utils
		self.mpPose = mp.solutions.holistic
		self.pose = self.mpPose.Holistic(
			self.mode,
			self.upBody,
			self.smooth,
			self.detectionCon,
			self.trackCon
		)
		self.results = None
		self.pose_positions = []

	def find_pose(self, img, draw=True):
		img.flags.writeable = False
		self.results = self.pose.process(img)
		img.flags.writeable = True
		if self.results.pose_landmarks:
			if draw:
				self.draw_landmarks(
					img,
					self.results.pose_landmarks,
					self.mpPose.POSE_CONNECTIONS
				)

	def draw_landmarks(self, img, landmarks, connections):
		self.mpDraw.draw_landmarks(img, landmarks, connections)

	def find_pose_position(self, img, draw=True):
		self.pose_positions = []
		if self.results.pose_landmarks:
			for id, lm in enumerate(self.results.pose_landmarks.landmark):
				h, w, c = img.shape
				# print(id, lm)
				cx, cy = int(lm.x * w), int(lm.y * h)
				self.pose_positions.append([id, cx, cy])
				if draw:
					cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

			self.populate_neck_mid_hip()

		return self.pose_positions

	def find_left_hand_position(self, img, draw=True):
		self.left_hand_positions = []
		if self.results.left_hand_landmarks:
			for id, lm in enumerate(self.results.left_hand_landmarks.landmark):
				h, w, c = img.shape
				# print(id, lm)
				cx, cy = int(lm.x * w), int(lm.y * h)
				self.left_hand_positions.append([id, cx, cy])
				if draw:
					cv2.circle(img, (cx, cy), 5, (255, 255, 0), cv2.FILLED)
		return self.left_hand_positions

	def find_right_hand_position(self, img, draw=True):
		self.right_hand_positions = []
		if self.results.right_hand_landmarks:
			for id, lm in enumerate(self.results.right_hand_landmarks.landmark):
				h, w, c = img.shape
				# print(id, lm)
				cx, cy = int(lm.x * w), int(lm.y * h)
				self.right_hand_positions.append([id, cx, cy])
				if draw:
					cv2.circle(img, (cx, cy), 5, (255, 255, 0), cv2.FILLED)

		return self.right_hand_positions

	def populate_neck_mid_hip(self):
		left_shoulder = self.pose_positions[11]
		right_shoulder = self.pose_positions[12]
		left_hip = self.pose_positions[23]
		right_hip = self.pose_positions[24]
		neck_x, neck_y = (left_shoulder[1] + right_shoulder[1]) // 2, (left_shoulder[2] + right_shoulder[2]) // 2
		hip_x, hip_y = (left_hip[1] + right_hip[1]) // 2, (left_hip[2] + right_hip[2]) // 2
		self.pose_positions.append([33, neck_x, neck_y])
		self.pose_positions.append([34, hip_x, hip_y])

	def find_angle(self, img, p1, p2, p3, draw=True):
		# Get the landmarks - (id, x, y) ignore id
		x1, y1 = self.pose_positions[p1][1:]
		x2, y2 = self.pose_positions[p2][1:]
		x3, y3 = self.pose_positions[p3][1:]

		# Calculate the Angle
		radius = math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2)
		angle = math.degrees(radius)
		if angle < 0:
			angle += 360

		# print(angle)

		# Draw
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
		return angle

	def draw_all(self, image):
		self.draw_landmarks(image, self.results.left_hand_landmarks, self.mpPose.HAND_CONNECTIONS)
		self.draw_landmarks(image, self.results.right_hand_landmarks, self.mpPose.HAND_CONNECTIONS)
		# self.draw_landmarks(image, self.results.face_landmarks, self.mpPose.FACE_CONNECTIONS)
		# self.draw_landmarks(image, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)


def main():
	cap = cv2.VideoCapture(0)
	pTime = 0
	detector = PoseDetector()
	while cap.isOpened():
		success, img = cap.read()
		if not success:
			print("Ignoring empty camera frame.")
			continue
		img = detector.find_pose(img)
		landmarks_points = detector.find_left_hand_position(img, draw=False)
		if len(landmarks_points) != 0:
			# https://google.github.io/mediapipe/images/mobile/pose_tracking_full_body_landmarks.png
			cv2.circle(img, (landmarks_points[14][1], landmarks_points[14][2]), 15, (0, 0, 255), cv2.FILLED)

		cTime = time.time()
		fps = 1 / (cTime - pTime)
		pTime = cTime

		cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3,
					(255, 0, 0), 3)

		cv2.imshow("Image", img)
		cv2.waitKey(1)


if __name__ == "__main__":
	main()
