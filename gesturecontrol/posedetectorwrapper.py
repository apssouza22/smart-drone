"""
    My own layer above the official Openpose python wrapper : https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/modules/python_module.md
    Tested only on ubuntu.
    Modify MODEL_FOLDER to point to the directory where the models are installed
"""

import argparse
from collections import namedtuple

import cv2

from common import posemodule as pm
from common.fps import FPS

body_kp_id_to_name = {
	0: "nose",
	1: "left_eye_inner",
	2: "left_eye",
	3: "left_eye_out",
	4: "right_eye_inner",
	5: "right_eye",
	6: "right_eye_out",
	7: "left_ear",
	8: "right_ear",
	9: "mouth_left",
	10: "mouth_right",
	11: "left_shoulder",
	12: "right_shoulder",
	13: "left_elbow",
	14: "right_elbow",
	15: "left_wrist",
	16: "right_wrist",
	17: "left_pinky",
	18: "right_pinky",
	19: "left_index",
	20: "right_index",
	21: "left_thumb",
	22: "right_thumb",
	23: "left_hip",
	24: "right_hip",
	25: "left_knee",
	26: "right_knee",
	27: "left_ankle",
	28: "right_ankle",
	29: "left_heel",
	30: "right_heel",
	31: "left_foot_index",
	32: "right_foot_index",
	33: "neck",
	34: "mid_hip",
}

body_kp_name_to_id = {v: k for k, v in body_kp_id_to_name.items()}

Pair = namedtuple('Pair', ['p1', 'p2', 'color'])
color_right_side = (0, 255, 0)
color_left_side = (0, 0, 255)
color_middle = (0, 255, 255)
color_face = (255, 255, 255)

pairs_head = [
	Pair("nose", "right_eye_out", color_right_side),
	Pair("nose", "left_eye_out", color_left_side),
	Pair("right_eye_out", "right_ear", color_right_side),
	Pair("left_eye_out", "left_ear", color_left_side)
]

pairs_upper_limbs = [
	Pair("neck", "right_shoulder", color_right_side),
	Pair("right_shoulder", "right_elbow", color_right_side),
	Pair("right_shoulder", "right_hip", color_right_side),
	Pair("right_elbow", "right_wrist", color_right_side),
	Pair("neck", "left_shoulder", color_left_side),
	Pair("left_shoulder", "left_elbow", color_left_side),
	Pair("left_shoulder", "left_hip", color_left_side),
	Pair("left_elbow", "left_wrist", color_left_side)
]

pairs_lower_limbs = [
	Pair("mid_hip", "right_hip", color_right_side),
	Pair("right_hip", "right_knee", color_right_side),
	Pair("right_knee", "right_ankle", color_right_side),
	Pair("right_ankle", "right_heel", color_right_side),
	Pair("mid_hip", "left_hip", color_left_side),
	Pair("left_hip", "left_knee", color_left_side),
	Pair("left_knee", "left_ankle", color_left_side),
	Pair("left_ankle", "left_heel", color_left_side)
]

pairs_spine = [
	Pair("nose", "neck", color_middle),
	Pair("neck", "mid_hip", color_middle)
]

pairs_feet = [
	Pair("right_ankle", "right_foot_index", color_right_side),
	Pair("right_ankle", "right_heel", color_right_side),
	Pair("left_ankle", "left_foot_index", color_left_side),
	Pair("left_ankle", "left_heel", color_left_side)
]

pairs_body = pairs_head + pairs_upper_limbs + pairs_lower_limbs + pairs_spine + pairs_feet


