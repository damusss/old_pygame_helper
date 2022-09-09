import pygame
from pygame_helper.graphics import *
from typing import Union, Tuple,List, Dict,Any,Type
# pygame shortcuts
from pygame.sprite import GroupSingle,spritecollide,spritecollideany

"""
This module contains some helpful sprites based on the pygame one.

Remember to add a super().__init__({arguments}) under the init methods if you want to inherit from them.
"""

# SPRITES
class Sprite(pygame.sprite.Sprite):
    """
    A sprite class with the addition of useful methods and attributes.
    """
    def __init__(self,image:pygame.Surface=None,topleft_pos:Tuple[int,int]=None,groups:Union[pygame.sprite.Group,List[pygame.sprite.Group]]=[],direction:Tuple[int,int]=(0,0),speed:Tuple[float,float]=(0,0),z_index:int=0,parent=None,parent_offset:Tuple[int,int]=(0,0)):
        super().__init__(groups)

        self.z_index = z_index

        self.direction = pygame.math.Vector2(direction)
        self.speed = pygame.math.Vector2(speed)
        self.position = pygame.math.Vector2()

        if image:
            self.image = image
            if topleft_pos:
                self.rect = self.image.get_rect(topleft=topleft_pos)
                self.set_hitbox()
                self.refresh_position()
            self.original_image = self.image
                
        self.parent = parent
        self.parent_offset = pygame.math.Vector2(parent_offset)

    def set_original_image(self):
        self.original_image = self.image

    def handle_event(self,event):
        """
        Override this method.
        """
        pass

    def copy(self):
        """
        Return an exact copy of the sprite (note: only built in attributes are copied).
        """
        new = Sprite(groups=self.groups(),z_index=self.z_index,direction=self.direction.xy,speed=self.speed.xy,position= self.position.xy)
        if hasattr(self,"rect"):
            new.rect = self.rect.copy()
        if hasattr(self, "hitbox"):
            new.hitbox = self.hitbox.copy()
        if hasattr(self,"image"):
            new.image = self.image
        return new

    def to_json(self,ignore_attributes:list=[])->dict:
        """
        Return a dictionary of the sprite that can be saved in a file, to be reloaded.
        """
        json = {}
        if not "z_index" in ignore_attributes:
            json["z_index"] = self.z_index
        if not "direction" in ignore_attributes:
            json["direction"] = {"x":self.direction.x,"y":self.direction.y}
        if not "speed" in ignore_attributes:
            json["speed"] = {"x":self.speed.x,"y":self.speed.y}
        if not "position" in ignore_attributes:
            json["position"] = {"x":self.position.x,"y":self.position.y}

        if hasattr(self, "image") and not "image" in ignore_attributes:
            json["image"] = {"width":self.image.get_width(),"height":self.image.get_height()}
        if hasattr(self, "rect") and not "rect" in ignore_attributes:
            json["rect"] = {"x":self.rect.x,"y":self.rect.y,"w":self.rect.w,"h":self.rect.h,"centerx":self.rect.centerx,"centery":self.rect.centery}
        if hasattr(self, "hitbox") and not "hitbox" in ignore_attributes:
            json["hitbox"] = {"x":self.hitbox.x,"y":self.hitbox.y,"w":self.hitbox.w,"h":self.hitbox.h,"centerx":self.hitbox.centerx,"centery":self.hitbox.centery}
        
        if not "groups" in ignore_attributes:
            json["groups"] = {"len":len(self.groups()),"types":[g.__class__.__name__ for g in self.groups()]}
        return json

    def from_json(self,json:dict,*other_args):
        """
        Return a new sprite loaded from a dictionary.
        """
        new = self.__class__(*other_args)
        keys = json.keys()
        if "z_index" in keys:
            new.z_index = json["z_index"]

        if "direction" in keys:
            new.direction.xy = (json["direction"]["x"],json["direction"]["y"])
        if "speed" in keys:
            new.speed.xy = (json["speed"]["x"],json["speed"]["y"])
        if "position" in keys:
            new.position.xy = (json["position"]["x"],json["position"]["y"])

        if "image" in keys:
            new.image = pygame.Surface((json["image"]["width"],json["image"]["height"]))
        if "rect" in keys:
            if "image" in keys:
                new.rect = new.image.get_rect(center=(json["rect"]["centerx"],json["rect"]["centery"]))
            else:
                new.rect = pygame.Rect(json["rect"]["x"], json["rect"]["y"], json["rect"]["w"], json["rect"]["h"])
        if "hitbox" in keys and "rect"in keys:
            new.hitbox = pygame.Rect(json["hitbox"]["x"], json["hitbox"]["y"], json["hitbox"]["w"], json["hitbox"]["h"])

        return new

    def set_hitbox(self,hitbox_inflate:Union[Tuple[int,int],List[int],pygame.math.Vector2]=(0,0))->pygame.Rect:
        """
        Setup the hitbox !after rect creation!
        """
        self.hitbox = self.rect.inflate(hitbox_inflate[0], hitbox_inflate[1])
        return self.hitbox

    def draw(self,surface:pygame.Surface)->None:
        """
        Draw the image on the screen.
        """
        if not surface:
            surface = pygame.displat.get_surface()
        surface.blit(self.image,self.rect)

    def draw_rect(self,surface,color="white",width:int=2,border_radius:int=0):
        """
        Draw the sprite rect.
        """
        if not surface:
            surface = pygame.displat.get_surface()
        pygame.draw.rect(surface, color, self.rect,width,border_radius)

    def is_on_screen(self,dokill:bool=False,surface:pygame.Surface=None)->bool:
        """
        Check if the sprite is inside the window
        """
        if not surface:
            surface = pygame.display.get_surface()
        if self.rect.right > 0 and self.rect.left < surface.get_width() and self.rect.bottom > 0 and self.rect.top < surface.get_height():
            return True
        return False

    def check_collision(self,sprite):
        """
        Check the collision with another sprite.
        """
        return self.rect.colliderect(sprite.rect)

    def mouse_collision(self):
        """
        Check if the mouse is hovering the sprite.
        """
        pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(pos[0], pos[1] )

    def refresh_position(self):
        """
        Set the position to the center of the rectangle (useful after changing the rectangle position manually).
        """
        self.position.xy = self.rect.center

    def update_position(self,direction="horizontal",dt=1):
        """
        Update the position and rectangle position of the sprite using the speed and direction. 

        You have to specify if you want to update the horizontal or vertical direction, Otherwise use 'update_positions'.
        """
        if direction == "horizontal" or direction == "h":
            self.position.x += self.direction.x*self.speed.x*dt
            self.rect.centerx = round(self.position.x)
            self.hitbox.centerx = self.rect.centerx
        elif direction =="vertical" or direction == "v":
            self.position.y += self.direction.y*self.speed.y*dt
            self.rect.centery = round(self.position.y)
            self.hitbox.centery = self.rect.centery

    def update_positions(self,dt=1):
        """
        Update the position of both the directions. Check 'update_position' for more.
        """
        self.update_position("h",dt)
        self.update_position("v",dt)

    def normalize_direction(self):
        """
        Normalize the direction of the sprite.
        """
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

    def collision(self,collision_group,direction="horizontal"):
        """
        Check the collisions between itself and a list of sprites. Both needs to have an hitbox.

        After collision detection the sprite will be moved to stop the collision.

        You have to specify in which direction to check collisions, Otherwise, use 'collsions'.
        """
        for sprite in collision_group.sprites():
            if hasattr(sprite, "hitbox"):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == "horizontal" or direction == "h":
                        if self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.position.x = self.hitbox.centerx

                    if direction == "vertical" or direction == "v":
                        if self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        self.rect.centery = self.hitbox.centery
                        self.position.y = self.hitbox.centery

    def collisions(self,collision_group):
        """
        Check collisions in both directions. For more check 'collision'.
        """
        self.collision(collision_group,"h")
        self.collision(collision_group,"v")

    def resize_rect(self):
        """
        Resize the rect to the image size, keeping the position. Useful after changing image.
        """
        self.rect = self.image.get_rect(center=self.rect.center)

    def scale(self,scale:float=None,sizes:tuple=None,smooth:bool=False)->pygame.Surface:
        """
        Scale the sprite and resize the rect.
        """
        self.image = scale_image(self.image,scale,sizes,smooth)
        self.resize_rect()
        return self.image

    def flip(self,horizontal:bool,vertical:bool)->pygame.Surface:
        """
        Flip the sprite and resize the rect.
        """
        self.image = pygame.transform.flip(self.image,horizontal,vertical)
        self.resize_rect()
        return self.image

    def rotate(self,angle:int):
        """
        Rotate the sprite and resize the rect.
        """
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.resize_rect()
        return self.image

    def stick_to_parent(self):
        """
        Set its position to the parent position offsetted.
        """
        if self.parent:
            self.position = self.parent_offset+self.parent.position

