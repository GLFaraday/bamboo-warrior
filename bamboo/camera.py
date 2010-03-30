from bamboo.geom import Rect
from bamboo.scene import Viewport


class Camera(object):
	"""A camera generates a viewport - ie. a place in the scene"""
	def __init__(self, width, height):
		self.width = width
		self.height = height

	def get_viewport(self):
		raise NotImplementedError("Subclasses must implement camera.get_viewport()") 

	@classmethod
	def for_window(cls, window, *args, **kwargs):
		return cls(*args, width=window.width, height=window.height, **kwargs)


class FixedCamera(Camera):
	"""A camera with a fixed position"""
	def __init__(self, width, height, center_x=0, center_y=0):
		super(FixedCamera, self).__init__(width, height)
		self.x = center_x
		self.y = center_y

	def move_to(self, center_x, center_y):
		self.x = center_x
		self.y = center_y

	def get_viewport(self):
		return Viewport(self.width, self.height, center_x=self.x, center_y=self.y)


class MovingCamera(FixedCamera):
	"""A camera that controls its own position""" 
	def update(self):
		"""Implement this to reposition the camera, etc."""

	def get_viewport(self):
		self.update()
		return super(MovingCamera, self).get_viewport()


class TrackingCamera(MovingCamera):
	"""A camera that follows an actor"""
	def __init__(self, actor, width, height):
		super(TrackingCamera, self).__init__(width, height)
		self.actor = actor

	def update(self):
		self.move_to(self.actor.x, self.actor.y)


class LevelCamera(MovingCamera):
	"""A camera that is restricted to the visible region of a level"""
	def __init__(self, width, height, level, center_x=0, center_y=0):
		super(LevelCamera, self).__init__(width, height, center_x, center_y)
		self.level = level

	def move_to(self, x, y):
		hw = self.width / 2
		hh = self.height / 2
		x = max(hw, min(self.level.width - hw, x))
		y = max(hh, y)
		self.x = x
		self.y = y
