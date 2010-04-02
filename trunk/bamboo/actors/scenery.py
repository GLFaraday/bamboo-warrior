from base import Actor

class Torii(Actor):
	initial_animation = 'torii'
	layer = 0
	@classmethod
	def on_class_load(cls):
		cls.load_sprite('torii', 'torii.png')
