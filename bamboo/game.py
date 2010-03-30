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

	def update(self, x):
		"""Update the world, or delegate to something that will"""

	def draw(self):
		"""Draw the scene, or delegate to something that will"""
		
	def run(self):
		pyglet.clock.schedule_interval(self.update, (1.0/FPS))
		pyglet.clock.set_fps_limit(FPS)
		pyglet.app.run()


class GameState(object):
	"""Represents the activities of the game at a given point.
	It should be possible to replace the gamestate to do something different
	with input or graphics."""

	def __init__(self, game):
		level = Level(Terrain(width=1280))
		scene = Scene(window, level)

		samurai = Samurai()
		level.spawn(samurai, x=60)

	def update(foo):
		if keys[key.Z]:
			samurai.jump()

		if keys[key.DOWN]:
			samurai.crouch()
		elif keys[key.RIGHT]:
			samurai.run_right()
		elif keys[key.LEFT]:
			samurai.run_left()
		else:
			samurai.stop()

		samurai.update()

		level.update()