class SimpleAnimatedSprite(Sprite):
    """
    Inherit from the helper sprite class, useful to add a basic animation to it.
    """
    def __init__(self,frames:List[pygame.Surface],topleft_pos:Tuple[int,int]=None,groups:Union[pygame.sprite.Group,List[pygame.sprite.Group]]=[],direction:Tuple[int,int]=(0,0),speed:Tuple[float,float]=(0,0),z_index:int=0,parent=None,parent_offset:Tuple[int,int]=(0,0)):
        self.frames = frames
        self.original_frames = frames

        self.frame_index = 0
        self.frame_speed = 0.2

        self.image = self.frames[int(self.frame_index)]
        super().__init__(self.image,topleft_pos,groups,direction,speed,z_index,parent,parent_offset)

    def scale(self,scale:float=None,scale_sizes:Tuple[int,int]=None,smooth:bool=False):
        """
        Scale the sprite.
        """
        self.frames = [scale_image(frame,scale,scale_sizes,smooth) for frame in self.frames]
        return self.frames

    def flip(self,horizontal:bool,vertical:bool)->pygame.Surface:
        """
        Flip the sprite.
        """
        self.frames = [pygame.transform.flip(frame,horizontal,vertical) for frame in self.frames]
        return self.frames

    def rotate(self,angle:int):
        """
        Rotate the sprite.
        """
        self.frames = [pygame.transform.rotate(frame,angle) for frame in self.original_frames]
        return self.frames

    def refresh_frames(self):
        """
        Call this when you change some frames, or use the set frames function.
        """
        self.original_frames = self.frames

    def set_frames(self,frames):
        """
        Set the frames and refresh them.
        """
        self.frames = frames
        self.original_frames = self.frames

    def copy(self):
        """
        Return an exact copy of the sprite (note: only built in attributes are copied).
        """
        new = SimpleAnimatedSprite(frames=self.frames,groups=self.groups(),z_index=self.z_index,direction=self.direction.xy,speed=self.speed.xy,position= self.position.xy)
        if hasattr(self,"rect"):
            new.rect = self.rect.copy()
        if hasattr(self, "hitbox"):
            new.hitbox = self.hitbox.copy()
        new.image = self.image
        new.frame_index = self.frame_index
        new.frame_speed = self.frame_speed
        return new

    def to_json(self,ignore_attributes:list=[])->dict:
        """
        Return a dictionary of the sprite that can be saved in a file, to be reloaded.
        """
        first = super().to_json(ignore_attributes)
        new = {}
        if not "frame_speed" in ignore_attributes:
            new["frame_speed"] = self.frame_speed
        if not "frames" in ignore_attributes:
            new["frames"] =[{"width":x.get_width(),"height":x.get_height()} for x in self.frames]
        if len(new.keys()) != 0:
            first.update(new)
        return first

    def from_json(self,json:dict,frames:list=[]):
        """
        Return a new sprite loaded from a dictionary.

        Since surfaces can't be properly saved, it's suggested to pass the frames here.
        """
        if len(frames)==0 and not "frames" in json.keys():
            raise AttributeError("Cannot create a new animated sprite without the frames in the argument or json.")
        if len(frames)>0:
            framess = frames 
        else:
            framess = [pygame.Surface((d["width"],d["height"])) for d in json["frames"]]
        new = super().from_json(json,framess)
        if "frame_speed" in json.keys():
            new.frame_speed = json["frame_speed"]
        return new

    def animate(self,kill_at_end:bool=False,dt:float=1.0,resize_rect=False)->None:
        """
        Update the frame index and the image.
        """
        # loop over images
        self.frame_index += self.frame_speed*dt
        if self.frame_index >= len(self.frames):
            if kill_at_end:
                self.kill()
            else:
                self.frame_index = 0
        
        # change image
        self.image = self.frames[int(self.frame_index)]
        if resize_rect:
            self.resize_rect()

