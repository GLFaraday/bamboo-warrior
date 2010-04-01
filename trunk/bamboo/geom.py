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
		return (self.x * self.x + self.y * self.y) ** 0.5

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
