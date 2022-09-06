import pygame, math
from graphics import *
from random import uniform, choice
from typing import Union,List, Tuple
import sprites
from pygame import Rect
from pygame.font import Font
# pathfining
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement

"""
This module contains useful classes to use in the game such as particles, trails, text, timers, buttons.
"""

# MATH UTILS FUNCTIONS
def det(a,b):
	"""
	I have no idea but the code is just: "return a[0]*b[1]-a[1]*b[0]".
	"""
	return a[0]*b[1]-a[1]*b[0]

def in_range(a,b,c):
	"""
	Check if a number is in the range of two others.
	"""
	return c>=min(a, b) and c<=max(a,b)

def dist(p1,p2):
	"""
	Calculate distance between two points.
	"""
	return math.sqrt((p2[0]-p1[0])**2+(p2[1]-p1[1])**2)

def tuple_slope(tuplee:Tuple[Tuple[float,float],Tuple[float,float]])->float:
	"""
	Find the slope of a line that is made of tuples.
	"""
	if (tuplee[1][0]-tuplee[0][0]) == 0:
		return None
	return (tuplee[1][1]-tuplee[0][1])/(tuplee[1][0]-tuplee[0][0])

# RAYCAST
class Ray():
	"""
	Another way of checking collisions between a ray and a list of sprites.

	That is the class version, meaning the ray is created once and only its attributes are changed.

	A bit more efficient, but only useful if the check is run every frame.

	Do not change the attributes that starts with a _, only use the functions! Or it will break.

	The thicness will not effect the ray collision range, just a visual effect.
	"""
	def __init__(self,origin:Tuple[int,int],direction:Tuple[float,float],lenght:int,color:Union[str,Tuple[int,int,int]]="white",thicness:int=2):
		self.ray = Segment(origin, (origin[0]+direction[0]*lenght,origin[1]+direction[1]*lenght),color,thicness)
		self._lenght = lenght
		self._direction = direction

	def cast(self,sprites:List[sprites.Sprite],draw:bool=False,surface:pygame.Surface=None)->List[sprites.Sprite]:
		"""
    	Return a list with the sprites that collides with the ray.
    	"""
		colliding = []
		for sprite in sprites:
			if self.ray.colliderect(sprite.rect):
				colliding.append(sprite)
		if draw:
			self.ray.draw(surface)
		return colliding

	def draw(self,surface:pygame.Surface=None):
		"""
		Draw the ray without checking collisions.
		"""
		self.ray.draw(surface)

	def set_origin(self,origin:Tuple[int,int]):
		"""
		Set the origin of the ray, and shift the end.
		"""
		self.ray.start.xy = origin
		self.ray.end.xy = (self.ray.start[0]+self._direction[0]*self._lenght,self.ray.start[1]+self._direction[1]*self._lenght)

	def set_direction(self,direction:Tuple[float,float]):
		"""
		Set the direction of the ray and shift its end.
		"""
		self._direction = direction
		self.ray.end.xy = (self.ray.start[0]+direction[0]*self._lenght,self.ray.start[1]+direction[1]*self._lenght)

	def set_lenght(self,lenght:int):
		"""
		Set the lenght of the ray and shift the end.
		"""
		self._lenght = lenght
		self.ray.end.xy = (self.ray.start[0]+self._direction[0]*lenght,self.ray.start[1]+self._direction[1]*enght)

	def set_color(self,color):
		"""
		Set the color of the ray.
		"""
		self.ray.color = color

	def set_thicness(self,thicness):
		"""
		Set the thicness of the ray.

		This will not effect the ray collision range, just a visual effect.
		"""
		self.ray.thicness = thicness

	def follow_sprite(self,sprite:sprites.Sprite,follow_direction:bool=True):
		"""
		Set the origin to the sprite position and (optional) the direction to the sprite one.
		"""
		self.set_origin(sprite.position)
		if follow_direction:
			self.set_direction(sprite.direction)

# BACKGROUND
class Background():
	"""
	A little bit easier way to make a background. Do not set manually the attributes, always use the methods.
	"""
	def __init__(self,image:pygame.Surface,window_sizes:Tuple[int,int],window_surface:pygame.Surface):
		self.original= image
		self.image = scale_image(self.original,None,window_sizes)
		self.window_sizes = window_sizes
		self.window = window_surface

	def get_image(self)->pygame.Surface:
		return self.image

	def change_image(self,image:pygame.Surface)->pygame.Surface:
		"""
		Change the image and resize it.
		"""
		self.original = image
		self.image = scale_image(self.original,None,self.window_sizes)
		return self.image

	def resize(self,window_sizes:Tuple[int,int]):
		"""
		Resize the image.
		"""
		self.window_sizes = window_sizes
		self.image = scale_image(self.original,None,self.window_sizes)

	def set_window(self,window_surface:pygame.Surface):
		"""
		Change the window surface.
		"""
		self.window= window_surface

	def draw(self):
		"""
		Draw the background.
		"""
		self.window.blit(self.image,(0,0))

