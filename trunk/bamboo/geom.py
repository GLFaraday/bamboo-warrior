import math

ERROR_TOLERANCE = 1e-9

class Vec2(object):
	"""A 2D vector object to make vector maths easy"""
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __repr__(self):
		return 'Vec2(%r, %r)' % tuple(self)

	def __str__(self):
		return '(%f, %f)' % tuple(self)

	def __add__(self, ano):
		return Vec2(self.x + ano.x, self.y + ano.y)

	def __sub__(self, ano):
		return Vec2(self.x - ano.x, self.y - ano.y)

	def __neg__(self):
		return Vec2(-self.x, -self.y)

	def __mul__(self, scalar):
		return Vec2(self.x * scalar, self.y * scalar)

	def __nonzero__(self):
		return abs(self.x) > ERROR_TOLERANCE or abs(self.y) > ERROR_TOLERANCE

	def __div__(self, scalar):
		return self * (1.0 / scalar)

	__rmul__ = __mul__

	def __iter__(self):
		"""For easy unpacking"""
		yield self.x
		yield self.y

	def mag(self):
		try:
			return self._mag
		except AttributeError:
			self._mag = math.sqrt(self.x * self.x  + self.y * self.y)
			return self._mag
	def mag2(self):
		return self.x * self.x  + self.y * self.y

	def normalized(self):
		# check for mag smaller than a threshold to eliminate a class of numerical error problems
		if not self:
			raise ZeroDivisionError("Normalization of very tiny vector is unlikely to give good results")

		return self / self.mag() 

	def dot(self, ano):
		return self.x * ano.x + self.y * ano.y

	def component_of(self, ano):
		"""Component of ano in the direction of self"""
		n = self.normalized()
		return n.dot(ano) * n

	def rotate(self, angle):
		x = self.x
		y = self.y
		sin = math.sin(angle)
		cos = math.cos(angle)
		return Vec2(cos * x - sin * y, sin * x + cos * y)

	def angle(self):
		return math.atan2(self.y, self.x)

	def rotate_degrees(self, angle):
		return self.rotate(angle * math.pi / 180.0)

	def angle_in_degrees(self):
		return self.angle() / math.pi * 180.0

	def perpendicular(self):
		"""Rotatation through 90 degrees, without trig functions"""
		return Vec2(-self.y, self.x)


class Matrix2(object):
	def __init__(self, x11, x12, x21, x22):
		self.x11 = x11
		self.x12 = x12
		self.x21 = x21
		self.x22 = x22
	
	def __mul__(self, vec):
		return Vec2(self.x11 * vec.x + self.x12 * vec.y, self.x21 * vec.x + self.x22 * vec.y)

	@staticmethod
	def rotation(angle):
		sin = math.sin(angle)
		cos = math.cos(angle)
		return Matrix2(cos, -sin, sin, cos)
		


class Rect(object):
	"""An axis-aligned rectangle"""
	def __init__(self, l, b, w, h):
		self.l = l
		self.b = b
		self.w = w
		self.h = h

	def _t(self):
		return self.b + self.h
	t = property(_t)

	def _r(self):
		return self.l + self.w
	r = property(_r)

	def bottomleft(self):
		return Vec2(self.l, self.b)

	def topleft(self):
		return Vec2(self.l, self.t)
	
	def topright(self):
		return Vec2(self.r, self.t)

	def bottomright(self):
		return Vec2(self.r, self.b)

	def center(self):
		return Vec2(self.l + self.w * 0.5, self.b + self.h * 0.5)

	def intersects(self, r):
		return r.r > self.l and r.l < self.r \
                	and r.t > self.b and r.b < self.t

	def __nonzero__(self):
		return bool(self.w or self.h)

	def contains(self, point):
		return p.x >= self.l and p.x < self.r \
			and p.y >= self.b and p.y < self.t

	def intersection(self, r):
		if not self.intersects(r):
			return None
		xs = [self.l, self.r, r.l, r.r]
		ys = [self.b, self.t, r.b, r.t]
		xs.sort()
		ys.sort()
		return Rect(xs[1], ys[1], xs[2] - xs[1], ys[2] - ys[1])

	def vertices(self):
		"""Pyglet vertex list"""
		vs = []
		for v in [self.bottomleft(), self.bottomright(), self.topright(), self.topleft()]:
			vs += [v.x, v.y]
		return vs

	def scale_about_center(self, sx, sy=None):
		if sy is None:
			sy = sx
		return Rect.from_center(self.center(), self.w * sx, self.h * sy)

	@staticmethod
	def from_center(c, w, h):
		return Rect(c.x - w * 0.5, c.y - h * 0.5, w, h)

	@staticmethod
	def from_corners(c1, c2):
		x1, x2 = sorted([c1.x, c2.x])
		y1, y2 = sorted([c1.y, c2.y])
		return Rect(x1, y1, x2 - x1, y2 - y1)
