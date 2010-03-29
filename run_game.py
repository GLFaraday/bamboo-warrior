#!/usr/bin/python

"""The Bamboo Warrior

A PyWeek 10 game by Daniel Pope"""

import math
import os.path
import random

import pyglet
from pyglet.window import key
from pyglet import gl

window = pyglet.window.Window(1280, 800)

pyglet.resource.path = ['resources/sprites', 'resources/textures', 'resources/music', 'resources/sounds']
pyglet.resource.reindex()

GRAVITY = 3
GROUND_Y = 60

class Samurai(object):
	FALL_SPEED = -5		#threshold at which to play falling animation

	def __init__(self, x=60):
		self.x = x
		self.y = 0
		self.dir = 'r'
		self.vx = 0
		self.vy = 0
		self.current = None
		self.load_resources()

		self.crouching = False

	def run_right(self):
		self.dir = 'r'
		self.vx = min(15, self.vx + 5)
		self.crouching = False

	def run_left(self):
		self.dir = 'l'
		self.vx = max(-15, self.vx - 5)
		self.crouching = False

	def apply_friction(self):
		if not self.is_on_ground():
			return

		if self.vx > 0:
			self.vx = max(0, self.vx - 1)
		elif self.vx < 0:
			self.vx = min(0, self.vx + 1)

	def crouch(self):
		if self.is_on_ground():
			self.crouching = True
			self.apply_friction()

	def stop(self):
		self.crouching = False
		self.apply_friction()

	def is_on_ground(self):
		return self.y <= (ground.height_at(self.x) + 2)

	def jump(self):
		if self.is_on_ground():
			self.crouching = False
			self.vy = 30
			self.y += 30 # leave the ground
			self.play_sound('jumping')

	def play_sound(self, name):
		self.sounds[name].play()

	def play_animation(self, name):
		k = name + '-' + self.dir
		if self.current == k:
			return 
		self.current = k

	def update_animation(self):
		if self.crouching:
			self.play_animation('crouching')
		elif self.is_on_ground():
			if self.vx:
				self.play_animation('running')
			else:
				self.play_animation('standing')
		else:
			if self.vy <= self.FALL_SPEED:
				self.play_animation('falling')
			else:
				self.play_animation('jumping')

	def update(self):
		self.x += self.vx
		gh = ground.height_at(self.x)
		if not self.is_on_ground():
			if self.y + self.vy - GRAVITY <= gh + 2:
				self.y = gh
				self.vy = 0
			else:
				vy0 = self.vy
				self.vy -= GRAVITY
				self.y += self.vy
		else:
			self.y = gh
		self.update_animation()

	resources_loaded = False

	@classmethod
	def load_sprite(cls, name, anchor_x=30, anchor_y=0):
		im = pyglet.resource.image('samurai-%s.png' % name)
		im.anchor_x = anchor_x
		im.anchor_y = anchor_y
		cls.graphics[name + '-r'] = pyglet.sprite.Sprite(im)
		cls.graphics[name + '-l'] = pyglet.sprite.Sprite(im.get_transform(flip_x=True))

	@classmethod
	def load_resources(cls):
		if cls.resources_loaded:
			return
		cls.graphics = {}
		cls.sounds = {}

		cls.load_sprite('standing', anchor_x=30)
		cls.load_sprite('crouching', anchor_x=30)
		cls.load_sprite('jumping', anchor_x=50, anchor_y=10)
		cls.load_sprite('falling', anchor_x=50)
		
		cls.sounds['jumping'] = pyglet.resource.media('samurai-jumping.wav', streaming=False)

		running_frames = [pyglet.resource.image('samurai-running%d.png' % (i + 1)) for i in range(6)]
		for f in running_frames:
			f.anchor_x = 105
		running_anim = pyglet.image.Animation.from_image_sequence(running_frames, 0.1)
		cls.graphics['running-r'] = pyglet.sprite.Sprite(running_anim) 
		cls.graphics['running-l'] = pyglet.sprite.Sprite(running_anim.get_transform(flip_x=True))

	def draw(self):
		if not self.current:
			self.play_animation('standing')
		sprite = self.graphics[self.current]
		sprite.set_position(self.x, self.y)
		sprite.draw() 