class AnimatedSprite(Sprite):
    """
    Inherit from the helper sprite class, useful to create some complex animation with different types of them.
    """
    def __init__(self,animations_dict:Dict[str,List[pygame.Surface]],first_animation_name:str=None,topleft_pos:Tuple[int,int]=None,groups:Union[pygame.sprite.Group,List[pygame.sprite.Group]]=[],direction:Tuple[int,int]=(0,0),speed:Tuple[float,float]=(0,0),z_index:int=0,parent=None,parent_offset:Tuple[int,int]=(0,0)):
        

        self.animations = animations_dict
        self.current_animation = first_animation_name if first_animation_name else list(animations_dict.keys())[0]
        self.original_animations = self.animations

        self.frame_index = 0
        self.frame_speed = 0.2

        self.image = self.animations[self.current_animation][int(self.frame_index)]

        super().__init__(self.image,topleft_pos,groups,direction,speed,z_index,parent,parent_offset)

    def scale(self,scale:float=None,scale_sizes:Tuple[int,int]=None,smooth:bool=False):
        """
        Scale the sprite.
        """
        self.animations = {name:[scale_image(frame,scale,scale_sizes,smooth) for frame in frames] for name,frames in self.animations}
        return self.animations

    def flip(self,horizontal:bool,vertical:bool)->pygame.Surface:
        """
        Flip the sprite.
        """
        self.animations = {name:[pygame.transform.flip(frame,horizontal,vertical) for frame in frames] for name,frames in self.animations}
        return self.animations

    def rotate(self,angle:int):
        """
        Rotate the sprite.
        """
        self.animations = {name:[pygame.transform.rotate(frame,angle) for frame in frames] for name,frames in self.original_animations}
        return self.animations

    def refresh_animations(self):
        """
        Call if you change a frame in the animations.
        """
        self.original_animations = self.animations

    def set_animations(self,animations_dict:Dict[str,List[pygame.Surface]]):
        """
        Set the animations.
        """
        self.animations = animations_dict
        self.original_animations = self.animations

    def copy(self):
        """
        Return an exact copy of the sprite (note: only built in attributes are copied).
        """
        new = AnimatedSprite(self.animations,self.current_animation,groups=self.groups(),z_index=self.z_index,direction=self.direction.xy,speed=self.speed.xy,position= self.position.xy)
        if hasattr(self,"rect"):
            new.rect = self.rect.copy()
        if hasattr(self, "hitbox"):
            new.hitbox = self.hitbox.copy()
        new.image = self.image
        new.frame_index = self.frame_index
        new.frame_speed = self.frame_speed
        return new

    def to_json(self,ignore_attributes:list=[])->dict:
        """
        Return a dictionary of the sprite that can be saved in a file, to be reloaded.
        """
        first = super().to_json(ignore_attributes)
        new = {}
        if not "frame_speed" in ignore_attributes:
            new["frame_speed"] = self.frame_speed
        if not "frames" in ignore_attributes:
            new["animations"] ={str(name):[{"width":i.get_width(),"height":i.get_height()} for i in self.animations[name]] for name in self.animations.keys()}
        if not "current_animation" in ignore_attributes:
            new["current_animation"] = self.current_animation
        if len(new.keys()) != 0:
            first.update(new)
        return first

    def from_json(self,json:dict,animations:dict=None,current_animation:str=None):
        """
        Return a new sprite loaded from a dictionary.

        Since surfaces can't be properly saved, it's suggested to pass the animations here.
        """
        if (not animations and not "animations" in json.keys()) or (not current_animation and not "current_animation" in json.keys()):
            raise AttributeError("Cannot create a new animated sprite without the animations or the current animation in the argument or json.")
        if animations:
            frames = animations 
        else:
            frames = {name:[pygame.Surface((i["width"],i["height"])) for i in json["animations"][name]] for name in json["animations"].keys() }
        if current_animation:
            current = current_animation
        else:
            current = json["current_animation"]
        new = super().from_json(json,frames,current)
        if "frame_speed" in json.keys():
            new.frame_speed = json["frame_speed"]
        return new

    def animate(self,dt:float=1.0,resize_rect=False)->None:
        """
        Update the frame index and the image.
        """
        self.frame_index += self.frame_speed*dt
        if self.frame_index >= len(self.animations[self.current_animation]):
            self.frame_index = 0

        self.image = self.animations[self.current_animation][int(self.frame_index)]

        if resize_rect:
            self.resize_rect()

