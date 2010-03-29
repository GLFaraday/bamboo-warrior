from base import Actor

class Torii(Actor):
	initial_animation = 'torii'
	@classmethod
	def on_class_load(cls):
		cls.load_sprite('torii', 'torii.png')
