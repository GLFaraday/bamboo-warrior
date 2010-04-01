import pyglet

from base import Character
from bamboo.geom import Vec2


class Samurai(Character):
	FALL_SPEED = -20		#threshold at which to play falling animation
	AIR_ACCEL = Vec2(5, 0)
	GROUND_ACCEL = 10
	MAX_RUN_SPEED = 15
	JUMP_IMPULSE = Vec2(0, 28)
	TREE_JUMP_IMPULSE = Vec2(10, 15)	# rightwards, negate x component for leftwards

	def __init__(self):
		super(Samurai, self).__init__(self)
		self.dir = 'r'
		self.rotation = 0
		self.current = None
		self.load_resources()

		self.looking = None		# only used when climbing trees
		self.crouching = False
		self.climbing = None

		self.trail = []

	def run_speed(self):
		return max(self.MAX_RUN_SPEED - self.v.mag(), 0) * self.GROUND_ACCEL

	def run_right(self):
		if self.is_climbing():
			if self.dir == 'l':
				self.play_animation('clinging-lookingout')
			else:
				self.play_animation('clinging-lookingacross')
			self.apply_force(Vec2(10, 0))
			self.looking = 'r'
		else:
			self.dir = 'r'
			if self.is_on_ground():
				self.apply_force(-self.run_speed() * self.ground_normal().perpendicular())
			else:
				self.apply_force(self.AIR_ACCEL)
			self.crouching = False

	def run_left(self):
		if self.is_climbing():
			if self.dir == 'r':
				self.play_animation('clinging-lookingout')
			else:
				self.play_animation('clinging-lookingacross')
			self.apply_force(Vec2(-10, 0))
			self.looking = 'l'
		else:
			self.dir = 'l'
			if self.is_on_ground():
				self.apply_force(self.run_speed() * self.ground_normal().perpendicular())
			else:
				self.apply_force(-self.AIR_ACCEL)
			self.crouching = False

	def is_climbing(self):
		return self.climbing is not None

	def climb_up(self):
		if not self.is_climbing():
			tree, distance = self.level.get_nearest_climbable(self.pos)
			if not tree or distance > 30:
				return
			tree.add_actor(self)
			self.looking = self.dir
		else:
			self.climbing.climb_up(self)

		self.play_animation('climbing')

	def climb_down(self):
		if not self.is_climbing():
			tree, distance = self.level.get_nearest_climbable(self.pos)
			if not tree or distance > 30:
				return
			self.looking = self.dir
			tree.add_actor(self)
		else:
			self.climbing.climb_down(self, dist=20.0)

		self.play_animation('clinging-slidingdown')

	def crouch(self):
		if self.is_on_ground():
			self.crouching = True

	def stop(self):
		if self.is_climbing():
			self.play_animation('clinging')
			self.looking = None
		else:
			self.crouching = False

	def jump(self):
		if self.is_on_ground():
			self.crouching = False
			self.apply_impulse(self.JUMP_IMPULSE)
		#	self.play_sound('jumping')
			self.play_animation('jumping')
		elif self.is_climbing():
			self.climbing.remove_actor(self)
			if self.looking:
				self.dir = self.looking
			if self.looking == 'r':
				self.apply_impulse(self.TREE_JUMP_IMPULSE)
			elif self.looking == 'l':
				ix, iy = self.TREE_JUMP_IMPULSE
				self.apply_impulse(Vec2(-ix, iy))
			self.play_animation('jumping')


	def play_animation(self, name, directional=True):
		"""Set the current animation""" 
		if directional:
			name = name + '-' + self.dir
		super(Samurai, self).play_animation(name)

	def update_animation(self):
		if not self.is_climbing():
			if self.crouching:
				self.play_animation('crouching')
			elif self.is_on_ground():
				if self.v.mag() < 0.01:
					self.play_animation('standing')
				else:
					self.play_animation('running')
			else:
				if self.v.y <= self.FALL_SPEED:
					self.play_animation('falling')

	def update(self):
		if not self.is_climbing():
			super(Samurai, self).update()
			self.rotation = 0
		else:
			f = self.get_net_force()
			# TODO: apply force to the tree we're climbing
		self.update_animation()

	resources_loaded = False

	@classmethod
	def on_class_load(cls):
		cls.load_directional_sprite('standing', anchor_x=30)
		cls.load_directional_sprite('crouching', anchor_x=30)
		cls.load_directional_sprite('jumping', anchor_x=50, anchor_y=20)
		cls.load_directional_sprite('falling', anchor_x=40, anchor_y=20)
		cls.load_directional_sprite('clinging', anchor_x=72)
		cls.load_directional_sprite('clinging-lookingout', anchor_x=72)
		cls.load_directional_sprite('clinging-lookingacross', anchor_x=35)
		cls.load_directional_sprite('clinging-slidingdown', anchor_x=51)

		cls.load_sound('jumping')
		cls.load_animation('running', 'samurai-running%d.png', 6, anchor_x=105)
		cls.load_animation('climbing', 'samurai-climbing%d.png', 6, anchor_x=60)

	def on_spawn(self):
		self.play_animation('standing')

	def draw_trail(self):
		if not hasattr(self, 'trail_batch'):
			self.trail_batch = pyglet.graphics.Batch()

		for s in reversed(self.trail):
			s.opacity *= 0.9
		
		# copy sprite
		s = pyglet.sprite.Sprite(self.sprite.image, *self.sprite.position, batch=self.trail_batch)
		s.rotation = self.sprite.rotation
		s.opacity = 128
		
		self.trail_batch.draw()

		# update trail
		TRAIL_LENGTH = 15
		for f in self.trail[TRAIL_LENGTH:]:
			f.delete()
		self.trail = [s] + self.trail[:TRAIL_LENGTH]

	def draw(self):
		self.draw_trail()
		super(Samurai, self).draw()
