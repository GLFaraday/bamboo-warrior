import os.path

import pyglet
from pyglet import gl

from bamboo.resources import ResourceTracker
from bamboo.geom import Rect


class Viewport(object):
	def __init__(self, width, height, center_x=0, center_y=0, scale=1):
		self.width = width
		self.height = height
		self.x = center_x
		self.y = center_y
		self.scale = scale
		
	def bounds(self):
		l = self.x - self.width // 2
		b = self.y - self.height // 2
		return Rect(l, b, l, b + self.height)

	def apply_transform(self):
		gl.glPushMatrix(gl.GL_MODELVIEW)
		bounds  = self.bounds()
		gl.glTranslatef(-bounds.l, -bounds.b, 0)

	def reset_transform(self):
		gl.glPopMatrix(gl.GL_MODELVIEW)


class Background(object):
	def __init__(self, texturename, window):
		self.texture = pyglet.resource.texture(texturename)
		self.create_batch(window)
	
	def create_batch(self, window):
		self.batch = pyglet.graphics.Batch()
		self.group = pyglet.sprite.SpriteGroup(self.texture, gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
		self.vertexlist = self.batch.add(4, gl.GL_QUADS, self.group,
			('v2i', [0,0, window.width,0, window.width,window.height, 0,window.height]),
			('t3f', self.texture.tex_coords),
		)
#		from bamboo.actors.trees import BackgroundBambooTree
#		import random
#		BackgroundBambooTree.load_resources()
#		self.trees = []
#		for i in range(20):
#			t = BackgroundBambooTree(angle=(random.random() - 0.5) * 0.2, x=random.random() * window.width)
#			t.create_sprites(self.batch, parent=pyglet.graphics.OrderedGroup(2))
#			self.trees.append(t)

	def draw(self):
		self.batch.draw()


class Scene(object):
	"""Used to manage rendering for a level"""
	def __init__(self, window, level):
		from bamboo.camera import FixedCamera
		self.window = window
		self.level = level
		self.camera = FixedCamera.for_window(self.window)
		self.background = Background('distant-background.png', window)
		self.background2 = Background('bamboo-forest.png', window)

	def draw(self):
		viewport = self.camera.get_viewport()
		self.background.draw()
		self.background2.draw()
		viewport.apply_transform()
		# set up matrix for viewport
		# compute PVS
		for l in self.level.get_actors():
			l.draw()
		self.level.ground.draw()
		# render PVS
		# reset matrix
		viewport.reset_transform()
