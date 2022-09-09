import pygame
from os import walk
from typing import Tuple,Union,Dict,List
from random import randint,choice
# pygame shortcuts
from pygame.transform import flip,rotate,rotozoom
from pygame.color import Color
from pygame.display import get_window_size,get_surface,set_caption,set_icon,set_mode
from pygame import Surface
from pygame.draw import rect as draw_rect
from pygame.draw import circle as draw_circle
from pygame.draw import line as draw_line
from pygame.draw import lines as draw_lines
from pygame.draw import polygon as draw_polygon

"""
This module contains useful functions to manage surfaces, imports, window, pixels, colors and more in pygame.
"""

# TRANSFORM
def load_image(path:str,convert_alpha:bool=False)->pygame.Surface:
	"""Load an image and return a surface."""
	return pygame.image.load(path).convert() if not convert_alpha else pygame.image.load(path).convert_alpha()

def scale_image(image:pygame.Surface,scale:float=None,sizes:Tuple[int,int]=None,smooth:bool=False)->pygame.Surface:
	"""Scale an image by scale or sizes."""
	if scale:
		if not smooth:
			return pygame.transform.scale(image,(int(image.get_width()*scale),int(image.get_height()*scale)))
		else:
			return pygame.transform.smoothscale(image,(int(image.get_width()*scale),int(image.get_height()*scale)))
	elif sizes:
		if not smooth:
			return pygame.transform.scale(image,(sizes[0],sizes[1]))
		else:
			return pygame.transform.smoothscale(image,(sizes[0],sizes[1]))

# IMPORT
def import_images_folder(folder_path:str,convert_alpha:bool=False,scale:float=None,scale_sizes:Tuple[int,int]=None)->list:
    """Return a list of images from a folder (useful for animations)."""
    surface_list = []

    for _,__,image_files in walk(folder_path):
        for image in image_files:
            full_path = folder_path + '/' + image
            image_surf = load_image(full_path,convert_alpha)
            if scale or scale_sizes:
                image_surf = scale_image(image_surf,scale,scale_sizes[0],scale_sizes[1])
            surface_list.append(image_surf)

    return surface_list

def import_images_folder_dict(folder_path:str,convert_alpha:bool=False,scale:float=None,scale_sizes:Tuple[int,int]=None)->dict:
    """Return a dict of images from a folder (useful for animations)."""
    surface_list = []

    for _,__,image_files in walk(folder_path):
        for image in image_files:
            full_path = folder_path + '/' + image
            image_surf = load_image(full_path,convert_alpha)
            if scale or scale_sizes:
                image_surf = scale_image(image_surf,scale,scale_sizes[0],scale_sizes[1])
            surface_list[image.split(".")[0]] = image_surf

    return surface_list

# PIXEL CALCULATOR
def width_calculator(your_window_width:int,desired_result:Union[int,float],rounded:bool=False)->Union[int,float]:
	"""
	Return a pixel number caluculated with a formula, that will have a different output based on the current window sizes.

	Very useful to make your objects different sizes, based on the screen resolution.

	if the current sizes are the same as the one passed, it will actually return the desired result.

	This function takes in considertion only the width. Otherwise there are the functions 'height_calculator' and 'medium_calculator'.
	"""
	divider = your_window_width/desired_result
	pixels = pygame.display.get_window_size()[0]/divider
	if rounded:
		return round(pixels)
	else:
		return pixels

def height_calculator(your_window_height:int,desired_result:Union[int,float],rounded:bool=False)->Union[int,float]:
	"""
	Return a pixel number caluculated with a formula, that will have a different output based on the current window sizes.

	Very useful to make your objects different sizes, based on the screen resolution.

	if the current sizes are the same as the one passed, it will actually return the desired result.

	This function takes in considertion only the height. Otherwise there are the functions 'width_calculator' and 'medium_calculator'.
	"""
	divider = your_window_height/desired_result
	pixels = pygame.display.get_window_size()[1]/divider
	if rounded:
		return round(pixels)
	else:
		return pixels

def medium_calculator(your_window_width:int,your_window_height:int,desired_result:Union[int,float],rounded:bool=False)->Union[int,float]:
	"""
	Return a pixel number caluculated with a formula, that will have a different output based on the current window sizes.

	Very useful to make your objects different sizes, based on the screen resolution.

	if the current sizes are the same as the one passed, it will actually return the desired result.

	This function makes the medium of the width and height. Otherwise there are the functions 'height_calculator' and 'width_calculator'.
	"""
	first = width_calculator(your_window_width,desired_result,rounded)
	second = height_calculator(your_window_height,desired_result,rounded)
	pixels = (first+second)/2
	if rounded:
		return round(pixels)
	else:
		return pixels

