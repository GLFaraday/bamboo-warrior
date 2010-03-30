import math

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

	def __neg__(self, ano):
		return Vec2(-self.x, -self.y)

	def __mul__(self, scalar):
		return Vec2(self.x * scalar, self.y * scalar)

	__rmul__ = __mul__

	def __iter__(self):
		"""For easy unpacking"""
		yield self.x
		yield self.y

	def mag(self):
		return (self.x ** 2 + self.y ** 2) ** 0.5

	def rotate(self, angle):
		x = self.x
		y = self.y
		sin = math.sin(angle)
		cos = math.cos(angle)
		return Vec2(cos * x - sin * y, sin * x + cos * y)

	def angle(self):
		return math.atan2(self.y, self.x)

	def angle_in_degrees(self):
		return self.angle() / math.pi * 180