class PoseDetectorWrapper:

	def __init__(self):
		"""
        openpose_rendering : if True, rendering is made by original Openpose library. Otherwise rendering is to the
        responsability of the user (~0.2 fps faster)
        """

		self.pose_detector = pm.PoseDetector()
		self.pose_kps = []
		self.left_hand_kps = []
		self.right_hand_kps = []

	def eval(self, image):
		self.pose_detector.find_pose(image, False)
		self.pose_kps = self.pose_detector.find_pose_position(image, False)
		self.left_hand_kps = self.pose_detector.find_left_hand_position(image, True)
		self.right_hand_kps = self.pose_detector.find_right_hand_position(image, True)
		self.pose_detector.draw_all(image)

	def draw_body(self, frame, pairs=pairs_body, thickness=3, color=None):
		"""Draw on 'frame' pairs of keypoints"""
		self.draw_pairs_points(frame, self.pose_kps, body_kp_name_to_id, pairs, thickness, color)

	@staticmethod
	def draw_pairs_points(frame, person, kp_name_to_id, pairs, thickness=3, color=None):
		"""Draw on 'frame' pairs of keypoints"""

		for pair in pairs:
			pose1 = person[kp_name_to_id[pair.p1]]
			pose2 = person[kp_name_to_id[pair.p2]]
			p1_x, p1_y = pose1[1], pose1[2]
			p2_x, p2_y = pose2[1], pose2[2]

			p1_conf, p2_conf = (p1_x + p2_x) // 2, (p1_y + p2_y) // 2
			if p1_conf != 0 and p2_conf != 0:
				col = color if color else pair.color
				cv2.line(frame, (p1_x, p1_y), (p2_x, p2_y), col, thickness)

	def get_body_kp(self, kp_name="nose"):
		"""Return the coordinates of a keypoint named 'kp_name', or None if keypoint not detected"""
		try:
			_, x, y = self.pose_kps[body_kp_name_to_id[kp_name]]
		except:
			print(f"get_body_kp: invalid kp_name '{kp_name}'")
			return None
		if x or y:
			return int(x), int(y)
		else:
			return None


if __name__ == '__main__':

	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--input", default="0", help="input video file (0, filename, rtsp://admin:admin@192.168.1.71/1, ...")
	ap.add_argument("-n", "--number_people_max", default=-1, help="limit the number of people detected")
	ap.add_argument("-f", "--face", action="store_true", help="enable face keypoint detection")
	ap.add_argument("--frt", type=float, default=0.4, help="face rendering threshold")
	ap.add_argument("-o", "--output", help="path to output video file")
	ap.add_argument("-r", "--rendering", default=True, action="store_true", help="display in a separate window the original rendering made by Openpose lib")

	args = ap.parse_args()

	if args.input.isdigit():
		args.input = int(args.input)
		w_h_list = [(960, 720), (640, 480), (320, 240)]
		w_h_idx = 0

	# Read video
	video = cv2.VideoCapture(args.input)
	if isinstance(args.input, int):
		w, h = w_h_list[w_h_idx]
		video.set(cv2.CAP_PROP_FRAME_WIDTH, w)
		video.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

	ok, frame = video.read()
	h, w, _ = frame.shape
	if args.output:
		fourcc = cv2.VideoWriter_fourcc(*"MJPG")
		out = cv2.VideoWriter(args.output, fourcc, 30, (w, h))

	my_op = PoseDetectorWrapper()

	fps = FPS()
	while True:
		# Read a new frame
		ok, frame = video.read()
		if not ok:
			break
		fps.update()
		frame = frame.copy()
		nb_persons, body_kps, face_kps = my_op.eval(frame)

		if len(body_kps) == 0:
			continue
		my_op.draw_body(frame)
		if args.face:
			my_op.draw_face(frame)
			my_op.draw_eyes(frame)

		fps.display(frame)
		cv2.imshow("Rendering", frame)
		if args.output:
			out.write(frame)
		# Exit if ESC pressed
		k = cv2.waitKey(1) & 0xff
		if k == 27:
			break
		elif k == 32:  # space
			cv2.waitKey(0)
		elif k == ord("s") and isinstance(args.input, int):
			w_h_idx = (w_h_idx + 1) % len(w_h_list)
			w, h = w_h_list[w_h_idx]
			video.set(cv2.CAP_PROP_FRAME_WIDTH, w)
			video.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

	video.release()
	cv2.destroyAllWindows()
