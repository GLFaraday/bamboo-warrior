from bamboo.geom import Vec2
from pyglet.window import key


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
		#music = pyglet.resource.media('shika-no-toone.ogg')
		#music.play()

		from bamboo.actors.samurai import Samurai
		from bamboo.actors.ninja import Ninja
		from bamboo.actors.playercharacter import PlayerController
		from bamboo.actors.aicontroller import AIController

		self.pc = Samurai()
		self.player = PlayerController(self.pc)
		self.level.spawn(self.pc, x=60, controller=self.player)

		ninja = Ninja()
		self.level.spawn(ninja, x=1000, controller=AIController(ninja))

	def update(self, keys):
		player = self.player

		if self.pc.is_alive():
			if keys[key.Z]:
				player.jump()
			elif keys[key.X]:
				player.attack()

			if keys[key.UP]:
				player.up()
			elif keys[key.DOWN]:
				player.down()
			elif keys[key.RIGHT]:
				player.right()
			elif keys[key.LEFT]:
				player.left()
		else:
			self.level.spawn(self.pc, x=60, controller=self.player)

		self.level.update()

	def draw(self):
		self.scene.update()
		self.scene.camera.move_to(self.pc.pos)
		self.scene.draw()


class StaticLevelGameState(BambooWarriorGameState):
	"""A gamestate that renders a static level. Used by the menu system"""
	def __init__(self, game, level='title.svg'):
		super(StaticLevelGameState, self).__init__(game, level)

	def update(self, keys):
		#TODO: update particles
		self.level.ground.update()

	def draw(self):
		self.update({})
		self.scene.camera.move_to(Vec2(60, 60))
		self.scene.update()
		self.scene.draw()
