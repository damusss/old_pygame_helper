#  imports
import pygame,sys
from pygame.constants import *
from pygame.locals import *
from typing import Tuple
# modules imports
from graphics import *
from events import *
from sprites import *
from classes import *
from saving import *
import graphics,events,sprites,classes,saving

"""
This is the main modules with 3 main functions. The content of the other modules are all imported aswell.
"""

# globals
debug_mode = False
debug_font = None

# INIT
def init(window_sizes:Tuple[int,int],window_caption:str="Pygame Helper Window",window_flag:int=0,window_icon_path:str=None,debug_activated:bool=False,debug_font_size:int=30)->Tuple[pygame.Surface,pygame.time.Clock]:
	"""
	Init pygame, setup it and return the main screen and the clock in a tuple.
	"""
	global debug_mode,debug_font
	# init
	pygame.init()
	# get main objects
	screen = pygame.display.set_mode(window_sizes,window_flag)
	clock = pygame.time.Clock()
	# set caption and icon
	pygame.display.set_caption(window_caption)
	if window_icon_path:
		icon_surface = load_image(window_icon_path,True)
		pygame.display.set_icon(icon_surface)
	# message
	print("Thanks for using pygame helper.")
	# set debug mode
	if debug_activated:
		debug_mode = True
		debug_font = pygame.font.Font(None,debug_font_size)
		print("Debug mode is activated - disable before publishing!")
	# return objects
	return screen,clock

# DEBUG
def debug(*debug_items,to_console:bool=False,surface_to_debug_on:pygame.Surface=None,x:int=20,y:int=20)->None:
	"""
	Debug to the screen or console whatever you pass to it.
	"""
	if debug_mode:
		string = "[debug]: "
		for item in debug_items:
			string += str(item) + ", "
		if to_console:
			print(string)
		else:
			if not surface_to_debug_on:
				surface_to_debug_on = pygame.display.get_surface()
			surface_to_debug_on.blit(debug_font.render(string,True,"white","black"),(x,y))
	else:
		print("Debug mode is not activated. Enable this option from the init method.")

# QUIT
def quit()->None:
	"""
	Quit pygame and exit.
	"""
	pygame.quit()
	sys.exit()
