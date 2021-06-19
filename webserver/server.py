import asyncio
import pathlib

import aiohttp_cors
from aiohttp import web

from webserver.controllers import TelloController, VideoController
from webserver.routers import routes
from webserver.video import VideoImageTrack, VideoSource
from webserver.websocket import WebSocketManager

PROJECT_ROOT = pathlib.Path(__file__).parent


def set_cors(my_app, offer_route):
	cors = aiohttp_cors.setup(my_app)
	cors.add(offer_route, {
		"*": aiohttp_cors.ResourceOptions(
			allow_credentials=True,
			expose_headers=("X-Custom-Server-Header",),
			allow_headers=("X-Requested-With", "Content-Type"),
			max_age=3600,
		)
	})


def setup_server_runner(video: VideoSource):
	app = web.Application()
	video_controller = VideoController(VideoImageTrack(video))
	offer_route = app.router.add_post("/offer", video_controller.offer)
	routes.add_class_routes(TelloController())
	app.add_routes([
		web.get('/ws', WebSocketManager.websocket_handler)
	])
	app.add_routes(routes)
	app.router.add_static('/static/', path=PROJECT_ROOT / 'static', name='static')
	set_cors(app, offer_route)
	app.on_shutdown.append(video_controller.on_shutdown)
	return web.AppRunner(app)


def run_server(runner):
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	loop.run_until_complete(runner.setup())
	site = web.TCPSite(runner, 'localhost', 8080)
	loop.run_until_complete(site.start())
	loop.run_forever()
	print("Access http://0.0.0.0:8080/static/index.html")


if __name__ == "__main__":
	run_server(setup_server_runner(VideoSource()))
