import asyncio
import json
import sys

import ujson
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack

from common.pygamescreen import PyGameScreen
from webserver.routers import routes
from webserver.video import VideoImageTrack


class Controller:
	def json(self, data, status: int = 200):
		return web.json_response(data, status=status, dumps=ujson.dumps)


class TelloController(Controller):
	def __init__(self, control: PyGameScreen):
		super().__init__()
		self.control = control

	@routes.get("/api/test")
	async def test(self, request):
		print(request)
		return self.json(["test"])

	@routes.get("/api/control")
	async def command(self, request):
		result = {'success': 'ok'}
		if request.rel_url.query['command'] != "release":
			self.control.controls_keypress[int(request.rel_url.query['value'])]()
			return self.json(result)

		for key, fn in self.control.controls_keyrelease.items():
			fn()

		return self.json(result)


class VideoController(Controller):

	def __init__(self, video_tracker: VideoImageTrack):
		super().__init__()
		self.video_tracker = video_tracker
		self.pcs = set()

	async def offer(self, request):
		params = await request.json()
		offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
		pc = RTCPeerConnection()
		self.pcs.add(pc)

		@pc.on("iceconnectionstatechange")
		async def on_iceconnectionstatechange():
			print("ICE connection state is %s" % pc.iceConnectionState)
			if pc.iceConnectionState == "failed":
				await pc.close()
				self.pcs.discard(pc)

		await pc.setRemoteDescription(offer)
		pc.addTrack(self.video_tracker)

		answer = await pc.createAnswer()
		await pc.setLocalDescription(answer)

		return web.Response(
			content_type="application/json",
			text=json.dumps({
				"sdp": pc.localDescription.sdp,
				"type": pc.localDescription.type
			}),
		)

	async def on_shutdown(self, app):
		coros = [pc.close() for pc in self.pcs]
		await asyncio.gather(*coros)
		self.pcs.clear()