# PATHFINING
class PathFinder():
	"""
	A useful pathfinding class to easly find paths for your sprites and making them follow the path.
	"""
	def __init__(self,matrix:List[List[int]],cell_pixel_size:int,allow_diagonal_movement:bool=True):
		self.matrix = matrix

		for row in self.matrix:
			for col in row:
				if col not in [0,1]:
					raise ValueError("Matrix values must be either 0 or 1.")

		self.grid = Grid(len(self.matrix[0]),len(self.matrix),self.matrix)
		self.width = len(self.matrix[0])
		self.height = len(self.matrix)
		self.cell_size = cell_pixel_size
		if allow_diagonal_movement:
			self.finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
		else:
			self.finder = AStarFinder()
		self.current_path = []
		self.collision_rects = []

	def validate_target(self,target_grid_coordinate:Tuple[int,int])->bool:
		"""
		Check if a position is inside the grid and if the node is not a wall.
		"""
		if 0 <= target_grid_coordinate[0] <= self.width-1 and 0 <=target_grid_coordinate[1] <= self.height-1:
			if self.matrix[target_grid_coordinate[1]][target_grid_coordinate[0]] != 0:
				return True
		return False

	def set_sprite_direction(self,sprite:sprites.Sprite):
		"""
		Set the direction of the sprite that is following the path.
		"""
		if self.collision_rects:
			start = pygame.math.Vector2(sprite.rect.center)
			end = pygame.math.Vector2(self.collision_rects[0].center)
			try:
				sprite.direction = (end-start).normalize()
			except:
				sprite.direction = pygame.math.Vector2()
		else:
			sprite.direction = pygame.math.Vector2()

	def sprite_follows_path(self,sprite:sprites.Sprite):
		"""
		Makes one sprite follow the path.
		"""
		if self.collision_rects:
			for rect in self.collision_rects:
				if rect.collidepoint(sprite.rect.center):
					del self.collision_rects[0]
					self.set_sprite_direction(sprite)
		else:
			if self.current_path:
				self.empty_path()

	def sprite_start_path(self,sprite:sprites.Sprite):
		"""
		Make the sprite start following the path (aka setting the direction).
		"""
		self.set_sprite_direction(sprite)

	def empty_path(self):
		"""
		Clear the path and the collision rects.
		"""
		self.current_path.clear()
		self.collision_rects.clear()

	def create_path_collision_rects(self,rect_size:int=4)->List[pygame.Rect]:
		"""
		Create collision rects in the path points to allow sprites to follow it.
		"""
		self.collision_rects.clear()
		if self.current_path:
			self.collision_rects = [pygame.Rect(((point[0]*self.cell_size)+self.cell_size//2-rect_size//2,(point[1]*self.cell_size)+self.cell_size//2-rect_size//2),(rect_size,rect_size)) for point in self.current_path]
		return self.collision_rects

	def draw_path(self,surface:pygame.Surface=None,color:Union[str,Tuple[int,int,int]]="white",line_width:int=3,shift_offset:Union[str,int]="cell_center"):
		"""
		Draw the path if one exists.
		"""
		if not surface:
			surface = pygame.display.get_surface()
		if len(self.current_path) > 1:
			if shift_offset == "cell_center":
				shift_offset = self.cell_size//2
			points = [((point[0]*self.cell_size)+shift_offset,(point[1]*self.cell_size)+shift_offset) for point in self.current_path]
			pygame.draw.lines(surface, color, False, points,line_width)

	def grid_to_pixel(self,grid_coordinate:Tuple[int,int])->Tuple[int,int]:
		"""
		Convert a grid position to a pixel one, using the cell size.
		"""
		return grid_coordinate[0]*self.cell_size,grid_coordinate[1]*self.cell_size

	def pixel_to_grid(self,pixel_coordinate:Tuple[int,int])->Tuple[int,int]:
		"""
		Convert a pixel position to a grid one, using the cell size.
		"""
		return int(pixel_coordinate[0]//self.cell_size),int(pixel_coordinate[1]//self.cell_size)

	def create_path(self,start_grid_coordinate:Tuple[int,int],end_grid_coordinate:Tuple[int,int],sprite:sprites.Sprite=None,collision_rects_size=4)->Tuple[List[Tuple[int,int]],List[pygame.Rect]]:
		"""
		Create a new path between two grid positions. If a sprite is given, it will start following the path.
		"""
		start = self.grid.node(start_grid_coordinate[0], start_grid_coordinate[1])
		end = self.grid.node(end_grid_coordinate[0], end_grid_coordinate[1])
		self.current_path,_ = self.finder.find_path(start, end, self.grid)
		self.grid.cleanup()
		self.create_path_collision_rects(collision_rects_size)
		if sprite:
			self.set_sprite_direction(sprite)
		return self.current_path, self.collision_rects

# GEOMETRY
class Circle():
	"""
	A useful class with circle informations and methods, similar to the pygame rect one.
	"""
	def __init__(self,center:Tuple[int,int],radius:float,color:Union[str,Tuple[int,int,int]]="white",line_width:int=0):
		self.center = pygame.math.Vector2(center)
		self.radius = radius
		self.color = color
		self.line_width = line_width

	@staticmethod
	def from_rect(rect:pygame.Rect,color:Union[str,Tuple[int,int,int]]="white",line_width:int=0):
		"""
		Return a circle made from a rect. This is a static method, working as a second constructor.
		"""
		if rect.w != rect.h:
			raise ValueError("Rect width and height must be the same to create a circle.")
		return Circle(rect.center, rect.w/2,color,line_width)

	def to_rect(self)->pygame.Rect:
		"""
		Return the bounding rect of the circle.
		"""
		return pygame.Rect(self.center.x-self.radius, self.center.y-self.radius, self.radius*2, self.radius*2)

	def set_center(self,pos):
		"""
		Set the center xy attribute.
		"""
		self.center.xy = (pos[0],pos[1])

	def collidemouse(self)->bool:
		"""
		Check if the mouse is hovering the circle.
		"""
		pos = pygame.mouse.get_pos()
		return self.collidepoint(pos[0], pos[1])

	def draw(self,surface:pygame.Surface=None,*direction_args):
		"""
		Draw the circle.
		"""
		if not surface:
			surface = pygame.display.get_surface()
		pygame.draw.circle(surface, self.color, self.center.xy, self.radius,self.line_width,*direction_args)

	def copy(self):
		"""
		Return the exact copy of a circle.
		"""
		return Circle(self.center, self.radius,self.color,self.line_width)

	def move(self,x:int,y:int):
		"""
		Move the circle center.
		"""
		self.center.x += x
		self.center.y += y

	def clamp(self,circle):
		"""
		Move the circle on the center of another one.
		"""
		self.center.xy = circle.xy

	def clip(self, circle): # needs math optimisation
		"""
		I have no idea, copied it from google.
		"""
		length = dist(self.center, circle.center)
		length2 = abs(length - (self.radius + circle.radius))
		newrad = length2 / 2
		newdist = self.radius - newrad
		newvec = pygame.math.Vector2(circle.x - self.x, circle.y - self.y)
		newvec.scale_to_length(newdist)
		return Circle((self.x + newvec.x, self.y + newvec.y), newrad)

	def normalize(self):
		"""
		Correct the radius if negative.
		"""
		self.radius = abs(self.radius)

	def contains(self,circle)->bool:
		"""
		Check if a circle is inside this circle.
		"""
		return dist(self.center, circle.center) + circle.radius <= self.radius

	def collidepoint(self,x:int,y:int)->bool:
		"""
		Check if a point is colliding this circle.
		"""
		return dist(self.center, (x,y)) <= self.radius  

	def collidecircle(self,circle)->bool:
		"""
		Check if two circles are colliding.
		"""
		return dist(self.center, circle.center) < self.radius + circle.radius

	def collidelist(self, circles:list)->tuple:
		"""
		Idk how to explain but it's similar to the rect one.
		"""
		for i in range(len(circles)):
			if dist(self.center, circles[i].center) < self.radius + circles[i].radius:
				return tuple((i,circles[i]))

	def collidelistall(self, circles:list)->List[tuple]:
		"""
		Idk how to explain but it's similar to the rect one.
		"""
		for i in range(len(circles)):
			if dist(self.center, circles[i].center) < self.radius + circles[i].radius:
				yield tuple((i,circles[i]))

	def collidedict(self, circles, use_values:bool = False)->tuple:
		"""
		Idk how to explain but it's similar to the rect one.
		"""
		if not use_values:
			for circle in circles:
				if dist(self.center, circle.center) < self.radius + circle.radius:
					return tuple((circle, circles[circle]))
		else:
			for key in circles.keys():
				if dist(self.center, circles[key].center) < self.radius + circle[key].radius:
					return tuple((key, circles[key]))                    


	def collidedictall(self, circles:dict, use_values:bool = False)->List[tuple]:
		"""
		Idk how to explain but it's similar to the rect one.
		"""
		if not use_values:
			for circle in circles:
				if dist(self.center, circle.center) < self.radius + circle.radius:
					yield tuple((circle, circles[circle]))
		else:
			for key in circles.keys():
				if dist(self.center, circles[key].center) < self.radius + circles[key].radius:
					yield tuple((key, circles[key]))

	@property
	def x(self):
		return self.center.x

	@x.setter
	def x(self,value):
		self.center.x = value

	@property
	def y(self):
		return self.center.y

	@y.setter
	def y(self,value):
		self.center.y = value

	@property
	def diameter(self):
		return self.radius*2

	@diameter.setter
	def diameter(self,value):
		self.radius = value/2

	@property
	def circumference(self):
		return self.radius * (math.pi*2)

	@circumference.setter
	def circumference(self,value):
		self.radius = value / (math.pi*2)

	@property
	def area(self):
		return self.radius**2*math.pi

	@area.setter
	def area(self,value):
		self.radius = math.sqrt(value/math.pi)
	
class Segment():
	"""
	A useful class to more easly work with segments in pygame or in general.
	"""
	def __init__(self,start_pos:Tuple[int,int],end_pos:Tuple[int,int],color:Union[str,Tuple[int,int,int]]="white",thicness:int=2):
		self.start = pygame.math.Vector2(start_pos)
		self.end = pygame.math.Vector2(end_pos)
		self.color = color
		self.thicness = thicness

	def to_tuple(self)->Tuple[Tuple[float,float],Tuple[float,float]]:
		return (self.start.xy,self.end.xy)

	def colliderect(self,rect:pygame.Rect)->bool:
		return any([self.tuple_intersects((rect.topleft,rect.bottomleft)),self.tuple_intersects((rect.topleft,rect.topright)),self.tuple_intersects((rect.bottomleft,rect.bottomright)),self.tuple_intersects((rect.topright,rect.bottomright))])

	def set_start(self,pos:Tuple[int,int]):
		"""
		Set the start xy attribute.
		"""
		self.start.xy = (pos[0],pos[1])

	def set_end(self,pos:Tuple[int,int]):
		"""
		Set the end xy attribute.
		"""
		self.end.xy = (pos[0],pos[1])

	def int(self):
		"""
		Correct any non-int value on the points.
		"""
		self.start.x = int(self.start.x)
		self.start.y = int(self.start.y)
		self.end.x = int(self.end.x)
		self.end.y = int(self.end.y)

	def int_point(self,point:Tuple[float,float])->Tuple[int,int]:
		"""
		Correct any non-int values in a point and return it.
		"""
		return (int(point[0]),int(point[1]))

	def move(self,x:int,y:int):
		"""
		Move the segment by an amount.
		"""
		self.start.x += x
		self.start.y += y
		self.end.x += x
		self.end.y += y

	def copy(self):
		"""
		Return an exact copy of the segment.
		"""
		return Segment(self.start, self.end,self.color,self.thicness)

	def to_line(self):
		"""
		Return a line with the same properties of this segment.
		"""
		return Line(self.start, self.end,self.color,self.thicness)

	def lenght(self)->float:
		"""
		Return the lenght of the segment.
		"""
		return math.dist(self.start,self.end)

	def slope(self)->float:
		"""
		Return the slope of the segment.
		"""
		if (self.end.x-self.start.x) == 0:
			return None
		return (self.end.y-self.start.y)/(self.end.x-self.start.x)

	def is_parallel(self,segment)->bool:
		"""
		Check if two segments are parallel.
		"""
		return self.slope() == segment.slope()

	def tuple_is_parallel(self,tuplee:Tuple[Tuple[float,float],Tuple[float,float]])->bool:
		"""
		Check if this segment and a tuple based segment are parallel.
		"""
		return self.slope() == tuple_slope(tuplee)

	def tuple_intersection_point(self,tuplee:Tuple[Tuple[float,float],Tuple[float,float]])->Tuple[float,float]:
		"""
		If the segment and the tuple based segment intersects, return the point, otherwise return (None,None)
		"""
		if not self.tuple_is_parallel(tuplee):
			if self.tuple_intersects(tuplee):
				return self.tuple_absolute_intersection_point(tuplee)
		return (None,None)

	def tuple_absolute_intersection_point(self,tuplee:Tuple[Tuple[float,float],Tuple[float,float]])->Tuple[float,float]:
		"""
		Calculate the intersection point of a segment and a tuple based segment (non parallel) even if the point is not inside them.
		"""
		if self.tuple_is_parallel(tuplee):
			raise ValueError("Parallel segments cannot intersect.")

		xdiff = (self.start.x-self.end.x,tuplee[0][0]-tuplee[1][0])
		ydiff = (self.start.y-self.end.y,tuplee[0][1]-tuplee[1][1])

		div = det(xdiff,ydiff)

		d = (det(self.start,self.end),det(tuplee[0],tuplee[1]))
		return (det(d,xdiff)/div,det(d,ydiff)/div)

	def tuple_intersects(self,tuplee:Tuple[Tuple[float,float],Tuple[float,float]])->bool:
		"""
		Check if the segment and a tuple based segment intersects.
		"""
		if not self.tuple_is_parallel(tuplee):
			point = self.tuple_absolute_intersection_point(tuplee)
			return in_range(self.start.x,self.end.x,point[0]) and in_range(tuplee[0][0],tuplee[1][0],point[0]) and in_range(self.start.y,self.end.y,point[1]) and in_range(tuplee[0][1],tuplee[1][1],point[1])
		return False

	def absolute_intersection_point(self,segment)->Tuple[float,float]:
		"""
		Calculate the intersection point of two segments (non parallel) even if the point is not inside them.
		"""
		if self.is_parallel(segment):
			raise ValueError("Parallel segments cannot intersect.")

		xdiff = (self.start.x-self.end.x,segment.start.x-segment.end.x)
		ydiff = (self.start.y-self.end.y,segment.start.y-segment.end.y)

		div = det(xdiff,ydiff)

		d = (det(self.start,self.end),det(segment.start,segment.end))
		return (det(d,xdiff)/div,det(d,ydiff)/div)

	def intersection_point(self,segment)->Tuple[float,float]:
		"""
		If the segments intersects, return the point, otherwise return (None,None)
		"""
		if not self.is_parallel(segment):
			if self.intersects(segment):
				return self.absolute_intersection_point(segment)
		return (None,None)

	def intersects(self,segment)->bool:
		"""
		Check if the segments intersects.
		"""
		if not self.is_parallel(segment):
			point = self.absolute_intersection_point(segment)
			return in_range(self.start.x,self.end.x,point[0]) and in_range(segment.start.x,segment.end.x,point[0]) and in_range(self.start.y,self.end.y,point[1]) and in_range(segment.start.y,segment.end.y,point[1])
		return False

	def draw(self,surface:pygame.Surface=None):
		"""
		Draw the segment.
		"""
		if not surface:
			surface = pygame.display.get_surface()
		pygame.draw.line(surface, self.color, self.start.xy, self.end.xy,width=self.thicness)

class Line():
	"""
	Similar to the segment, but with slightly different math, as two non parallel lines always have an intersection.
	"""
	def __init__(self,point1:Tuple[int,int],point2:Tuple[int,int],color:Union[str,Tuple[int,int]]="white",thicness:int=2):
		self.point1 = pygame.math.Vector2(point1)
		self.point2 = pygame.math.Vector2(point2)
		self.color = color
		self.thicness = thicness

	def to_tuple(self)->Tuple[Tuple[float,float],Tuple[float,float]]:
		return (self.point1.xy,self.point2.xy)

	def colliderect(self,rect:pygame.Rect)->bool:
		return any([self.tuple_intersects((rect.topleft,rect.bottomleft)),self.tuple_intersects((rect.topleft,rect.topright)),self.tuple_intersects((rect.bottomleft,rect.bottomright)),self.tuple_intersects((rect.topright,rect.bottomright))])

	def set_point1(self,pos:Tuple[int,int]):
		"""
		Set the point1 xy attribute.
		"""
		self.point1.xy = (pos[0],pos[1])

	def set_point2(self,pos:Tuple[int,int]):
		"""
		Set the point2 xy attribute.
		"""
		self.point2.xy = (pos[0],pos[1])

	def int(self):
		"""
		Correct any non-int value on the points.
		"""
		self.point1.x = int(self.point1.x)
		self.point1.y = int(self.point1.y)
		self.point2.x = int(self.point2.x)
		self.point2.y = int(self.point2.y)

	def int_point(self,point:Tuple[float,float])->Tuple[int,int]:
		"""
		Correct any non-int values in a point and return it.
		"""
		return (int(point[0]),int(point[1]))

	def move(self,x:int,y:int):
		"""
		Move the line by an amount.
		"""
		self.point1.x += x
		self.point1.y += y
		self.point2.x += x
		self.point2.y += y

	def lenght(self)->float:
		"""
		Return the lenght between the two known points.
		"""
		return math.dist(self.point1,self.point2)

	def slope(self)->float:
		"""
		Return the slope of the line.
		"""
		if (self.point2.x-self.point1.x) == 0:
			return None
		return (self.point2.y-self.point1.y)/(self.point2.x-self.point1.x)

	def is_parallel(self,line)->bool:
		"""
		Check if two lines are parallel.
		"""
		return self.slope() == line.slope()

	def tuple_is_parallel(self,tuplee:Tuple[Tuple[float,float],Tuple[float,float]])->bool:
		"""
		Check if this line and a tuple based line are parallel.
		"""
		return self.slope() == tuple_slope(tuplee)

	def tuple_intersection_point(self,tuplee:Tuple[Tuple[float,float],Tuple[float,float]])->Tuple[float,float]:
		"""
		If the line and the tuple based line intersects, return the point, otherwise return (None,None)
		"""
		if not self.tuple_is_parallel(tuplee):
			return self.tuple_absolute_intersection_point(tuplee)
		return (None,None)

	def tuple_absolute_intersection_point(self,tuplee:Tuple[Tuple[float,float],Tuple[float,float]])->Tuple[float,float]:
		"""
		Calculate the intersection point of a line and a tuple based line (non parallel) even if the point is not inside them.
		"""
		if self.tuple_is_parallel(tuplee):
			raise ValueError("Parallel lines cannot intersect.")

		xdiff = (self.point1.x-self.point2.x,tuplee[0][0]-tuplee[1][0])
		ydiff = (self.point1.y-self.point2.y,tuplee[0][1]-tuplee[1][1])

		div = det(xdiff,ydiff)

		d = (det(self.point1,self.point2),det(tuplee[0],tuplee[1]))
		return (det(d,xdiff)/div,det(d,ydiff)/div)

	def tuple_intersects(self,tuplee:Tuple[Tuple[float,float],Tuple[float,float]])->bool:
		"""
		Check if the segment and a tuple based segment intersects.
		"""
		if not self.tuple_is_parallel(tuplee):
			return True
		return False

	def copy(self):
		"""
		Return an exact copy of the line.
		"""
		return Line(self.point1, self.point2,self.color,self.thicness)

	def to_segment(self):
		"""
		Convert the line to a segment.
		"""
		return Segment(self.point1, self.point2,self.color,self.thicness)

	def absolute_intersection_point(self,line)->Tuple[float,float]:
		"""
		Calculate the intersection point of two lines (non parallel, otherwise throws an error).
		"""
		if self.is_parallel(line):
			raise ValueError("Parallel lines cannot intersect.")

		xdiff = (self.point1.x-self.point2.x,line.point1.x-line.point2.x)
		ydiff = (self.point1.y-self.point2.y,line.point1.y-line.point2.y)

		div = det(xdiff,ydiff)

		d = (det(self.point1,self.point2),det(line.point1,line.point2))
		return (det(d,xdiff)/div,det(d,ydiff)/div)

	def intersection_point(self,line)->Tuple[float,float]:
		"""
		If the lines are not parallel, return the intersection point, otherwise return (None,None)
		"""
		if not self.is_parallel(line):
			return self.absolute_intersection_point(line)
		return (None,None)

	def intersects(self,line)->bool:
		"""
		Check if the lines intersects (aka if they are not parallel).
		"""
		if not self.is_parallel(line):
			return True
		return False

	def draw(self,surface:pygame.Surface=None):
		"""
		Draw the line (it will look like a segment).
		"""
		if not surface:
			surface = pygame.display.get_surface()
		pygame.draw.line(surface, self.color, self.point1.xy, self.point2.xy,width=self.thicness)

# PARTICLES
class CircleParticles():
	"""
	A particles generator fully customizable that uses only circles.
	"""
	def __init__(self, 
		origin:Union[Tuple[int,int],List[int],pygame.math.Vector2], 
		anchor_sprite:sprites.Sprite=None,
		anchor_offset:Union[Tuple[int,int],List[int],pygame.math.Vector2]=(0,0),
		active:bool=True,
		colors:List[Union[str,Tuple[int,int,int]]]=["white"],
		use_gravity:bool=True,
		gravity_speed:float=0.1,
		cooldown:int=1000,
		speed_random_range:Tuple[Tuple[float,float],Tuple[float,float]]=((-1.0,1.0),(-1.0,1.0)),
		change_over_time:bool=True,
		change_multiplier:int=-1,
		start_radius:int=3,
		destroy_or_hide_cooldown:int=9999,
		destroy_after_time:bool=False,
		hide_after_time:bool=False):

		self.origin_point = pygame.math.Vector2(origin)
		self.anchor_sprite = anchor_sprite
		self.anchor_offset = pygame.math.Vector2(anchor_offset)

		self.particles = []

		self.use_gravity = use_gravity
		self.gravity_speed = gravity_speed
		self._cooldown = cooldown
		self.speed_random_range = speed_random_range
		self.change_over_time = change_over_time
		self.change_multiplier = change_multiplier
		self._start_scale = start_radius
		self.destroy_or_hide_cooldown = destroy_or_hide_cooldown
		self.destroy_after_time = destroy_after_time
		self.hide_after_time = hide_after_time
		self.active = active
		self.colors = colors

		self.scaleMinuser = self._start_scale/self._cooldown

		self.lastTime = pygame.time.get_ticks()
		self.lastHide = pygame.time.get_ticks()

	def copy(self):
		return CircleParticles(self.origin_point.xy,self.anchor_sprite,self.anchor_offset,self.active,self.colors,self.use_gravity,self.gravity_speed,self.cooldown,self.speed_random_range,self.change_over_time,self.change_multiplier,self.start_radius,self.destroy_or_hide_cooldown,self.destroy_after_time,self.hide_after_time)

	@property
	def cooldown(self)->int:
		return self._cooldown
	
	@cooldown.setter
	def cooldown(self,value:int):
		self._cooldown = value
		self.scaleMinuser = self._start_scale/self._cooldown

	@property
	def start_radius(self)->int:
		return self._start_scale
	
	@start_radius.setter
	def start_radius(self,value:int):
		self._start_scale= value
		self.scaleMinuser = self._start_scale/self._cooldown

	def empty_particles(self)->None:
		"""
		Clear the particle list.
		"""
		self.particles.clear()

	def update_position(self)->None:
		"""
		Change the origin point to the anchor sprite center offsetted.
		"""
		if self.anchor_sprite:
			self.origin_point.xy = self.anchor_offset + self.anchor_sprite.rect.center

	def generate(self)->None:
		"""
		Add one particle to the list.
		"""
		if self.active:
			self.particles.append({"color":choice(self.colors),"pos":list(self.origin_point.xy),"speed":[uniform(self.speed_random_range[0][0],self.speed_random_range[0][1]),uniform(self.speed_random_range[1][0],self.speed_random_range[1][1])],"time":self._cooldown,"scale":self._start_scale})

	def draw(self,surface:pygame.Surface)->None:
		"""
		Blit the particles and update them.
		"""
		if not surface:
			surface = pygame.display.get_surface()
		current = pygame.time.get_ticks()

		toRemove = []

		for particle in self.particles:
			particle["pos"][0] += particle["speed"][0]
			particle["pos"][1] += particle["speed"][1]

			dt = current-self.lastTime

			particle["time"] -= dt

			if self.use_gravity:
				particle["speed"][1] += self.gravity_speed

			if particle["time"] <= 0:
				toRemove.append(particle)

			if self.change_over_time:
				preview = particle["scale"]+((dt*self.scaleMinuser) * self.change_multiplier)
				if round(preview) > 0:
					particle["scale"] = preview

			pygame.draw.circle(surface,particle["color"],(int(particle["pos"][0]),int(particle["pos"][1])),round(particle["scale"]))

		for particle in toRemove:
			self.particles.remove(particle)

		if self.destroy_after_time or self.hide_after_time:
			if current-self.lastHide >= self.destroy_or_hide_cooldown:
				if self.destroy_after_time:
					self.kill()
				elif self.hide_after_time:
					self.active = False
					self.empty_particles()
				self.lastHide = current

		self.lastTime = current

	def kill(self)->None:
		"""
		Delete itself.
		"""
		del self

class Particles():
	"""
	A particles generator fully customizable.
	"""
	def __init__(self, 
	origin:Union[Tuple[int,int],List[int],pygame.math.Vector2],
	 anchor_sprite:sprites.Sprite=None,
	 anchor_offset:Union[Tuple[int,int],List[int],pygame.math.Vector2]=(0,0),
	 images:List[pygame.Surface]=[],
	 active:bool=True,
	 use_gravity:bool=True,
	 gravity_speed:float=0.1,
	 cooldown:int=1000,
	 speed_random_range:Tuple[Tuple[float,float],Tuple[float,float]]=((-1.0,1.0),(-1.0,1.0)),
	 change_over_time:bool=True,
	 change_multiplier:int=-1,
	 start_scale:float=1.0,
	 destroy_or_hide_cooldown:int=9999,
	 destroy_after_time:bool=False,
	 hide_after_time:bool=False):

		self.origin_point = pygame.math.Vector2(origin)
		self.anchor_sprite = anchor_sprite
		self.anchor_offset = pygame.math.Vector2(anchor_offset)

		self.particles = []

		self.use_gravity = use_gravity
		self.gravity_speed = gravity_speed
		self._cooldown = cooldown
		self.speed_random_range = speed_random_range
		self.change_over_time = change_over_time
		self.change_multiplier = change_multiplier
		self._start_scale = start_scale
		self.destroy_or_hide_cooldown = destroy_or_hide_cooldown
		self.destroy_after_time = destroy_after_time
		self.hide_after_time = hide_after_time
		self.active = active

		self.original_images = images if len(images)>0 else [empty_image((5,5),"white")]

		self.scaleMinuser = self._start_scale/self._cooldown

		self.lastTime = pygame.time.get_ticks()
		self.lastHide = pygame.time.get_ticks()

		for image in self.original_images:
			image = scale_image(image,self._start_scale)

	def copy(self):
		return CircleParticles(self.origin_point.xy,self.anchor_sprite,self.anchor_offset,self.original_images,self.active,self.use_gravity,self.gravity_speed,self.cooldown,self.speed_random_range,self.change_over_time,self.change_multiplier,self.start_scale,self.destroy_or_hide_cooldown,self.destroy_after_time,self.hide_after_time)

	@property
	def cooldown(self)->int:
		return self._cooldown
	
	@cooldown.setter
	def cooldown(self,value:int):
		self._cooldown = value
		self.scaleMinuser = self._start_scale/self._cooldown

	@property
	def start_scale(self)->float:
		return self._start_scale
	
	@start_scale.setter
	def start_scale(self,value:float):
		self._start_scale= value
		self.scaleMinuser = self._start_scale/self._cooldown
		for image in self.original_images:
			image = scale_image(image,self._start_scale)

	def empty_particles(self)->None:
		"""
		Empty the particle list.
		"""
		self.particles.clear()

	def update_position(self)->None:
		"""
		Change the origin point to the anchor sprite rect center offsetted.
		"""
		if self.anchor_sprite:
			self.origin_point.xy = self.anchor_offset + self.anchor_sprite.rect.center

	def generate(self)->None:
		"""
		Add one particle to the list.
		"""
		if self.active:
			image = choice(self.original_images)
			self.particles.append({"pos":list(self.origin_point.xy),"speed":[uniform(self.speed_random_range[0][0],self.speed_random_range[0][1]),uniform(self.speed_random_range[1][0],self.speed_random_range[1][1])],"time":self._cooldown,"scale":self._start_scale,"image":image,"original":image})

	def draw(self,surface:pygame.Surface)->None:
		"""
		Blit the particles and update them.
		"""
		if not surface:
			surface = pygame.display.get_surface()
		current = pygame.time.get_ticks()

		toRemove = []

		for particle in self.particles:
			particle["pos"][0] += particle["speed"][0]
			particle["pos"][1] += particle["speed"][1]

			dt = current-self.lastTime

			particle["time"] -= dt

			if self.use_gravity:
				particle["speed"][1] += self.gravity_speed

			if particle["time"] <= 0:
				toRemove.append(particle)

			if self.change_over_time:
				preview = particle["scale"]+((dt*self.scaleMinuser) * self.change_multiplier)
				if preview > 0:
					particle["scale"] = preview
				particle["image"] = scale_image(particle["original"],particle["scale"])

			surface.blit(particle["image"],particle["pos"])

		for particle in toRemove:
			self.particles.remove(particle)

		if self.destroy_after_time or self.hide_after_time:
			if current-self.lastHide >= self.destroy_or_hide_cooldown:
				if self.destroy_after_time:
					self.kill()
				elif self.hide_after_time:
					self.active = False
					self.empty_particles()
				self.lastHide = current

		self.lastTime = current

	def kill(self)->None:
		"""
		Delete itself.
		"""
		del self

# TRAILS
class Trail():
	"""
	A customizable trail generator to attach to a sprite.
	"""
	def __init__(self,sprite:sprites.Sprite,offset:Union[Tuple[int,int],List[int],pygame.math.Vector2] =(0,0),color:Union[str,Tuple[int,int,int]]="white",trail_thicness:int=5,disappear_speed:float=0.1,active:bool=True):
		self.sprite = sprite

		self.offset = pygame.math.Vector2(offset)
		self.origin_point = self.offset+self.sprite.rect.center
		self.color = color
		self.trail_thicness = trail_thicness
		self.disappear_speed = disappear_speed
		self.previus = pygame.math.Vector2(self.origin_point)
		self.active = active

		self.lines = []

	def copy(self):
		new = Trail(self.sprite,self.offset,self.color,self.trail_thicness,self.disappear_speed,self.active)
		new.lines = self.lines
		return new

	def kill(self)->None:
		"""
		Delete itself.
		"""
		del self

	def clear_trail(self)->None:
		"""
		Clear the trail list.
		"""
		self.lines.clear()

	def update_position(self)->None:
		"""
		Change th origin point to the sprite rect center offsetted.
		"""
		self.origin_point = self.offset+self.sprite.rect.center

	def generate(self)->None:
		"""
		Add one trail line to the list.
		"""
		if self.active:
			if self.previus != self.origin_point:
				self.lines.append({"color":self.color,"size":self.trail_thicness,"pos1":self.origin_point.xy,"pos2":self.previus.xy})

			self.previus = self.origin_point

	def draw(self,surface:pygame.Surface,dt:float=1.0)->None:
		"""
		Draw the trail lines.
		"""
		if not surface:
			surface = pygame.display.get_surface()

		toRemove = []

		for par in self.lines:
			par["size"] -= self.disappear_speed*dt
			if round(par["size"]) <= 0:
				toRemove.append(par)
				continue
			else:
				pygame.draw.line(surface, par["color"], par["pos1"], par["pos2"],round(par["size"]) )


		for p in toRemove:
			self.lines.remove(p)

#UI
class Text():
	"""
	Easier way to draw some text. When some value changes, the image is resetted. 
	"""
	def __init__(self,center_pos:Tuple[int,int]=(0,0),topleft_pos:Tuple[int,int]=None,font:pygame.font.Font=None,text:str="Text",color:Union[str,Tuple[int,int,int]]="black",antialiasing:bool=True,bg_color:Union[str,Tuple[int,int,int]]=None,stick_topleft:bool=False):
		if font:
			self._font = font
		else:
			self._font = pygame.font.Font(None,20)
		self._text = text
		self._color = color
		self._antialiasing= antialiasing
		self._bg_color = bg_color
		self.center_pos = center_pos
		self.topleft_pos = topleft_pos
		self.button = None
		self.stick_topleft = stick_topleft
		self.image = self._font.render(self._text,self._antialiasing,self._color,self._bg_color) 
		if self.topleft_pos:
			self.rect = self.image.get_rect(topleft=self.topleft_pos)
		else:
			self.rect = self.image.get_rect(center=self.center_pos)

	def draw(self,surface:pygame.Surface=None,draw_outline:bool=False,outline_inflate:Tuple[int,int]=(7,7),outline_color:Union[str,Tuple[int,int,int]]="copy_text",outline_width:int=2,outline_border_radius:int=0):
		"""
		Draw the text.
		"""
		if not surface:
			surface = pygame.display.get_surface()

		surface.blit(self.image,self.rect)
		if draw_outline:
			if outline_color == "copy_text":
				outline_color = self._color
			pygame.draw.rect(surface, outline_color, self.rect.inflate(outline_inflate),outline_width,outline_border_radius)

	@property
	def font(self):
		return self._font

	@font.setter
	def font(self,f):
		self._font = f
		self.refresh_image()

	@property
	def text(self):
		return self._text

	@text.setter
	def text(self,t):
		self._text = str(t)
		self.refresh_image()

	@property
	def color(self):
		return self._color

	@color.setter
	def color(self,tc):
		self._color = tc
		self.refresh_image()
	
	@property
	def antialiasing(self):
		return self._antialiasing

	@antialiasing.setter
	def antialiasing(self,a):
		self._antialiasing = a 
		self.refresh_image()

	@property
	def bg_color(self):
		return self._bg_color

	@bg_color.setter
	def bg_color(self,bc):
		self._bg_color = bc
		self.refresh_image()

	def refresh_image(self)->None:
		"""
		Reset the text image.
		"""
		self.image = self._font.render(self._text,self._antialiasing,self._color,self._bg_color) 
		if self.stick_topleft:
			self.rect = self.image.get_rect(topleft=self.rect.topleft)
		else:
			self.rect = self.image.get_rect(center=self.rect.center)
		if self.button:
			self.button.refresh_hitbox()

class InputBox():
	"""
	An easy way to implement an imput box, with events binding.
	"""
	def __init__(self, box_rect:pygame.Rect, font:pygame.font.Font,start_text:str='Type Here',max_char:int = 25,color_active:Union[str,Tuple[int,int,int]]="white",color_inactive:Union[str,Tuple[int,int,int]]=(200,200,200),antialiasing:bool=True,start_focused=False,bar_width:int=2):
		self.rect = box_rect
		self.color_active = color_active
		self.color_inactive = color_inactive
		self.color = self.color_inactive
		self.start_text = start_text
		self.text = start_text
		self.font = font
		self.antialiasing = antialiasing
		self.txt_surface = self.font.render(self.text, self.antialiasing, self.color)
		self.active = False
		self.max = max_char
		self.on_text_change = None
		self.on_text_increase = None
		self.on_text_decrease = None
		self.on_return_pressed = None
		test = self.font.render("MAX",True,"white")
		self.bar_rect = pygame.Rect(self.rect.left, self.rect.left, bar_width, test.get_height()+bar_width*2)
		del test
		self.bar_visible = True
		self.start_bar = pygame.time.get_ticks()
		self.bar_cooldown = 420
		self.bar_width = bar_width
		if start_focused:
			self.focus()

	def focus(self):
		"""
		Focus the input box.
		"""
		self.active = True
		self.color = self.color_active
		self.refresh_surface()

	def unfocus(self):
		"""
		Unfocus the input box.
		"""
		self.active = False
		self.color = self.color_inactive
		self.refresh_surface()

	def bind_events(self,on_text_change=None,on_text_increase=None,on_text_decrease=None,on_return_pressed=None):
		"""
		Bind the events functions.
		"""
		self.on_text_change = on_text_change
		self.on_text_increase = on_text_increase
		self.on_text_decrease = on_text_decrease
		self.on_return_pressed = on_return_pressed

	def handle_event(self, event:pygame.event.Event):
		"""
		Process the events. Put this under the event loop.
		"""
		if event.type == pygame.MOUSEBUTTONDOWN:
			# If the user clicked on the input_box rect.
			if self.rect.collidepoint(event.pos):
				# Toggle the active variable.
				self.active = not self.active
			else:
				self.active = False
			# Change the current color of the input box.
			self.color = self.color_active if self.active else self.color_inactive
			self.refresh_surface()
		if event.type == pygame.KEYDOWN:
			if self.active:
				if event.key == pygame.K_BACKSPACE:
					before = self.text
					self.text = self.text[:-1]
					if len(self.text) != len(before):
						if self.on_text_decrease:
							self.on_text_decrease()
						if self.on_text_change:
							self.on_text_change()
					if not self.text.strip():
						self.set_text(self.start_text)
					if before.strip() == self.start_text:
						self.set_text("")
				elif event.key == pygame.K_RETURN:
					if self.on_return_pressed:
						self.on_return_pressed()
				else:
					if self.text.strip() == self.start_text:
						self.set_text("")
					if not len(self.text) > self.max:
						self.text += event.unicode
						if self.on_text_increase:
							self.on_text_increase()
						if self.on_text_change:
							self.on_text_change()
				# Re-render the text.
				self.refresh_surface()

	def refresh_surface(self):
		"""
		Set the surface to the new text.
		"""
		self.txt_surface = self.font.render(self.text, self.antialiasing, self.color)

	def draw(self,surface, text_offset:Tuple[int,int]=(0,0),draw_rect:bool=True,rect_color:Union[str,Tuple[int,int,int]]="copy_text",width:int=5,draw_bar = True):
		"""
		Draw the text and the rect (optional).
		"""
		# Blit the text.
		surface.blit(self.txt_surface, (self.rect.x+text_offset[0],self.rect.y+text_offset[1]))
		# Blit the rect.
		if draw_rect:
			if rect_color == "copy_text":
				rect_color = self.color
			pygame.draw.rect(surface, rect_color, self.rect, width)
		if draw_bar and self.active:
			if pygame.time.get_ticks()-self.start_bar >= self.bar_cooldown:
				self.start_bar = pygame.time.get_ticks()
				self.bar_visible = not self.bar_visible
			if self.bar_visible:
				self.bar_rect.center = (self.rect.left+self.txt_surface.get_width()+text_offset[0]+2,self.rect.top+text_offset[1]+self.bar_rect.h/2-self.bar_width)
				pygame.draw.rect(surface, self.color, self.bar_rect)

	def get_text(self)->str:
		"""
		Return the text.
		"""
		return self.text

	def set_text(self,text:str,ignore_max_char:bool=False):
		if len(text) <= self.max or ignore_max_char:
			self.text = text
		self.refresh_surface()

class ImageButton():
	"""
	A button based on an image.
	"""
	def __init__(self,surface,center_pos:Tuple[int,int]=(0,0),topleft_pos:Tuple[int,int]=None,hitbox_inflate:Tuple[int,int]=(0,0),on_click_func=None,click_button:int=0):

		self._image = surface
		self.clicked = False
		self.hitbox_inflate = hitbox_inflate
		self.rect = self._image.get_rect(center = center_pos)
		if topleft_pos:
			self.rect.topleft = topleft_pos
		self.hitbox = self.rect.inflate(self.hitbox_inflate)
		self.on_click_function = on_click_func
		self.on_click_button = click_button

	def refresh_rect(self):
		"""
		Resize the rect to the image size.
		"""
		self.rect = self._image.get_rect(center = self.rect.center)
		self.hitbox = self.rect.inflate(self.hitbox_inflate)

	@property
	def image(self):
		return self._image

	@image.setter
	def image(self,value):
		self._image = value
		self.refresh_hitbox()

	def draw(self, surface:pygame.Surface=None):
		"""
		Draw the button and the image and text (both optional)
		"""
		if not surface:
			surface = get_window_surface()
		surface.blit(self.image, self.rect)

	def check_click(self,allow_multi_click:bool=False)->bool:
		"""
		Check if the button is got clicked or is being clicked. If a function is passed in the init, it will be called.
		"""
		action = False

		self.hitbox.center = self.rect.center

		pos = pygame.mouse.get_pos()
		mouse = pygame.mouse.get_pressed()

		if self.hitbox.collidepoint(pos):
			if mouse[self.on_click_button]:
				if self.clicked == False or allow_multi_click == True:
					action = True
					self.clicked = True
					if self.on_click_function:
						self.on_click_function()

			if not mouse[self.on_click_button]:
				self.clicked = False

		return action

class TextButton():
	"""
	A button based on a text object.
	"""
	def __init__(self,text:Text,hitbox_inflate:Tuple[int,int]=(0,0),on_click_func=None,click_button:int=0):
		self.clicked = False

		self.text = text
		self.hitbox_inflate = hitbox_inflate
		self.hitbox = self.text.rect.inflate(self.hitbox_inflate)
		self.text.button = self
		self.on_click_function = on_click_func
		self.on_click_button = click_button

	def refresh_hitbox(self):
		"""
		Refresh the hitbox on the rect size.
		"""
		self.hitbox = self.text.rect.inflate(self.hitbox_inflate)

	def draw(self, surface:pygame.Surface=None,draw_outline:bool=False,outline_inflate:Tuple[int,int]=(5,5),outline_color:Union[str,Tuple[int,int,int]]="copy_text",outline_width:int=2,outline_border_radius:int=0):
		"""
		Draw the button and the image and text (both optional)
		"""
		if not surface:
			surface = get_window_surface()
		self.text.draw(surface,draw_outline,outline_inflate,outline_color,outline_width,outline_border_radius)

	def check_click(self,allow_multi_click:bool=False)->bool:
		"""
		Check if the button is got clicked or is being clicked. If a function is passed in the init, it will be called.
		"""
		action = False

		self.hitbox.center = self.text.rect.center

		pos = pygame.mouse.get_pos()
		mouse = pygame.mouse.get_pressed()

		if self.hitbox.collidepoint(pos):
			if mouse[self.on_click_button]:
				if self.clicked == False or allow_multi_click == True:
					action = True
					self.clicked = True
					if self.on_click_function:
						self.on_click_function()

			if not mouse[self.on_click_button]:
				self.clicked = False

		return action

# TIMERS
class CooldownTimer():
	"""
	A timer, based on a cooldown. Not recommended.
	"""
	def __init__(self,cooldown:int):

		self.cooldown = cooldown
		self.timer = cooldown
		self.finished = False

	def update(self,dt:float=1.0)->None:
		"""
		Update the timer.
		"""
		# decrease timer value
		self.timer -= 1*dt
		if self.timer <= 0:
		    # set the status finished to true
		    self.finished = True
		    self.timer = 0

	def reset(self)->None:
		"""
		Reset the timer.
		"""
		# reset the variables
		self.timer = self.cooldown
		self.finished = False

class Timer:
	"""
	A timer based on game ticks.
	"""
	def __init__(self,duration:int,func = None,start_active=False):
		self.duration = duration 
		self.func = func
		self.start_time = 0
		self.active = False
		if start_active:
			self.activate()

	def activate(self)->None:
		"""
		Activate the timer.
		"""
		self.active = True
		self.start_time = pygame.time.get_ticks()

	def deactivate(self)->None:
		"""
		Deactivate the timer.
		"""
		self.active = False
		self.start_time = 0

	def update(self,activate_on_end=False)->None:
		"""
		Update the timer.
		"""
		current_time = pygame.time.get_ticks()
		if current_time - self.start_time> self.duration:
			if self.func and self.start_time != 0:
				self.func()
			self.deactivate()
			if activate_on_end:
				self.activate()

