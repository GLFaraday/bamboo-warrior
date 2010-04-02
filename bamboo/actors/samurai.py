import pyglet

from base import PhysicalObject, Actor
from bamboo.geom import Vec2, Rect

from bamboo.actors.gibs import BloodSpray


class Character(PhysicalObject):
	"""A character is a humanoid, who can fight, climb trees, etc."""
	FALL_SPEED = -20		#threshold at which to play falling animation
	AIR_ACCEL = Vec2(5, 0)
	GROUND_ACCEL = 15
	MAX_RUN_SPEED = 20
	JUMP_IMPULSE = Vec2(0, 30)
	TREE_JUMP_IMPULSE = Vec2(10, 15)	# rightwards, negate x component for leftwards
	CLIMB_UP_RATE = 10.0
	CLIMB_DOWN_RATE = 20.0

	ATTACK_RATE = 20	# min number of frames allowed between attacks

	TRAIL_LENGTH = 10	# length of the trail
	TRAIL_DECAY = 0.9	# fractional opacity change per trail sprite

	is_pc = False	# True if this character is a player character

	collision_mask = 0x01

	layer = 2

	MAX_HEALTH = 10

	def __init__(self):
		super(Character, self).__init__()
		self.dir = 'r'
		self.rotation = 0
		self.current = None

		self.looking = None		# only used when climbing trees
		self.crouching = False
		self.climbing = None
		self.attack_timer = 0
		self.climb_rate = 0		# current climb rate (when climbing a tree)
		self.health = self.MAX_HEALTH

		self.trail = []

	def run_speed(self):
		return max(self.MAX_RUN_SPEED - self.v.mag(), 0) * self.GROUND_ACCEL

	def run_right(self):
		if self.is_climbing():
			self.apply_force(Vec2(10, 0))
			self.looking = 'r'
			self.climb_rate = 0
		else:
			self.dir = 'r'
			if self.is_on_ground():
				self.apply_force(-self.run_speed() * self.runforce * self.ground_normal().perpendicular())
			else:
				self.apply_force(self.AIR_ACCEL)
			self.crouching = False

	def run_left(self):
		if self.is_climbing():
			self.apply_force(Vec2(-10, 0))
			self.looking = 'l'
			self.climb_rate = 0
		else:
			self.dir = 'l'
			if self.is_on_ground():
				self.apply_force(self.run_speed() * self.ground_normal().perpendicular())
			else:
				self.apply_force(-self.AIR_ACCEL)
			self.crouching = False

	def is_climbing(self):
		return self.climbing is not None

	def climb(self, tree, rate=0):
		"""Set this character as climbing the given tree."""
		tree.add_actor(self)
		self.looking = self.dir
		self.climb_rate = rate

	def nearby_climbable(self):
		"""Returns the nearest climbable, or None if there is none
		in "range"."""
		tree, distance = self.level.get_nearest_climbable(self.pos)
		if tree and distance < 30:
			return tree

	def climb_up(self):
		assert self.is_climbing()
		self.climbing.climb_up(self, dist=self.CLIMB_UP_RATE)
		self.climb_rate = self.CLIMB_UP_RATE

	def climb_down(self):
		assert self.is_climbing()
		self.climbing.climb_down(self, dist=self.CLIMB_DOWN_RATE)
		self.climb_rate = -self.CLIMB_DOWN_RATE

	def crouch(self):
		assert self.is_on_ground()
		self.crouching = True

	def stop(self):
		if self.is_climbing():
			self.climb_rate = 0
			self.looking = None
		else:
			self.crouching = False

	def on_jump(self):
		pass

	def on_tree_jump(self):
		self.on_jump()

	def on_spawn(self):
		pass

	def jump(self):
		if self.is_on_ground():
			self.crouching = False
			self.apply_impulse(self.JUMP_IMPULSE)
			self.on_jump()
		elif self.is_climbing():
			self.climbing.remove_actor(self)
			if self.looking:
				self.dir = self.looking
			if self.looking == 'r':
				self.apply_impulse(self.TREE_JUMP_IMPULSE)
			elif self.looking == 'l':
				ix, iy = self.TREE_JUMP_IMPULSE
				self.apply_impulse(Vec2(-ix, iy))
			self.on_tree_jump()

	def play_animation(self, name, directional=True):
		"""Set the current animation""" 
		if directional:
			name = name + '-' + self.dir
		super(Character, self).play_animation(name)

	def update_animation(self):
		pass

	def update(self):
		if self.attack_timer > 0:
			self.attack_timer -= 1

		if not self.is_climbing():
			# update physics
			super(Character, self).update()
			self.rotation = 0
		else:
			f = self.get_net_force()
			# TODO: apply force to the tree we're climbing
		self.update_animation()

	def draw_trail(self):
		if not hasattr(self, 'trail_batch'):
			self.trail_batch = pyglet.graphics.Batch()

		for s in reversed(self.trail):
			s.opacity *= self.TRAIL_DECAY
		
		# copy sprite
		s = pyglet.sprite.Sprite(self.sprite.image, *self.sprite.position, batch=self.trail_batch)
		s.rotation = self.sprite.rotation
		s.opacity = 128
		
		# update trail
		for f in self.trail[self.TRAIL_LENGTH - 1:]:
			f.delete()
		self.trail = [s] + self.trail[:self.TRAIL_LENGTH - 1]

		self.trail_batch.draw()


	def is_attacking(self):
		return self.attack_timer > self.ATTACK_RATE

	def can_attack(self):
		return self.attack_timer == 0

	def attack(self):
		if not self.can_attack():
			return

		self.attack_timer = self.ATTACK_RATE + 3

		if self.crouching:
			c = self.pos + Vec2(0, 72)
		else:
			c = self.pos + Vec2(0, 100)
		dir = self.looking or self.dir
		if dir == 'r':
			attack_region = Rect.from_corners(c - Vec2(0, 15), c + Vec2(180, 25))
			force = Vec2(10, 0) + self.v
		else:
			attack_region = Rect.from_corners(c - Vec2(0, 15), c + Vec2(-180, 25))
			force = Vec2(-10, 0) + self.v

		victims = [a for a in self.level.characters_colliding(attack_region) if a != self]
		if not victims:
			return
		damage = 10.0 / len(victims)
		force = force / len(victims)
		for a in victims: 
			point = attack_region.intersection(a.bounds()).center()
			a.hit(point, force, damage)

	def delete(self):
		super(Character, self).delete()
		if self.climbing:
			self.climbing.remove_actor(self)

	def dims(self):
		return 60, 140	

	def bounds(self):
		w, h = self.dims()
		return Rect(self.pos.x - w / 2, self.pos.y, w, h)

	def hit(self, point, force, damage=10):
		self.level.spawn(BloodSpray(v=force), x=point.x, y=point.y)
		self.health -= damage
		if self.health <= 0:
			corpse = self.CORPSE(self)
			self.level.spawn(corpse, x=self.pos.x, y=self.pos.y)
			self.on_death() 
			self.level.kill(self)

	def on_death(self):
		pass

	def draw(self):
		if self.TRAIL_LENGTH:
			self.draw_trail()
		super(Character, self).draw()


