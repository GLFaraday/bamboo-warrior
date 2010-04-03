import pyglet

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
		self.huds = []
		self.start_level(level)

	def get_camera(self):
		from bamboo import camera
		return camera.LeadingCamera.for_window(self.scene.window, level=self.level)

	def start_level(self, level):
		from bamboo.levelloader import SVGLevelLoader
		from bamboo.scene import Scene

		loader = SVGLevelLoader()
		self.level = loader.load(level)
		self.scene = Scene(self.game.window, self.level)
		self.scene.camera = self.get_camera()
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
		self.pc.lives = 4
		self.spawn_player()
		self.pc.add_death_listener(self.on_player_death)
	
		self.create_hud(self.pc)

	def create_hud(self, pc, side='l', col=(255, 255, 255)):
		from bamboo.hud import HUD
		HUD.load_resources()
		hud = HUD(self.game.window, pc, side=side, col=col)
		self.huds.append(hud)
		
	def on_player_death(self, player):
		if self.pc.lives == 0:
			# do game over
			pass
		else:
			pyglet.clock.schedule_once(self.spawn_player, 3)

	def spawn_player(self, *args):
		self.pc.lives -= 1
		self.pc.v = Vec2(0,0)
		self.level.spawn(self.pc, x=60, controller=self.player)

	def update(self, keys):
		player = self.player

		if self.pc.is_alive():
			if keys[key.RSHIFT]:
				player.jump()
			elif keys[key.RCTRL]:
				player.attack()

			if keys[key.UP]:
				player.up()
			elif keys[key.DOWN]:
				player.down()
			elif keys[key.RIGHT]:
				player.right()
			elif keys[key.LEFT]:
				player.left()

			self.scene.camera.track(self.pc.pos)

		self.level.update()

	def draw(self):
		self.scene.update()
		self.scene.camera.update()
		self.scene.draw()
		for h in self.huds:
			h.update_batch()
			h.draw()


class StaticLevelGameState(BambooWarriorGameState):
	"""A gamestate that renders a static level. Used by the menu system"""
	def __init__(self, game, level='title.svg'):
		super(StaticLevelGameState, self).__init__(game, level)

	def update(self, keys):
		self.level.update_scenery()

	def draw(self):
		self.update({})
		self.scene.camera.move_to(Vec2(60, 60))
		self.scene.update()
		self.scene.draw()


class MultiplayerGameState(BambooWarriorGameState):
	def __init__(self, game, level='arena.svg'):
		super(MultiplayerGameState, self).__init__(game, level)

	def get_camera(self):
		from bamboo import camera
		return camera.DualTrackingCamera.for_window(self.scene.window, level=self.level)

	def start(self):
		"""Start is called when the gamestate is initialised"""
		from bamboo.actors.samurai import Samurai
		from bamboo.actors.playercharacter import PlayerController

		self.pc1 = Samurai(col=(255,200,200))
		self.pc2 = Samurai(col=(200,200,255))
		self.player1 = PlayerController(self.pc1)
		self.player2 = PlayerController(self.pc2)
		self.player1.lives = 0
		self.player2.lives = 0
		self.create_hud(self.pc1, side='l', col=self.pc1.col)
		self.create_hud(self.pc2, side='r', col=self.pc2.col)

		self.spawn_p1()
		self.spawn_p2()

	def spawn_p1(self):
		self.pc1.v = Vec2(0,0)
		self.level.spawn(self.pc1, x=60, controller=self.player1)

	def spawn_p2(self):
		self.pc2.dir = 'l'
		self.pc2.v = Vec2(0,0)
		self.level.spawn(self.pc2, x=self.level.width - 60, controller=self.player2)

	def update(self, keys):
		player1 = self.player1
		player2 = self.player2
		if self.pc1.is_alive():
			if keys[key.RSHIFT]:
				player1.jump()
			elif keys[key.RCTRL]:
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
			if keys[key.U]:
				player2.jump()
			elif keys[key.I]:
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

		if self.pc1.is_alive() and self.pc2.is_alive():
			self.scene.camera.track_both(self.pc1.pos, self.pc2.pos)
		elif self.pc1.is_alive():
			self.scene.camera.track(self.pc1.pos)
		elif self.pc2.is_alive():
			self.scene.camera.track(self.pc2.pos)

		self.level.update()

	def draw(self):
		self.scene.update()
		self.scene.camera.update()
		self.scene.draw()
		for h in self.huds:
			h.update_batch()
			h.draw()
