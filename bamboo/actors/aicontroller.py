import random

class AIController(object):
	SLEEP_DISTANCE = 700	# Don't engage targets further away than this

	def __init__(self, character):
		self.character = character
		self.target = None
		self.attack_timer = 0
		self.strategy = None
		self.strategy_time = 0

		self.target_tree = None

	def choose_target(self):
		"""Returns the nearest player character, or None
		if there are no players in range"""
		targets = self.character.level.find_playercharacters()
		nearest, distance = None, None
		for t in targets:
			d = self.character.distance_to(t.pos)
			if nearest is None or d < distance:
				nearest = t
				distance = d 
		if distance < self.SLEEP_DISTANCE:
			return nearest


	def range_to(self, pos):
		return (pos - self.character.pos).mag()

	def range_to_target(self):
		return self.range_to(self.target.pos)

	def direction_to(self, pos):
		x = self.character.pos.x
		tx = pos.x 
		if x < tx:
			return 'r'
		else:
			return 'l'
		# TODO: handle above or below case

	def run_towards(self, pos):
		dir = self.direction_to(pos)
		if dir == 'r':
			self.character.run_right()
		else:
			self.character.run_left()

	def run_towards_target(self):
		if not self.target:
			return
		self.run_towards(self.target.pos)

	def on_character_death(self):
		pass

	def update(self):
		if self.attack_timer > 0:
			self.attack_timer -= 1

		if not self.target or not self.target.is_alive():
			t = self.choose_target()
			if not t:
				return
			self.target = t

		if not self.strategy or self.strategy_time % 30 == 0:
			self.pick_strategy()

		getattr(self, 'strategy_' + self.strategy)()
		self.strategy_time += 1

	def set_strategy(self, strategy):
		self.strategy = strategy
		self.strategy_time = 1

	def pick_strategy(self):
		if self.target.is_climbing():
			self.set_strategy('climbtree')
		else:
			self.set_strategy('approach')

	def pick_tree(self):
		nearest = None
		distance = None
		sx = self.character.pos.x
		tx = self.target.pos.x
		for a in self.character.level.get_climbables():
			ax = a.pos.x
			if sx < tx - 100:
				if a.pos.x > tx:
					continue
			elif sx > tx + 100:
				if a.pos.x < tx:
					continue
			if a.actors:
				continue
				
			d = abs(tx - ax)
			if nearest is None or d < distance:
				nearest = a
				distance = d

		return nearest, distance

	def strategy_climbtree(self):
		if self.target_tree is None or self.strategy_time % 10 == 0:
			tree, dist = self.pick_tree()
			if tree and dist < 300:
				self.target_tree = tree
			else:
				self.set_strategy('await')
				return

		px = self.character.pos.x
		tx = self.target_tree.pos.x

		if self.character.is_climbing() and self.character.climbing != self.target_tree:
			self.run_towards(self.target_tree.pos)
			self.character.jump()
		elif abs(px - tx) < 20:
			self.character.climb(self.target_tree, 1)
			self.set_strategy('treefight')
		else:
			self.run_towards(self.target_tree.pos)

	def strategy_treefight(self):
		if self.target.pos.y > self.character.pos.y + 50:
			self.character.climb_up()
		elif self.target.pos.y < self.character.pos.y - 50:
			self.character.climb_down()
			if not self.character.is_climbing():
				self.set_strategy('approach')
		else:
			self.run_towards_target()
			if (self.target.pos - self.character.pos).mag() < 200:
				self.character.attack()
			self.character.stop()
		
	def strategy_approach(self):
		if self.target.is_climbing() and self.strategy_time % 60 == 0:
			self.pick_strategy()
		if self.range_to_target() > 100:
			self.run_towards_target()
		else:
			if self.attack_timer == 0:
				self.character.attack()
				self.attack_timer = 100
			self.character.stop()

	def strategy_await(self):
		if not self.target.is_climbing():
			self.pick_strategy()
			return

		if self.range_to(self.target.climbing.pos) > 100:
			self.run_towards(self.target.climbing.pos)
		else:
			self.character.dir = self.direction_to(self.target.climbing.pos)
			if self.character.is_on_ground():
				self.character.crouch()
