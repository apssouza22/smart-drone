import time

import aiohttp
from aiohttp import web


class WebSocketManager:
	sockets = []
	msg = ""
	last_msg = ""

	async def handle(self) -> None:
		while True:
			if self.msg != self.last_msg:
				await self.send("{\"position\":\"" + self.msg + "\"}")
				self.last_msg = self.msg
				time.sleep(0.25)

	async def send(self, message: str):
		for socket in WebSocketManager.sockets:
			await socket.send_str(message)

	@staticmethod
	async def websocket_handler(request):
		ws = web.WebSocketResponse()
		await ws.prepare(request)

		WebSocketManager.sockets.append(ws)
		async for msg in ws:
			if msg.type == aiohttp.WSMsgType.TEXT:
				if msg.data == 'close':
					await ws.close()
				else:
					pass
			elif msg.type == aiohttp.WSMsgType.ERROR:
				print('ws connection closed with exception %s' %
					  ws.exception())

		print('websocket connection closed')
		WebSocketManager.sockets.remove(ws)
		return ws
