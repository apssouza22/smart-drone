import cv2
from aiortc import VideoStreamTrack
from av import VideoFrame


class VideoSource:
	def __init__(self):
		self.cap = cv2.VideoCapture(0)
		self.frame = None

	def read(self):
		if self.frame is None:
			return self.cap.read()[1]
		return self.frame

	def update(self, frame):
		self.frame = frame


class VideoImageTrack(VideoStreamTrack):

	def __init__(self, video_source):
		super().__init__()
		self.video_source = video_source

	async def recv(self):
		pts, time_base = await self.next_timestamp()
		image = self.video_source.read()

		frame = VideoFrame.from_ndarray(image, format="bgr24")
		frame.pts = pts
		frame.time_base = time_base
		return frame
