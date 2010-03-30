import re

import pyglet
from pyglet.window import key

FPS = 60

class GameState(object):
	def start(self):
		"""Called when the gamestate is first activated"""

	def draw(self):
		"""Called once per frame to handle drawing"""

	def update(self, keys):
		"""Called once per frame to update the logic;
		keys is a KeyStateHandler that contains the current state of the keyboard"""

	def on_key_press(self, code, modifiers):
		"""Called when a key is pressed"""


class Game(object):
	def __init__(self, options):
		"""Here options is an optparse object or similar that contains a few
		commandline options for configuring the game, eg. fullscreen and window dims
		"""
		self.init_resources()
		self.window = self.create_window(options)
		self.init_events()
		self.gamestate = GameState()

	def init_resources(self):
		pyglet.resource.path = ['resources/sprites', 'resources/textures', 'resources/music', 'resources/sounds', 'resources/levels']
		pyglet.resource.reindex()

	def create_window(self, options):
		mo = re.match(r'(\d+)x(\d+)', options.resolution)
		if mo:
			width = int(mo.group(1))
			height = int(mo.group(2))
		else:
			width = 1280
			height = 720

		window = pyglet.window.Window(width, height, fullscreen=options.fullscreen)
		window.set_caption('Bamboo Warrior')
		return window

	def on_key_press(self, code, modifiers):
		if code == key.F12:
			print "Wrote", scene.save_screenshot()
			return pyglet.event.EVENT_HANDLED
		return self.gamestate.on_key_press(code, modifiers)

	def init_events(self):
		self.keys = key.KeyStateHandler()
		self.window.push_handlers(on_key_press=self.on_key_press, on_draw=self.draw)
		self.window.push_handlers(self.keys)

	def set_gamestate(self, gamestate):
		self.gamestate = gamestate
		gamestate.start()

	def update(self, x):
		"""Update the world, or delegate to something that will"""
		self.gamestate.update(self.keys)

	def draw(self):
		"""Draw the scene, or delegate to something that will"""
		self.gamestate.draw()
	
	def run(self):
		pyglet.clock.schedule_interval(self.update, (1.0/FPS))
		pyglet.clock.set_fps_limit(FPS)
		pyglet.app.run()


class BambooWarriorGameState(GameState):
	"""Represents the activities of the game at a given point.
	It should be possible to replace the gamestate to do something different
	with input or graphics."""

	def __init__(self, game, level='level1.svg'):
		self.game = game
		self.start_level(level)

	def start_level(self, level):
		from bamboo.levelloader import SVGLevelLoader
		from bamboo.scene import Scene
		from bamboo.camera import LevelCamera

		loader = SVGLevelLoader()
		self.level = loader.load(level)
		self.scene = Scene(self.game.window, self.level)
		self.scene.camera = LevelCamera.for_window(self.scene.window, level=self.level)
		self.level.restart()

	def start(self):
		"""Start is called when the gamestate is initialised"""
		music = pyglet.resource.media('shika-no-toone.ogg')
		music.play()

		from bamboo.actors.samurai import Samurai
		self.samurai = Samurai()
		self.level.spawn(self.samurai, x=60)

	def update(self, keys):
		samurai = self.samurai

		if keys[key.Z]:
			samurai.jump()

		if keys[key.UP]:
			samurai.climb_up()
		elif keys[key.DOWN]:
			if samurai.is_climbing():
				samurai.climb_down()
			else:
				samurai.crouch()
		elif keys[key.RIGHT]:
			samurai.run_right()
		elif keys[key.LEFT]:
			samurai.run_left()
		else:
			samurai.stop()

		samurai.update()

		self.level.update()

	def draw(self):
		self.scene.camera.move_to(self.samurai.x, self.samurai.y)
		self.scene.draw()
