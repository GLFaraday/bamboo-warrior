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

pyglet.resource.path = ['resources/sprites', 'resources/textures', 'resources/music', 'resources/sounds', 'resources/levels']
pyglet.resource.reindex()


from bamboo.actors.samurai import Samurai
from bamboo.actors.scenery import Torii
from bamboo.actors.trees import BambooTree, BackgroundBambooTree
from bamboo.terrain import Terrain
from bamboo.level import Level
from bamboo.scene import Scene

level = Level(Terrain(width=1280))
scene = Scene(window, level)

level.spawn(Torii(), x=650)

for i in range(4):
	level.spawn(BackgroundBambooTree(angle=(random.random() - 0.5) * 0.2), x=random.random() * window.width)

for i in range(3):
	level.spawn(BambooTree(), x=random.randint(0, 9) * 128 + 64)

samurai = Samurai()
level.spawn(samurai, x=60)




def update(foo):
	if keys[key.Z]:
		samurai.jump()

	if keys[key.UP]:
		samurai.climb_up()
	elif keys[key.DOWN]:
		if samurai.is_climbing():
			samurai.climb_down()
		else:
			samurai.crouch()
	elif keys[key.RIGHT]:
		samurai.run_right()
	elif keys[key.LEFT]:
		samurai.run_left()
	else:
		samurai.stop()

	samurai.update()

	level.update()


@window.event
def on_draw():
	scene.draw()
#	draw_background()
##	window.clear()
#	torii.draw()
#	samurai.draw()
#	for tree in trees:
#		tree.draw()
#	level.ground.draw()


def on_key_press(code, modifiers):
	if code == key.F12:
		print "Wrote", scene.save_screenshot()
		return pyglet.event.EVENT_HANDLED

window.push_handlers(on_key_press=on_key_press)

keys = key.KeyStateHandler()
window.push_handlers(keys)

music = pyglet.resource.media('shika-no-toone.ogg')
music.play()

FPS = 60

pyglet.clock.schedule_interval(update, (1.0/FPS))
pyglet.clock.set_fps_limit(FPS)
pyglet.app.run()
