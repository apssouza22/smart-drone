from typing import (
	Any,
)
from aiohttp import web
import inspect


class ClassRouteTableDef(web.RouteTableDef):
	def __repr__(self) -> str:
		return "<ClassRouteTableDef count={}>".format(len(self._items))

	def route(self,
			  method: str,
			  path: str,
			  **kwargs: Any):
		def inner(handler: Any) -> Any:
			# Is Any rather than _HandlerType because of mypy limitations, see
			# https://github.com/python/mypy/issues/3882 and
			# https://github.com/python/mypy/issues/2087
			handler.route_info = (method, path, kwargs)
			return handler

		return inner

	def add_class_routes(self, instance: Any) -> None:
		def predicate(member: Any) -> bool:
			return all((inspect.iscoroutinefunction(member), hasattr(member, "route_info")))

		for _, handler in inspect.getmembers(instance, predicate):
			method, path, kwargs = handler.route_info
			super().route(method, path, **kwargs)(handler)


routes = ClassRouteTableDef()