class Corpse(PhysicalObject):
	def __init__(self, character):
		super(Corpse, self).__init__()
		self.dir = character.dir

	def on_spawn(self):
		self.play_animation('dying', directional=True)
		self.death_timer = 0

	def update(self):
		if self.death_timer < 200:
			super(Corpse, self).update()
		self.death_timer += 1
		if self.death_timer < 15:
			rot = 1 if self.dir == 'l' else -1
			self.rotation = min(60, self.rotation + 0.6 + 0.3 * rot * self.death_timer)
		elif self.death_timer == 15:
			self.rotation = 0
			self.play_animation('dead', directional=True)
		elif self.death_timer == 350:
			self.level.kill(self)
		elif self.death_timer > 200:
			self.pos += Vec2(0,-0.5)

class SamuraiCorpse(Corpse):
	@classmethod
	def on_class_load(cls):
		cls.load_directional_sprite('dying', 'samurai-dying.png', anchor_x=125)
		cls.load_directional_sprite('dead', 'samurai-dead.png', anchor_x=160, anchor_y=15)


class Samurai(Character):
	"""Represents a set of graphics"""
	CORPSE = SamuraiCorpse
	
	@classmethod
	def on_class_load(cls):
		cls.load_directional_sprite('standing', anchor_x=30)
		cls.load_directional_sprite('attacking', anchor_x=30)
		cls.load_directional_sprite('crouching', anchor_x=30)
		cls.load_directional_sprite('crouching-attacking', anchor_x=30)
		cls.load_directional_sprite('jumping', anchor_x=50, anchor_y=20)
		cls.load_directional_sprite('falling', anchor_x=40, anchor_y=20)
		cls.load_directional_sprite('clinging', anchor_x=72)
		cls.load_directional_sprite('clinging-lookingout', anchor_x=72)
		cls.load_directional_sprite('clinging-lookingacross', anchor_x=35)
		cls.load_directional_sprite('clinging-slidingdown', anchor_x=51)
		cls.load_directional_sprite('clinging-lookingout-attacking', anchor_x=241)
		cls.load_directional_sprite('clinging-lookingacross-attacking', anchor_x=35)

		cls.load_sound('jumping')
		cls.load_animation('running', 'samurai-running%d.png', 6, anchor_x=105)
		cls.load_animation('climbing', 'samurai-climbing%d.png', 6, anchor_x=60)

	def update_animation(self):
		if self.is_attacking():
			if self.is_climbing():
				if self.looking != self.dir:
					self.play_animation('clinging-lookingout-attacking')
				else:
					self.play_animation('clinging-lookingacross-attacking')
			elif self.crouching:
				self.play_animation('crouching-attacking')
			else:
				self.play_animation('attacking')
		elif not self.is_climbing():
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
		else:
			if self.climb_rate > 0:
				self.play_animation('climbing')
			elif self.climb_rate < 0:
				self.play_animation('clinging-slidingdown')
			else:
				if self.looking is None:
					self.play_animation('clinging')
				elif self.looking != self.dir:
					self.play_animation('clinging-lookingout')
				else:
					self.play_animation('clinging-lookingacross')
	def on_spawn(self):
		self.play_animation('standing')

	def on_jump(self):
		#self.play_sound('jumping')
		self.play_animation('jumping')
