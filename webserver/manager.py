import threading

from webserver.server import setup_server_runner, run_http_server, run_socket_server
from webserver.video import VideoSource
from webserver.websocket import WebSocketManager


class WebControlManager:
	def __init__(self, enable_http, enable_socket):
		self.is_socket_enabled = enable_socket
		self.is_http_enabled = enable_http
		self.video_source = VideoSource()
		self.socket = WebSocketManager()

	def start_http(self):
		if self.is_http_enabled:
			server_runner = setup_server_runner(self.video_source)
			td = threading.Thread(target=run_http_server, args=(server_runner,))
			td.start()

	def start_socket(self):
		if self.is_socket_enabled:
			td2 = threading.Thread(target=run_socket_server, args=(self.socket,))
			td2.start()

	def send_frame(self, frame):
		self.video_source.update(frame)

	def send_msg(self, msg):
		self.socket.msg = msg