# WINDOW
def update_window(clock:pygame.time.Clock,desired_fps:int,window_surface:pygame.Surface=None,fill_color:Union[str,Tuple[int,int,int]]="black")->None:
	"""Update the window and fill it after using the clock and pygame."""
	clock.tick(desired_fps)
	pygame.display.flip()
	if window_surface:
		window_surface.fill(fill_color)

def resize_window(current_surface,resized_window_sizes,resizable=True,flag=0):
    """
    Resize the window surface and blit the old one on it. Useful after the VIDEORESIZE event.
    """
    if resizable:
    	flag = pygame.RESIZABLE
    new = pygame.display.set_mode(resized_window_sizes,flag)
    new.blit(current_surface, (0,0))
    return new

def set_fullscreen()->pygame.Surface:
	"""
	Set the window to fullscreen mode.
	"""
	sizes = pygame.display.get_window_size()
	return pygame.display.set_mode(sizes,pygame.FULLSCREEN)

def set_windowed()->pygame.Surface:
	"""
	Exit the fullscreen mode.
	"""
	sizes = pygame.display.get_window_size()
	return pygame.display.set_mode(sizes)

def set_resizable()->pygame.Surface:
	"""
	Set the window to a resizable one.
	"""
	sizes = pygame.display.get_window_size()
	return pygame.display.set_mode(sizes,pygame.RESIZABLE)

def set_noframe()->pygame.Surface:
	"""
	Set the window to no frame mode.
	"""
	sizes = pygame.display.get_window_size()
	return pygame.display.set_mode(sizes,pygame.NOFRAME)

# OTHER
def resize_rect(original_rect:pygame.Rect,surface:pygame.Surface)->pygame.Rect:
	"""Return a rect of the same sizes of the image passed but at the same position of the original."""
	return surface.get_rect(center=original_rect.center)

def empty_image(sizes:Tuple[int,int]=(1,1),color:Union[str,Tuple[int,int,int]]=None)->pygame.Surface:
	"""Return a basic surface."""
	image = pygame.Surface(sizes)
	if color:
		image.fill(color)

	return image

# COLOR
def random_rgb_color()->Tuple[int,int,int]:
	"""
	Return a color with random rgb values.
	"""
	return (randint(0,255),randint(0,255),randint(0,255))

