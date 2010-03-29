import pyglet
from pyglet.window import key

FPS = 30

class Game(object):
	def __init__(self, options):
		"""Here options is an optparse object or similar that contains a few
		commandline options for configuring the game, eg. fullscreen and window dims
		"""
		self.init_resources()
		self.window = self.create_window(options)

	def init_resources(self):
		pyglet.resource.path = ['resources/sprites', 'resources/textures', 'resources/music', 'resources/sounds', 'resources/levels']
		pyglet.resource.reindex()

	def create_window(self):
		window = pyglet.window.Window(1280, 800)
		return window

	def update(self):
		"""Update the world, or delegate to something that will"""

	def draw(self):
		"""Draw the scene, or delegate to something that will"""
		
	def run(self):
		pyglet.clock.schedule_interval(self.update, (1.0/FPS))
		pyglet.clock.set_fps_limit(FPS)
		pyglet.app.run()
