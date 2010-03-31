from base import Character
from bamboo.geom import Vec2


class Samurai(Character):
	FALL_SPEED = -10		#threshold at which to play falling animation
	AIR_ACCEL = Vec2(1.5, 0)
	GROUND_ACCEL = Vec2(10, 0)
	JUMP_IMPULSE = Vec2(0, 35)

	def __init__(self):
		super(Samurai, self).__init__(self)
		self.dir = 'r'
		self.rotation = 0
		self.current = None
		self.load_resources()

		self.crouching = False
		self.climbing = None

	def run_right(self):
		if self.is_climbing():
			if self.dir == 'l':
				self.play_animation('clinging-lookingout')
			else:
				self.play_animation('clinging-lookingacross')
			self.apply_force(Vec2(10, 0))
		else:
			self.dir = 'r'
			if self.is_on_ground():
				self.apply_force(self.GROUND_ACCEL)
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
		else:
			self.dir = 'l'
			if self.is_on_ground():
				self.apply_force(-self.GROUND_ACCEL)
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
			self.play_animation('climbing')
		else:
			self.climbing.climb_up(self)

	def climb_down(self):
		if not self.is_climbing():
			tree, distance = self.level.get_nearest_climbable(self.pos)
			if not tree or distance > 30:
				return
			tree.add_actor(self)
		else:
			self.climbing.climb_down(self)

	def crouch(self):
		if self.is_on_ground():
			self.crouching = True

	def stop(self):
		if self.is_climbing():
			self.play_animation('clinging')
		else:
			self.crouching = False

	def jump(self):
		if self.is_on_ground():
			self.crouching = False
			self.apply_impulse(self.JUMP_IMPULSE)
			self.play_sound('jumping')
		elif self.is_climbing():
			self.climbing.remove_actor(self)

	def play_animation(self, name):
		"""Set the current animation""" 
		k = name + '-' + self.dir
		if self.current == k:
			return 
		self.current = k

	def update_animation(self):
		if not self.is_climbing():
			if self.crouching:
				self.play_animation('crouching')
			elif self.is_on_ground():
				if self.v.mag() > 0.5:
					self.play_animation('running')
				else:
					self.play_animation('standing')
			else:
				if self.v.y <= self.FALL_SPEED:
					self.play_animation('falling')
				else:
					self.play_animation('jumping')

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
		cls.load_directional_sprite('jumping', anchor_x=50, anchor_y=10)
		cls.load_directional_sprite('falling', anchor_x=50)
		cls.load_directional_sprite('clinging', anchor_x=72)
		cls.load_directional_sprite('clinging-lookingout', anchor_x=72)
		cls.load_directional_sprite('clinging-lookingacross', anchor_x=35)

		cls.load_sound('jumping')
		cls.load_animation('running', 'samurai-running%d.png', 6, anchor_x=105)
		cls.load_animation('climbing', 'samurai-climbing%d.png', 6, anchor_x=60)

	def on_spawn(self):
		self.play_animation('standing')

	def draw(self):
		sprite = self.graphics[self.current]
		sprite.set_position(self.pos.x, self.pos.y)
		sprite.rotation = self.rotation
		sprite.draw() 
