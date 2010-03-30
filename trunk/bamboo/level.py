class Level(object):
	def __init__(self, ground):
		self.ground = ground
		self.actors = []

	def spawn(self, actor, x, y=None):
		if not actor._resources_loaded:
			actor.load_resources()

		if y is None:
			y = self.ground.height_at(x)
		actor.x = x
		actor.y = y
		actor.level = self

		self.actors.append(actor)
		actor.on_spawn()

	def kill(self, actor):
		self.actors.remove(actor)
		self.actor.level = None

	def get_actors(self):
		return self.actors[:]

	def update(self):
		"""Run physics, update everything in the world"""
		self.ground.update()
		for a in self.actors:
			a.update()

	def get_nearest_climbable(self, x, y):
		"""Return the nearest climbable and the distance to that climbable."""
		from bamboo.actors.trees import Climbable
		nearest = None
		distance = None
		for a in self.actors:
			if isinstance(a, Climbable) and a.is_climbable():
				d = a.distance_from(x, y)
				if nearest is None or d < distance:
					nearest = a
					distance = d

		return nearest, distance