COLORS = {
"maroon":(128,0,0),
"dark red":(139,0,0),
"brown":(165,42,42),
"firebrick":(178,34,34),
"crimson":(220,20,60),
"red":(255,0,0),
"tomato":(255,99,71),
"coral":(255,127,80),
"indian red":(205,92,92),
"light coral":(240,128,128),
"dark salmon":(233,150,122),
"salmon":(250,128,114),
"light salmon":(255,160,122),
"orange red":(255,69,0),
"dark orange":(255,140,0),
"orange":(255,165,0),
"gold":(255,215,0),
"dark golden rod":(184,134,11),
"golden rod":(218,165,32),
"pale golden rod":(238,232,170),
"dark khaki":(189,183,107),
"khaki":(240,230,140),
"olive":(128,128,0),
"yellow":(255,255,0),
"yellow green":(154,205,50),
"dark olive green":(85,107,47),
"olive drab":(107,142,35),
"lawn green":(124,252,0),
"chartreuse":(127,255,0),
"green yellow":(173,255,47),
"dark green":(0,100,0),
"green":(0,128,0),
"forest green":(34,139,34),
"lime":(0,255,0),
"lime green":(50,205,50),
"light green":(144,238,144),
"pale green":(152,251,152),
"dark sea green":(143,188,143),
"medium spring green":(0,250,154),
"spring green":(0,255,127),
"sea green":(46,139,87),
"medium aqua marine":(102,205,170),
"medium sea green":(60,179,113),
"light sea green":(32,178,170),
"dark slate gray":(47,79,79),
"teal":(0,128,128),
"dark cyan":(0,139,139),
"aqua":(0,255,255),
"cyan":(0,255,255),
"light cyan":(224,255,255),
"dark turquoise":(0,206,209),
"turquoise":(64,224,208),
"medium turquoise":(72,209,204),
"pale turquoise":(175,238,238),
"aqua marine":(127,255,212),
"powder blue":(176,224,230),
"cadet blue":(95,158,160),
"steel blue":(70,130,180),
"corn flower blue":(100,149,237),
"deep sky blue":(0,191,255),
"dodger blue":(30,144,255),
"light blue":(173,216,230),
"sky blue":(135,206,235),
"light sky blue":(135,206,250),
"midnight blue":(25,25,112),
"navy":(0,0,128),
"dark blue":(0,0,139),
"medium blue":(0,0,205),
"blue":(0,0,255),
"royal blue":(65,105,225),
"blue violet":(138,43,226),
"indigo":(75,0,130),
"dark slate blue":(72,61,139),
"slate blue":(106,90,205),
"medium slate blue":(123,104,238),
"medium purple":(147,112,219),
"dark magenta":(139,0,139),
"dark violet":(148,0,211),
"dark orchid":(153,50,204),
"medium orchid":(186,85,211),
"purple":(128,0,128),
"thistle":(216,191,216),
"plum":(221,160,221),
"violet":(238,130,238),
"magenta / fuchsia":(255,0,255),
"orchid":(218,112,214),
"medium violet red":(199,21,133),
"pale violet red":(219,112,147),
"deep pink":(255,20,147),
"hot pink":(255,105,180),
"light pink":(255,182,193),
"pink":(255,192,203),
"antique white":(250,235,215),
"beige":(245,245,220),
"bisque":(255,228,196),
"blanched almond":(255,235,205),
"wheat":(245,222,179),
"corn silk":(255,248,220),
"lemon chiffon":(255,250,205),
"light golden rod yellow":(250,250,210),
"light yellow":(255,255,224),
"saddle brown":(139,69,19),
"sienna":(160,82,45),
"chocolate":(210,105,30),
"peru":(205,133,63),
"sandy brown":(244,164,96),
"burly wood":(222,184,135),
"tan":(210,180,140),
"rosy brown":(188,143,143),
"moccasin":(255,228,181),
"navajo white":(255,222,173),
"peach puff":(255,218,185),
"misty rose":(255,228,225),
"lavender blush":(255,240,245),
"linen":(250,240,230),
"old lace":(253,245,230),
"papaya whip":(255,239,213),
"sea shell":(255,245,238),
"mint cream":(245,255,250),
"slate gray":(112,128,144),
"light slate gray":(119,136,153),
"light steel blue":(176,196,222),
"lavender":(230,230,250),
"floral white":(255,250,240),
"alice blue":(240,248,255),
"ghost white":(248,248,255),
"honeydew":(240,255,240),
"ivory":(255,255,240),
"azure":(240,255,255),
"snow":(255,250,250),
"black":(0,0,0),
"dim gray":(105,105,105),
"dim grey":(105,105,105),
"grey":(128,128,128),
"gray":(128,128,128),
"dark gray":(169,169,169),
"dark grey":(169,169,169),
"silver":(192,192,192),
"light gray":(211,211,211),
"light grey":(211,211,211),
"gainsboro":(220,220,220),
"white smoke":(245,245,245),
"white":(255,255,255),
}

