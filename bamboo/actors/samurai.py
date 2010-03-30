from base import Actor

GRAVITY = 0.5

class Samurai(Actor):
	FALL_SPEED = -5		#threshold at which to play falling animation

	def __init__(self):
		self.dir = 'r'
		self.vx = 0
		self.vy = 0
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
			self.vx = 10
			self.vy = 8
		else:
			self.dir = 'r'
			self.vx = min(10, self.vx + 1)
			self.crouching = False

	def run_left(self):
		if self.is_climbing():
			if self.dir == 'r':
				self.play_animation('clinging-lookingout')
			else:
				self.play_animation('clinging-lookingacross')
			self.vx = -10
			self.vy = 8
		else:
			self.dir = 'l'
			self.vx = max(-10, self.vx - 1)
			self.crouching = False

	def is_climbing(self):
		return self.climbing is not None

	def climb_up(self):
		if not self.is_climbing():
			tree, distance = self.level.get_nearest_climbable(self.x, self.y)
			if not tree or distance > 30:
				return
			tree.add_actor(self)
			self.play_animation('climbing')
		else:
			self.climbing.climb_up(self)

	def climb_down(self):
		if not self.is_climbing():
			tree, distance = self.level.get_nearest_climbable(self.x, self.y)
			if not tree or distance > 30:
				return
			tree.add_actor(self)
		else:
			self.climbing.climb_down(self)

	def apply_friction(self):
		if not self.is_on_ground():
			return

		if self.vx > 0:
			self.vx = max(0, self.vx - 1)
		elif self.vx < 0:
			self.vx = min(0, self.vx + 1)

	def crouch(self):
		if self.is_on_ground():
			self.crouching = True
			self.apply_friction()

	def stop(self):
		if self.is_climbing():
			self.play_animation('clinging')
		else:
			self.crouching = False
			self.apply_friction()

	def is_on_ground(self):
		return self.y <= (self.level.ground.height_at(self.x) + 2)

	def jump(self):
		if self.is_on_ground():
			self.crouching = False
			self.vy = 13
			self.y += 15 # leave the ground
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
				if self.vx:
					self.play_animation('running')
				else:
					self.play_animation('standing')
			else:
				if self.vy <= self.FALL_SPEED:
					self.play_animation('falling')
				else:
					self.play_animation('jumping')

	def update(self):
		if not self.is_climbing():
			self.rotation = 0
			self.x += self.vx
			gh = self.level.ground.height_at(self.x)
			if not self.is_on_ground():
				if self.y + self.vy - GRAVITY <= gh + 2:
					self.y = gh
					self.vy = 0
				else:
					vy0 = self.vy
					self.vy -= GRAVITY
					self.y += self.vy
			else:
				self.y = gh
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
		sprite.set_position(self.x, self.y)
		sprite.rotation = self.rotation
		sprite.draw() 