# GROUPS
class Group(pygame.sprite.Group):
    """
    A pygame group that allows json serialization.
    """
    def __init__(self):
        super().__init__()

    def to_json(self,ignore_attributes=[])->list:
        """
        Return a list of the serialized sprites using their own to_json methods.
        """
        sprites = []
        for sprite in self.sprites():
            if hasattr(sprite, "to_json"):
                json = sprite.to_json(ignore_attributes)
                sprites.append(sprite)
            else:
                raise AttributeError("Sprites need to have the to_json method defined in order to be serialized.")
        return sprites

    def from_json(self,json:List[Dict[str,Any]],sprite_type:Type,*from_json_extra_args)->list:
        """
        Create the sprites from a list of dictionaries to then add them to itself.
        """
        example = sprite_type()
        for sprite in json:
            if hasattr(example, "from_json"):
                s = example.from_json(sprite,from_json_extra_args)
                self.add(s)
            else:
                raise AttributeError("Sprites need to have the from_json method defined in order to be deserialized.")

class CameraGroup(Group):
    """
    Very useful for games with a camera like Stardew Valley.
    """
    def __init__(self):
        super().__init__()
        self.offset = pygame.math.Vector2()

    def draw(self,screen:pygame.Surface,main_sprite:Sprite,layers:list,screen_center:tuple)->None:
        """
        Draw the sprites sorting them by y coordinate and by layer, positioning the camera to the center of the main sprite.

        The sprites needs to have a z_index, rect and image.
        """
        self.offset.x = main_sprite.rect.centerx - screen_center[0]
        self.offset.y = main_sprite.rect.centery - screen_center[1]

        for layer in layers.values():
            for sprite in sorted(self.sprites(),key=lambda sprite:sprite.rect.centery):
                if sprite.z_index == layer:
                    offset_rect = sprite.rect.copy()
                    offset_rect.center -= self.offset

                    screen.blit(sprite.image, offset_rect)
