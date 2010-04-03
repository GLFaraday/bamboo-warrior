from bamboo.geom import Vec2

class ActorSpawn(object):
	NAME_MAP = {
		'BambooTree': 'bamboo.actors.trees.BambooTree',
		'Torii': 'bamboo.actors.scenery.Torii',
		'EatingSamurai': 'bamboo.actors.scenery.EatingSamurai',
		'StandingNinja': 'bamboo.actors.ninja.Ninja',
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
		mod = __import__(modname, {}, {}, [classname])
		return getattr(mod, classname)
		
	def spawn(self, level):
		from bamboo.actors.characters import Character
		from bamboo.actors.aicontroller import AIController
		obj = self.get_class()()
		if isinstance(obj, Character):
			controller = AIController(obj)
		else:
			controller = None
		level.spawn(obj, self.pos.x, self.pos.y, controller)


class Level(object):
	def __init__(self, width, height, ground, actor_spawns=[]):
		self.width = width
		self.height = height
		self.ground = ground
		self.actor_spawns = actor_spawns
		self.actors = []
		self.controllers = []

	def restart(self):
		self.actors = []
		for spawnpoint in self.actor_spawns:
			spawnpoint.spawn(self)
			
	def spawn(self, actor, x, y=None, controller=None):
		if not actor._resources_loaded:
			actor.load_resources()

		if y is None:
			y = self.ground.height_at(x)
		actor.pos = Vec2(x, y)
		actor.level = self

		if controller is not None:
			actor.controller = controller
			self.controllers.append(controller)

		self.actors.append(actor)
		actor.on_spawn()

	def kill(self, actor):
		self.actors.remove(actor)
		if actor.controller:
			actor.controller.on_character_death()
			self.controllers.remove(actor.controller)
		actor.delete()
		actor.level = None

	def get_actors(self):
		return self.actors[:]

	def update(self):
		"""Run physics, update everything in the world"""
		self.ground.update()

		for c in self.controllers:
			c.update()

		self.collide()

		for a in self.actors:
			a.update()

	def collide(self):
		for i, a in enumerate(self.actors):
			for b in self.actors[i+1:]:
				if a.collision_mask & b.collision_mask:
					intersection = a.bounds().intersection(b.bounds())
					if intersection:
						d = min(intersection.w, intersection.h) # amount of intersection
						v = (b.pos - a.pos).normalized() # direction AB
						a.pos -= v
						b.pos += v

	def get_climbables(self):
		from bamboo.actors.trees import Climbable
		for a in self.actors:
			if isinstance(a, Climbable) and a.is_climbable():
				yield a

	def get_nearest_climbable(self, pos):
		"""Return the nearest climbable and the distance to that climbable."""
		nearest = None
		distance = None
		for a in self.get_climbables():
			d = a.distance_from(pos)
			if nearest is None or d < distance:
				nearest = a
				distance = d

		return nearest, distance

	def find_playercharacters(self):
		from bamboo.actors.samurai import Character
		return [a for a in self.actors if isinstance(a, Character) and a.is_pc]

	def characters_colliding(self, rect):
		from bamboo.actors.samurai import Character
		return [a for a in self.actors if isinstance(a, Character) and a.bounds().intersects(rect)]
		
