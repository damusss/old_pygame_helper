"""
FILE FOR TESTING NEW FEATURES
"""

import pygame,random
from pygame_helper import helper

screen,clock = helper.init((800,600),debug_activated=True)

main = helper.Sprite(helper.empty_image((300,150),"green"),(100,100),speed=(1,1.5),direction=(1,0.3))
collide = [helper.Sprite(helper.empty_image((100,100),"red"),(500,300)),helper.Sprite(helper.empty_image((100,100),"blue"),(650,350))]
ray = helper.Ray(main.position,main.direction,200,"orange",5)

while True:
	for e in helper.get_events():
		helper.quit_event(e)

	main.draw(screen)
	for c in collide:
		c.draw(screen)
	main.update_positions()
	ray.follow_sprite(main)

	helper.debug(round(clock.get_fps()),len(ray.cast(collide,True,screen)))

	helper.update_window(clock, 60,screen,"black")