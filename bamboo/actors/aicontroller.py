import random

class AIController(object):
	SLEEP_DISTANCE = 700	# Don't engage targets further away than this

	def __init__(self, character):
		self.character = character
		self.target = None

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

	def range_to_target(self):
		return (self.target.pos - self.character.pos).mag()

	def direction_to_target(self):
		x = self.character.pos.x
		tx = self.target.pos.x 
		if x < tx:
			return 'r'
		else:
			return 'l'
		# TODO: handle above or below case

	def run_towards_target(self):
		dir = self.direction_to_target()
		if dir == 'r':
			self.character.run_right()
		else:
			self.character.run_left()

	def update(self):
		if self.target is not None and not self.target.is_alive():
			self.target = None

		if not self.target:
			t = self.choose_target()
			if not t:
				return
			self.target = t
		if self.range_to_target() > 100:
			self.run_towards_target()
