from bamboo.resources import ResourceTracker


class Actor(ResourceTracker):
	initial_animation = None

	x = None
	y = None
	level = None

	def play_sound(self, name):
		"""Play a named sound from the Actor's resources"""
		self.sounds[name].play()

	def play_animation(self, name):
		"""Set the current animation""" 
		self.current = name

	def draw(self):
		"""Subclasses should implement this method to draw the actor"""	
		sprite = self.graphics[self.current]
		sprite.set_position(self.x, self.y)
		sprite.draw() 

	def update(self):
		"""Subclasses can implement this method if necessary to implement game logic"""

	def on_spawn(self):
		"""Subclasses can implement this method to initialise the actor"""
		if self.initial_animation:
			self.play_animation(self.initial_animation)
