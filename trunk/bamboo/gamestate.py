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


class MultiplayerGameState(BambooWarriorGameState):
	def __init__(self, game, level='arena.svg'):
		super(MultiplayerGameState, self).__init__(game, level)

	def start(self):
		"""Start is called when the gamestate is initialised"""
		from bamboo.actors.samurai import Samurai
		from bamboo.actors.playercharacter import PlayerController

		self.pc1 = Samurai(col=(255,200,200))
		self.pc2 = Samurai(col=(200,200,255))
		self.player1 = PlayerController(self.pc1)
		self.player2 = PlayerController(self.pc2)
		self.spawn_p1()
		self.spawn_p2()

	def spawn_p1(self):
		self.level.spawn(self.pc1, x=60, controller=self.player1)

	def spawn_p2(self):
		self.pc2.dir = 'l'
		self.level.spawn(self.pc2, x=self.level.width - 60, controller=self.player2)

	def update(self, keys):
		player1 = self.player1
		player2 = self.player2
		if self.pc1.is_alive():
			if keys[key.Z]:
				player1.jump()
			elif keys[key.X]:
				player1.attack()

			if keys[key.UP]:
				player1.up()
			elif keys[key.DOWN]:
				player1.down()
			elif keys[key.RIGHT]:
				player1.right()
			elif keys[key.LEFT]:
				player1.left()
		else:
			self.spawn_p1()

		if self.pc2.is_alive():
			if keys[key.O]:
				player2.jump()
			elif keys[key.P]:
				player2.attack()

			if keys[key.W]:
				player2.up()
			elif keys[key.S]:
				player2.down()
			elif keys[key.D]:
				player2.right()
			elif keys[key.A]:
				player2.left()
		else:
			self.spawn_p2()

		self.level.update()

	def draw(self):
		self.scene.update()
		# TODO: multitrackingcamera
		self.scene.camera.move_to(Vec2(self.level.width // 2, 60))
		self.scene.draw()
