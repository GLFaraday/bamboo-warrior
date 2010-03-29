import pyglet
from pyglet import gl

from bamboo.resources import ResourceTracker


class Viewport(object):
	def __init__(self, window, center_x=0, center_y=0):
		self.width = window.width
		self.height = window.height
		self.look_at(center_x, center_y)

	def look_at(self, x, y):
		self.x = x
		self.y = y

	def bounds(self):
		l = x - self.width // 2
		b = y - self.height // 2
		return l, b, l + self.width, b + self.height


class Scene(object):
	"""Used to manage rendering for a level"""
	def __init__(self, window, level):
		self.window = window
		self.level = level
		self.viewport = Viewport(window)
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

	def draw_background(self):
		viewport = self.viewport
		gl.glEnable(gl.GL_TEXTURE_2D)
		gl.glBindTexture(gl.GL_TEXTURE_2D, self.background_tex.get_texture().id)
		pyglet.graphics.draw(4, gl.GL_QUADS,
			('v2i', [0,0, viewport.width,0, viewport.width,viewport.height, 0,viewport.height]),
			('t3f', self.background_tex.tex_coords),
		)

	def draw(self):
		self.draw_background()
		# set up matrix for viewport
		# compute PVS
		for l in self.level.get_actors():
			l.draw()
		self.level.ground.draw()
		# render PVS
		# reset matrix

