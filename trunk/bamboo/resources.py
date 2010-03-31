import pyglet


def set_anchor(tex, anchor_x, anchor_y):
	"""Sets the anchor point for the texture, but accepts a special value
	'center' to center the texture in that direction.
	"""
	if anchor_x == 'center':
		tex.anchor_x = tex.width / 2
	elif anchor_x == 'right':
		tex.anchor_x = tex.width
	else:
		tex.anchor_x = anchor_x

	if anchor_y == 'center':
		tex.anchor_y = tex.height / 2
	elif anchor_y == 'top':
		tex.anchor_y = tex.height
	else:
		tex.anchor_y = anchor_y


class ResourceTracker(object):
	"""Superclass for objects that want to ensure resources are loaded as they are added to the scene.

	Subclasses implement the class method on_class_load to load the resources.
	"""

	_resources_loaded = False

	graphics = {}
	sounds = {}
	textures = {}

	@classmethod
	def load_texture(cls, name, resource=None, anchor_x='center', anchor_y=0):
		if resource is None:
			resource = cls.__name__.lower() + '-' + name + '.png'
		im = pyglet.resource.texture(resource)
		set_anchor(im, anchor_x, anchor_y)
		cls.textures[name] = im
		return im

	@classmethod
	def load_sprite(cls, name, resource=None, anchor_x='center', anchor_y=0):
		if resource is None:
			resource = cls.__name__.lower() + '-' + name + '.png'
		im = pyglet.resource.image(resource)
		set_anchor(im, anchor_x, anchor_y)
		cls.graphics[name] = im

	@classmethod
	def load_directional_sprite(cls, name, resource=None, anchor_x='center', anchor_y=0):
		if resource is None:
			resource = cls.__name__.lower() + '-' + name + '.png'
		im = pyglet.resource.image(resource)
		set_anchor(im, anchor_x, anchor_y)
		cls.graphics[name + '-r'] = im
		cls.graphics[name + '-l'] = im.get_transform(flip_x=True)

	@classmethod
	def load_sound(cls, name, resource=None):
		if resource is None:
			resource = cls.__name__.lower() + '-' + name + '.wav'
		cls.sounds[name] = pyglet.resource.media(resource, streaming=False)

	@classmethod
	def load_animation(cls, name, resource, frames, anchor_x='center', anchor_y=0, framerate=0.1):
		if resource is None:
			resource = cls.__name__.lower() + '-' + name + '%d.png'
		frame_textures = [pyglet.resource.image(resource % (i + 1)) for i in range(frames)]
		for f in frame_textures:
			set_anchor(f, anchor_x, anchor_y)
		anim = pyglet.image.Animation.from_image_sequence(frame_textures, framerate)
		cls.graphics[name + '-r'] = anim
		cls.graphics[name + '-l'] = anim.get_transform(flip_x=True)

	@classmethod
	def on_class_load(cls):
		"""Load the resources required to use the class.

		Subclasses would typically call
		cls.load_sprite()
		cls.load_directional_sprite()
		cls.load_sound()
		cls.load_texture()
		"""

	@classmethod
	def load_resources(cls):
		if cls._resources_loaded:
			return

		try:
			loader = cls.on_class_load
		except AttributeError:
			pass
		else:
			loader()

		cls._resources_loaded = True

	# TODO: unload resources
