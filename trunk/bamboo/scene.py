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


class Scene(object):
	"""Used to manage rendering for a level"""
	def __init__(self, window, level):
		from bamboo.camera import FixedCamera
		self.window = window
		self.level = level
		self.camera = FixedCamera.for_window(self.window)
		self.background_tex = pyglet.resource.image('background.png')

	def save_screenshot(self):
		"""Save a screenshot to the grabs/ directory"""
		gl.glPixelTransferf(gl.GL_ALPHA_BIAS, 1.0)	# don't transfer alpha channel
		image = pyglet.image.ColorBufferImage(0, 0, self.window.width, self.window.height)
		n = 1
		outfile = 'grabs/screenshot.png'
		while os.path.exists(outfile):
			n += 1
			outfile = 'grabs/screenshot-%d.png' % n
		image.save(outfile)
		gl.glPixelTransferf(gl.GL_ALPHA_BIAS, 0.0)	# restore alpha channel transfer
		return outfile

	def draw_background(self, viewport):
		gl.glEnable(gl.GL_TEXTURE_2D)
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.background_tex.get_texture().id)
		pyglet.graphics.draw(4, gl.GL_QUADS,
			('v2i', [0,0, viewport.width,0, viewport.width,viewport.height, 0,viewport.height]),
			('t3f', self.background_tex.tex_coords),
		)

	def draw(self):
		viewport = self.camera.get_viewport()
		self.draw_background(viewport)
		viewport.apply_transform()
		# set up matrix for viewport
		# compute PVS
		for l in self.level.get_actors():
			l.draw()
		self.level.ground.draw()
		# render PVS
		# reset matrix
		viewport.reset_transform()

