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
		return Rect(l, b, self.width, self.height)

	def apply_transform(self):
		gl.glPushMatrix(gl.GL_MODELVIEW)
		bounds  = self.bounds()
		gl.glTranslatef(-bounds.l, -bounds.b, 0)

	def reset_transform(self):
		gl.glPopMatrix(gl.GL_MODELVIEW)


class InfiniteDistanceBackground(object):
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

class NearBackground(object):
	def __init__(self, texturename, level, scale=2, y=100, depth=0.1):
		self.texture = pyglet.resource.texture(texturename)
		self.scale = scale * (1 + depth)
		self.level_w = level.width
		self.w = self.level_w * (1 + depth)
		self.y = y
		self.create_batch(level)
	
	def create_batch(self, level):
		self.batch = pyglet.graphics.Batch()
		self.group = pyglet.sprite.SpriteGroup(self.texture, gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
		tex = self.texture
		repeats = float(self.w) / (tex.width * self.scale)
		self.vertexlist = self.batch.add(4, gl.GL_QUADS, self.group,
			('v2f', [0,self.y, self.w,self.y, self.w,tex.height * self.scale + self.y, 0,tex.height * self.scale + self.y]),
			('t2f', [0,0, repeats,0, repeats,0.99, 0,0.99])
		)

	def draw(self, viewport):
		bs = viewport.bounds()
		wfrac = bs.l / float(self.level_w - bs.w)
		dx = (self.w - self.level_w) * (wfrac - 0.5)

		gl.glPushMatrix(gl.GL_MODELVIEW)
		gl.glTranslatef(dx, 0, 0)
		self.batch.draw()
		gl.glPopMatrix(gl.GL_MODELVIEW)


class Scene(object):
	"""Used to manage rendering for a level"""
	def __init__(self, window, level):
		from bamboo.camera import FixedCamera
		self.window = window
		self.level = level
		self.camera = FixedCamera.for_window(self.window)
		self.background = InfiniteDistanceBackground('distant-background.png', window)
		self.background2 = NearBackground('bamboo-forest.png', level, depth=0.15)
		self.background3 = NearBackground('bamboo-forest.png', level, depth=0.4, y=-150)
		self.batch = pyglet.graphics.Batch()
		self.fps = pyglet.clock.ClockDisplay()

	def update(self):
		for a in self.level.get_actors():
			a.update_batch(self.batch)

	def draw(self):
		viewport = self.camera.get_viewport()

		self.background.draw()
		viewport.apply_transform()
		self.background3.draw(viewport)
		self.background2.draw(viewport)
		# set up matrix for viewport
		# compute PVS
		self.batch.draw()	
		self.level.ground.draw()
		# render PVS
		# reset matrix
		viewport.reset_transform()
		#draw HUD elements
		self.fps.draw()

