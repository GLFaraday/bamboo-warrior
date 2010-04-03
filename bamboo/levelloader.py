import re
from xml.etree import ElementTree

import pyglet

from bamboo.geom import Vec2
from bamboo.level import Level, ActorSpawn
from bamboo.terrain import Terrain

SVG_NS = 'http://www.w3.org/2000/svg'
INKSCAPE_NS = 'http://www.inkscape.org/namespaces/inkscape'
XLINK_NS = 'http://www.w3.org/1999/xlink'


class LevelParseError(Exception):
	"""Raised when there is a problem parsing the SVG level"""


class SVGLevelLoader(object):
	"""Constructs a level from an SVG file constructed with Inkscape"""
	def load(self, svgfile):
		file = pyglet.resource.file(svgfile)
		doc = ElementTree.parse(file)
		self.width = int(float(doc.getroot().get('width')))
		self.height = int(float(doc.getroot().get('height')))
		for g in doc.findall('./{%s}g' % SVG_NS):
			if g.get('{%s}label' % INKSCAPE_NS) == 'Level':
				return self.load_from_group(g)
		raise ValueError("No level found in " + svgfile)

	def load_from_group(self, g):
		spawnpoints = []
		terrain = None
		for obj in g:
			id = obj.get('id')
			if id == 'ground':
				heightmap = self.load_path(obj)
				terrain = self.load_terrain(heightmap)
			elif obj.tag == '{%s}use' % SVG_NS:
				spawn = self.load_object(obj)
				spawnpoints.append(spawn)
			else:
				raise LevelParseError("Unknown XML element encountered" + obj.tag)
		if terrain is None:
			raise LevelParseError("No #ground element found")
		return Level(self.width, self.height, ground=terrain, actor_spawns=spawnpoints)

	def load_terrain(self, heightmap):
		t = Terrain(heightmap)
		return t

	def load_object(self, use):
		name = use.get('{%s}href' % XLINK_NS).replace('#', '')
		transform = use.get('transform')
		mo = re.match(r'translate\(([\d.-]+),([\d.-]+)\)', transform)
		if not mo:
			raise LevelParseError("Cannot parse transform attribute '%s'" % transform)
		pos = Vec2(float(mo.group(1)), self.height - float(mo.group(2)))
		return ActorSpawn(name, pos)

	def load_path(self, path):
		"""Read coordinates from path"""
		p = PathLoader(path.get('d'))
		return [Vec2(v.x, self.height - v.y) for v in p.coordinates()]


class PathLoader(object):
	"""Loads an SVG path as a sequence of Vec2s"""

	def __init__(self, s):
		self.s = s

	def tokens(self):
		return re.split(r'[, ]', self.s)

	def coordinates(self):
		self.closed = False # until proven guilty
		state = None
		pos = Vec2(0, 0)
		x = None # hold x coordinate while we wait for the y
		for tok in self.tokens():
			# read until we have a coordinate pair
			try:
				v = float(tok)
			except ValueError:
				if tok in 'Zz':
					self.closed = True
				state = tok
				continue

			if x is None:
				if state == 'v':
					pos += Vec2(0, v)
					yield pos
				elif state == 'V':
					pos = Vec2(pos.x, v)
					yield pos
				elif state == 'h':
					pos += Vec2(v, 0)
					yield pos
				elif state == 'H':
					pos = Vec2(v, pos.y)
					yield pos
				else:
					x = v
				continue

			# we have a coordinate pair, work out what to do with it in the current state
			v = Vec2(x, v)
			x = None

			if state in 'lm':
				pos += v
				yield pos
			elif state in 'LM':
				pos = v
				yield pos
			else:
				raise LevelParseError("Coordinate pair in state %s is unsupported." % state)