COLORS_HEX = {
	"maroon":"#800000",
"dark red":"#8B0000",
"brown":"#A52A2A",
"firebrick":"#B22222",
"crimson":"#DC143C",
"red":"#FF0000",
"tomato":"#FF6347",
"coral":"#FF7F50",
"indian red":"#CD5C5C",
"light coral":"#F08080",
"dark salmon":"#E9967A",
"salmon":"#FA8072",
"light salmon":"#FFA07A",
"orange red":"#FF4500",
"dark orange":"#FF8C00",
"orange":"#FFA500",
"gold":"#FFD700",
"dark golden rod":"#B8860B",
"golden rod":"#DAA520",
"pale golden rod":"#EEE8AA",
"dark khaki":"#BDB76B",
"khaki":"#F0E68C",
"olive":"#808000",
"yellow":"#FFFF00",
"yellow green":"#9ACD32",
"dark olive green":"#556B2F",
"olive drab":"#6B8E23",
"lawn green":"#7CFC00",
"chartreuse":"#7FFF00",
"green yellow":"#ADFF2F",
"dark green":"#006400",
"green":"#008000",
"forest green":"#228B22",
"lime":"#00FF00",
"lime green":"#32CD32",
"light green":"#90EE90",
"pale green":"#98FB98",
"dark sea green":"#8FBC8F",
"medium spring green":"#00FA9A",
"spring green":"#00FF7F",
"sea green":"#2E8B57",
"medium aqua marine":"#66CDAA",
"medium sea green":"#3CB371",
"light sea green":"#20B2AA",
"dark slate gray":"#2F4F4F",
"teal":"#008080",
"dark cyan":"#008B8B",
"aqua":"#00FFFF",
"cyan":"#00FFFF",
"light cyan":"#E0FFFF",
"dark turquoise":"#00CED1",
"turquoise":"#40E0D0",
"medium turquoise":"#48D1CC",
"pale turquoise":"#AFEEEE",
"aqua marine":"#7FFFD4",
"powder blue":"#B0E0E6",
"cadet blue":"#5F9EA0",
"steel blue":"#4682B4",
"corn flower blue":"#6495ED",
"deep sky blue":"#00BFFF",
"dodger blue":"#1E90FF",
"light blue":"#ADD8E6",
"sky blue":"#87CEEB",
"light sky blue":"#87CEFA",
"midnight blue":"#191970",
"navy":"#000080",
"dark blue":"#00008B",
"medium blue":"#0000CD",
"blue":"#0000FF",
"royal blue":"#4169E1",
"blue violet":"#8A2BE2",
"indigo":"#4B0082",
"dark slate blue":"#483D8B",
"slate blue":"#6A5ACD",
"medium slate blue":"#7B68EE",
"medium purple":"#9370DB",
"dark magenta":"#8B008B",
"dark violet":"#9400D3",
"dark orchid":"#9932CC",
"medium orchid":"#BA55D3",
"purple":"#800080",
"thistle":"#D8BFD8",
"plum":"#DDA0DD",
"violet":"#EE82EE",
"magenta / fuchsia":"#FF00FF",
"orchid":"#DA70D6",
"medium violet red":"#C71585",
"pale violet red":"#DB7093",
"deep pink":"#FF1493",
"hot pink":"#FF69B4",
"light pink":"#FFB6C1",
"pink":"#FFC0CB",
"antique white":"#FAEBD7",
"beige":"#F5F5DC",
"bisque":"#FFE4C4",
"blanched almond":"#FFEBCD",
"wheat":"#F5DEB3",
"corn silk":"#FFF8DC",
"lemon chiffon":"#FFFACD",
"light golden rod yellow":"#FAFAD2",
"light yellow":"#FFFFE0",
"saddle brown":"#8B4513",
"sienna":"#A0522D",
"chocolate":"#D2691E",
"peru":"#CD853F",
"sandy brown":"#F4A460",
"burly wood":"#DEB887",
"tan":"#D2B48C",
"rosy brown":"#BC8F8F",
"moccasin":"#FFE4B5",
"navajo white":"#FFDEAD",
"peach puff":"#FFDAB9",
"misty rose":"#FFE4E1",
"lavender blush":"#FFF0F5",
"linen":"#FAF0E6",
"old lace":"#FDF5E6",
"papaya whip":"#FFEFD5",
"sea shell":"#FFF5EE",
"mint cream":"#F5FFFA",
"slate gray":"#708090",
"light slate gray":"#778899",
"light steel blue":"#B0C4DE",
"lavender":"#E6E6FA",
"floral white":"#FFFAF0",
"alice blue":"#F0F8FF",
"ghost white":"#F8F8FF",
"honeydew":"#F0FFF0",
"ivory":"#FFFFF0",
"azure":"#F0FFFF",
"snow":"#FFFAFA",
"black":"#000000",
"dim gray":"#696969",
"dim grey":"#696969",
"gray":"#808080",
"grey":"#808080",
"dark gray":"#A9A9A9",
"dark grey":"#A9A9A9",
"silver":"#C0C0C0",
"light gray":"#D3D3D3",
"light grey":"#D3D3D3",
"gainsboro":"#DCDCDC",
"white smoke":"#F5F5F5",
"white":"#FFFFFF",
}

def colors()->Dict[str,Tuple[int,int,int]]:
	"""
	Return the colors dict.
	"""
	return COLORS

def hex_colors()->Dict[str,str]:
	"""Return the hex color dict."""
	return COLORS_HEX

def colors_names()->List[str]:
	"""
	Return a list with all the color names.
	"""
	return COLORS.keys()

def color_values()->List[Tuple[int,int,int]]:
	"""
	Return a list with all the color rgbs.
	"""
	return COLORS.values()

def hex_color_values()->List[str]:
	"""
	Return a list with all the color hexs.
	"""
	return COLORS_HEX.values()

def random_color_name()->str:
	"""
	Choose a random color name.
	"""
	return choice(COLORS.keys())

def random_color()->Tuple[int,int,int]:
	"""
	Chooses a random color.
	"""
	return choice(COLORS.values())

def random_hex_color()->str:
	"""
	Chooses a random hex color from the dict.
	"""
	return choice(COLORS_HEX.values())

def get_color(name:str)->Tuple[int,int,int]:
	"""
	Get the color value from the name.
	"""
	return COLORS[name]

def get_hex_color(name:str)->str:
	"""
	Get the hex color value from the name.
	"""
	return COLORS_HEX[name]

def color_exists(name:str)->bool:
	"""
	Check if a color name is available.
	"""
	return name in COLORS.keys()
