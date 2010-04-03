#!/usr/bin/python

"""The Bamboo Warrior

A PyWeek 10 game by Daniel Pope"""

from optparse import OptionParser

parser = OptionParser()
parser.add_option('-f', '--fullscreen', action='store_true', help='Start fullscreen', default=False)
parser.add_option('-d', '--resolution', help='Screen or window resolution (WxH)', default='1280x720')
parser.add_option('-p', '--profiler', action='store_true', help='Print profiler stats on exit', default=False)

options, arguments = parser.parse_args()

from bamboo.menu import MenuGameState
from bamboo.game import Game

game = Game(options)
state = MenuGameState(game)
game.set_gamestate(state)

if options.profiler:
	import cProfile
	cProfile.run('game.run()')
else:
	game.run()
