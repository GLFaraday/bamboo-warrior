import pyglet

from bamboo.resources import ResourceTracker
from bamboo.geom import Vec2


class Actor(ResourceTracker):
	initial_animation = None
	current = None
	sprite = None

	level = None
	rotation = 0

	def play_sound(self, name):
		"""Play a named sound from the Actor's resources"""
		self.sounds[name].play()

	def play_animation(self, name):
		"""Set the current animation""" 
		if self.current == name:
			return
		self.current = name
		self.sprite = pyglet.sprite.Sprite(self.graphics[name], self.pos.x, self.pos.y)

	def draw(self):
		"""Subclasses should implement this method to draw the actor"""	
		self.sprite.set_position(self.pos.x, self.pos.y)
		self.sprite.rotation = self.rotation
		self.sprite.draw() 

	def update(self):
		"""Subclasses can implement this method if necessary to implement game logic"""

	def on_spawn(self):
		"""Subclasses can implement this method to initialise the actor"""
		if self.initial_animation:
			self.play_animation(self.initial_animation)


GRAVITY = 1.8

class Character(Actor):
	"""A character is an actor bound by simple platform physics"""
	MASS = 1
	FRICTION = 0.3
	LINEAR_DAMPING = 0.05

	def __init__(self, pos):
		self.pos = pos
		self.v = Vec2(0, 0)
		self.f = Vec2(0, -GRAVITY)
	
	def apply_force(self, vec):
		self.f += vec

	def apply_impulse(self, vec):
		self.v += vec / self.MASS

	def ground_force(self):
		restitution = Vec2(0, -min(0, self.v.y + self.f.y))
		friction = Vec2(-self.v.x, 0) * self.FRICTION
		return restitution + friction

	def is_on_ground(self):
		return self.pos.y <= (self.level.ground.height_at(self.pos.x) + 2)

	def get_net_force(self):
		"""This can only be called once per frame"""
		if self.is_on_ground():
			gf = self.ground_force()
			self.f += gf 
		f = self.f
		self.f = Vec2(0, -GRAVITY)
		return f

	def update(self):
		f = self.get_net_force()
		accel = f / self.MASS
		self.v = (self.v + accel) * (1 - self.LINEAR_DAMPING)
		self.f = Vec2(0, -GRAVITY)
		self.pos += self.v
		g = self.level.ground.height_at(self.pos.x)
		if self.pos.y < g:
			self.pos = Vec2(self.pos.x, g)
