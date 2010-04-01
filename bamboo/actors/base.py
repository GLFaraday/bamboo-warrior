import pyglet

from bamboo.resources import ResourceTracker
from bamboo.geom import Vec2


class Actor(ResourceTracker):
	initial_animation = None
	current = None
	sprite = None

	level = None
	rotation = 0

	def _get_pos(self):
		return self._pos
	
	def _set_pos(self, pos):
		self._pos = pos
		if self.level:
			# TODO: tell level we've moved, so level can optimise
			self._ground_level = self.level.ground.height_at(pos.x)
			self._ground_normal = self.level.ground.normal_at(pos.x)

	_pos = Vec2(0, 0)
	pos = property(_get_pos, _set_pos)

	def ground_level(self):
		try:
			return self._ground_level
		except AttributeError:
			self._ground_level = self.level.ground.height_at(self.pos.x)
			return self._ground_level

	def ground_normal(self):
		try:
			return self._ground_normal
		except AttributeError:
			self._ground_normal = self.level.ground.normal_at(self.pos.x)
			return self._ground_normal
			

	def play_sound(self, name):
		"""Play a named sound from the Actor's resources"""
		self.sounds[name].play()

	def play_animation(self, name):
		"""Set the current animation""" 
		if self.current == name:
			return
		self.current = name
		if self.sprite:
			self.sprite.delete()
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


GRAVITY = Vec2(0, -1.6)

class Character(Actor):
	"""A character is an actor bound by simple platform physics"""
	MASS = 15
	FRICTION = 0.6
	LINEAR_DAMPING = 0.0

	def __init__(self, pos):
		self.pos = pos
		self.v = Vec2(0, 0)
		self.f = self.get_weight()
	
	def apply_force(self, vec):
		self.f += vec

	def apply_impulse(self, vec):
		self.v += vec

	def apply_ground_force(self):
		normal = self.ground_normal()
		tangent = normal.perpendicular()

		restitution = -min(normal.dot(self.v), 0) * normal
		self.apply_impulse(restitution)

		normalforce = -min(normal.dot(self.f), 0) * normal
		self.apply_force(normalforce)

		friction = self.FRICTION * normalforce.mag()	# max friction
		ground_velocity = tangent.component_of(self.v)
		ground_force = tangent.component_of(self.f)
		if ground_velocity:
			f = min(friction, ground_velocity.mag() * self.MASS + ground_force.mag())
			self.apply_force(-ground_velocity.normalized() * f)
		elif ground_force:
			f = min(ground_force.mag(), friction)
			self.apply_force(-ground_force.normalized() * f)

	def is_on_ground(self):
		return self.pos.y <= (self.ground_level() + 0.5)

	def get_net_force(self):
		"""This can only be called once per frame"""
		if self.is_on_ground():
			self.apply_ground_force()
		f = self.f
		self.f = self.get_weight()
		return f

	def get_weight(self):
		return GRAVITY * self.MASS

	def update(self):
		f = self.get_net_force()
		accel = f / self.MASS
		self.v = (self.v + accel) * (1 - self.LINEAR_DAMPING)
		self.pos += self.v
		g = self.ground_level()
		if self.pos.y < g:
			self.pos = Vec2(self.pos.x, g)