from base import Actor

GRAVITY = 3

class Samurai(Actor):
	FALL_SPEED = -5		#threshold at which to play falling animation

	def __init__(self):
		self.dir = 'r'
		self.vx = 0
		self.vy = 0
		self.current = None
		self.load_resources()

		self.crouching = False

	def run_right(self):
		self.dir = 'r'
		self.vx = min(15, self.vx + 5)
		self.crouching = False

	def run_left(self):
		self.dir = 'l'
		self.vx = max(-15, self.vx - 5)
		self.crouching = False

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
		self.crouching = False
		self.apply_friction()

	def is_on_ground(self):
		return self.y <= (self.level.ground.height_at(self.x) + 2)

	def jump(self):
		if self.is_on_ground():
			self.crouching = False
			self.vy = 30
			self.y += 30 # leave the ground
			self.play_sound('jumping')

	def play_animation(self, name):
		"""Set the current animation""" 
		k = name + '-' + self.dir
		if self.current == k:
			return 
		self.current = k

	def update_animation(self):
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

		cls.load_sound('jumping')
		cls.load_animation('running', 'samurai-running%d.png', 6, anchor_x=105)

	def on_spawn(self):
		self.play_animation('standing')

	def draw(self):
		sprite = self.graphics[self.current]
		sprite.set_position(self.x, self.y)
		sprite.draw() 
