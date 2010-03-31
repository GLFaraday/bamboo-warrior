from bamboo.geom import Vec2

class ActorSpawn(object):
	NAME_MAP = {
		'BambooTree': 'bamboo.actors.trees.BambooTree',
		'Torii': 'bamboo.actors.scenery.Torii',
	}

	def __init__(self, name, pos):
		if name not in self.NAME_MAP:
			raise ValueError("Unknown object")
		self.name = name
		self.pos = pos

	def get_class(self):
		modpath = self.NAME_MAP[self.name]
		parts = modpath.split('.')
		classname = parts[-1]
		modname = '.'.join(parts[:-1])
		mod = __import__(modname, {}, {}, [classname], -1)
		return getattr(mod, classname)
		
	def spawn(self, level):
		obj = self.get_class()
		level.spawn(obj(), self.pos.x, self.pos.y)


class Level(object):
	def __init__(self, width, height, ground, actor_spawns=[]):
		self.width = width
		self.height = height
		self.ground = ground
		self.actor_spawns = actor_spawns
		self.actors = []

	def restart(self):
		self.actors = []
		for spawnpoint in self.actor_spawns:
			spawnpoint.spawn(self)
			

	def spawn(self, actor, x, y=None):
		if not actor._resources_loaded:
			actor.load_resources()

		if y is None:
			y = self.ground.height_at(x)
		actor.pos = Vec2(x, y)
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

	def get_nearest_climbable(self, pos):
		"""Return the nearest climbable and the distance to that climbable."""
		from bamboo.actors.trees import Climbable
		nearest = None
		distance = None
		for a in self.actors:
			if isinstance(a, Climbable) and a.is_climbable():
				d = a.distance_from(pos)
				if nearest is None or d < distance:
					nearest = a
					distance = d

		return nearest, distance