class Ground(object):
	def __init__(self, width=800, heightmap=[100,100,165,180,120,140]):
		self.width = width
		self.unit_width = width / (len(heightmap) - 1)
		self.heightmap = heightmap
		self.create_batch()

		self.wind_phase = 0

	resources_loaded = False

	def height_at(self, x):
		segment = x // self.unit_width
		if segment < 0:
			return self.heightmap[0]
		if segment >= (len(self.heightmap) - 1):
			return self.heightmap[-1]
		frac = float(x % self.unit_width) / self.unit_width
		y1, y2 = self.heightmap[segment:segment + 2]
		return frac * y2 + (1 - frac) * y1

	@classmethod
	def load_resources(cls):
		if cls.resources_loaded:
			return
		cls.earth = pyglet.resource.texture('earth.png')
		cls.grass = pyglet.resource.texture('grass.png')

	def create_batch(self):
		self.load_resources()
		layer1 = pyglet.graphics.OrderedGroup(1)
		layer2 = pyglet.graphics.OrderedGroup(2)
		earthgroup = pyglet.graphics.TextureGroup(self.earth, parent=layer1)
		grassgroup = pyglet.sprite.SpriteGroup(self.grass, pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA, parent=layer2)
		
		batch = pyglet.graphics.Batch()

		earth_vertices = []
		earth_texcoords = []
		grass_vertices = []
		grass_texcoords = []

		for i, h in enumerate(self.heightmap):
			x = self.unit_width * i
			earth_vertices += [x, 0, x, h]
			earth_texcoords += [x / 256.0, 1 - h / 256.0, x / 256.0, 1]

			grass_vertices += [x, h - 5, x, h + self.grass.height - 5]
			grass_texcoords += [x / 128.0, self.grass.tex_coords[1], x / 128.0, self.grass.tex_coords[7]]
		
		batch.add(len(earth_vertices) / 2, gl.GL_QUAD_STRIP, earthgroup, ('v2i', earth_vertices), ('t2f', earth_texcoords))
		self.grass_list = batch.add(len(grass_vertices) / 2, gl.GL_QUAD_STRIP, grassgroup, ('v2f', grass_vertices), ('t2f', grass_texcoords))
		
		self.batch = batch

	def update_grass(self):
		self.wind_phase += 0.08
		for i in range(len(self.heightmap)):
			base_x = i * self.unit_width
			dx = 4 * math.sin(self.wind_phase + base_x / 128.0 * 0.5) + 3 * math.sin(self.wind_phase * 0.375 + base_x / 128.0 * 0.5)
			self.grass_list.vertices[i * 4] = base_x + dx * -0.2
			self.grass_list.vertices[i * 4 + 2] = base_x + dx

	def draw(self):
		self.batch.draw()


samurai = Samurai()
ground = Ground(width=1280)
		
class BambooTree(object):
	height = 20

	PIECE_HEIGHT = 61

	def __init__(self, x=60, height=20):
		self.height = height
		self.x = x
		self.y = ground.height_at(x)
		self.create_sprites()

	resources_loaded = False

	@classmethod
	def load_resources(cls):
		if cls.resources_loaded:
			return
		cls.piece = pyglet.resource.image('bamboo-piece.png')
		cls.leaf1 = pyglet.resource.image('bamboo-leaf1.png')
		cls.leaf2 = pyglet.resource.image('bamboo-leaf2.png')
		cls.resources_loaded = True

	def create_sprites(self):
		self.load_resources()
		self.batch = pyglet.graphics.Batch()
		self.sprites = []

		for i in range(self.height):
			if i > 7:
				if random.randint(0, 3) == 0:
					self.sprites.append(pyglet.sprite.Sprite(self.leaf1, x=self.x + 23, y=self.PIECE_HEIGHT * i + self.y, batch=self.batch))
				if random.randint(0, 3) == 0:
					self.sprites.append(pyglet.sprite.Sprite(self.leaf2, x=self.x - 92, y=self.PIECE_HEIGHT * i + self.y, batch=self.batch))
			self.sprites.append(pyglet.sprite.Sprite(self.piece, x=self.x, y=self.PIECE_HEIGHT * i + self.y, batch=self.batch))

	def draw(self):
		self.batch.draw()

trees = [BambooTree(random.randint(0, 9) * 128 + 64) for i in range(3)]

torii_sprite = pyglet.resource.image('torii.png')
torii_sprite.anchor_x = torii_sprite.width / 2
torii = pyglet.sprite.Sprite(torii_sprite, x=800, y=120)


def update(foo):
	if keys[key.UP]:
		samurai.jump()

	if keys[key.DOWN]:
		samurai.crouch()
	elif keys[key.RIGHT]:
		samurai.run_right()
	elif keys[key.LEFT]:
		samurai.run_left()
	else:
		samurai.stop()

	samurai.update()

	ground.update_grass()

background_tex = pyglet.resource.image('background.png')
def draw_background():
	gl.glEnable(gl.GL_TEXTURE_2D)
	gl.glBindTexture(gl.GL_TEXTURE_2D, background_tex.get_texture().id)
	pyglet.graphics.draw(4, gl.GL_QUADS,
		('v2i', [0,0, window.width,0, window.width,window.height, 0,window.height]),
		('t3f', background_tex.tex_coords),
	)

@window.event
def on_draw():
	draw_background()
#	window.clear()
	torii.draw()
	samurai.draw()
	for tree in trees:
		tree.draw()
	ground.draw()

#window.push_handlers(pyglet.window.event.WindowEventLogger())

def save_screenshot():
	"""Save a screenshot to the grabs/ directory"""
	gl.glPixelTransferf(gl.GL_ALPHA_BIAS, 1.0)	# don't transfer alpha channel
	image = pyglet.image.ColorBufferImage(0, 0, window.width, window.height)
	n = 1
	outfile = 'grabs/screenshot.png'
	while os.path.exists(outfile):
		n += 1
		outfile = 'grabs/screenshot-%d.png' % n
	image.save(outfile)
	gl.glPixelTransferf(gl.GL_ALPHA_BIAS, 0.0)	# restore alpha channel transfer
	return outfile

def on_key_press(code, modifiers):
	if code == key.F12:
		print "Wrote", save_screenshot()
		return pyglet.event.EVENT_HANDLED

window.push_handlers(on_key_press=on_key_press)

keys = key.KeyStateHandler()
window.push_handlers(keys)

music = pyglet.resource.media('shika-no-toone.ogg')
music.play()

FPS = 30
pyglet.clock.schedule_interval(update, (1.0/FPS))
pyglet.clock.set_fps_limit(FPS)
pyglet.app.run()
