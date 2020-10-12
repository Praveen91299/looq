# original code from DaFluffyPotato

import pygame, sys, os, random
clock = pygame.time.Clock()
import math
from data.microqiskit import *
import faulthandler; faulthandler.enable()

from pygame.locals import *

global e_colorkey
e_colorkey = (255,255,255)

def set_global_colorkey(colorkey):
    global e_colorkey
    e_colorkey = colorkey

# physics core

# 2d collisions test
def collision_test(object_1,object_list):
    collision_list = []
    for obj in object_list:
        if obj.colliderect(object_1):
            collision_list.append(obj)
    return collision_list

# 2d physics object
class physics_obj(object):
   
    def __init__(self,x,y,x_size,y_size):
        self.width = x_size
        self.height = y_size
        self.rect = pygame.Rect(x,y,self.width,self.height)
        self.x = x
        self.y = y
       
    def move(self,movement,platforms,ramps=[]):
        self.x += movement[0]
        self.rect.x = int(self.x)
        block_hit_list = collision_test(self.rect,platforms)
        collision_types = {'top':False,'bottom':False,'right':False,'left':False,'slant_bottom':False,'data':[]}
        # added collision data to "collision_types". ignore the poorly chosen variable name
        for block in block_hit_list:
            markers = [False,False,False,False]
            if movement[0] > 0:
                self.rect.right = block.left
                collision_types['right'] = True
                markers[0] = True
            elif movement[0] < 0:
                self.rect.left = block.right
                collision_types['left'] = True
                markers[1] = True
            collision_types['data'].append([block,markers])
            self.x = self.rect.x
        self.y += movement[1]
        self.rect.y = int(self.y)
        block_hit_list = collision_test(self.rect,platforms)
        for block in block_hit_list:
            markers = [False,False,False,False]
            if movement[1] > 0:
                self.rect.bottom = block.top
                collision_types['bottom'] = True
                markers[2] = True
            elif movement[1] < 0:
                self.rect.top = block.bottom
                collision_types['top'] = True
                markers[3] = True
            collision_types['data'].append([block,markers])
            self.change_y = 0
            self.y = self.rect.y
        return collision_types

# 3d collision detection
# todo: add 3d physics-based movement

class cuboid(object):
    
    def __init__(self,x,y,z,x_size,y_size,z_size):
        self.x = x
        self.y = y
        self.z = z
        self.x_size = x_size
        self.y_size = y_size
        self.z_size = z_size
        
    def set_pos(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z
        
    def collidecuboid(self,cuboid_2):
        cuboid_1_xy = pygame.Rect(self.x,self.y,self.x_size,self.y_size)
        cuboid_1_yz = pygame.Rect(self.y,self.z,self.y_size,self.z_size)
        cuboid_2_xy = pygame.Rect(cuboid_2.x,cuboid_2.y,cuboid_2.x_size,cuboid_2.y_size)
        cuboid_2_yz = pygame.Rect(cuboid_2.y,cuboid_2.z,cuboid_2.y_size,cuboid_2.z_size)
        if (cuboid_1_xy.colliderect(cuboid_2_xy)) and (cuboid_1_yz.colliderect(cuboid_2_yz)):
            return True
        else:
            return False

# entity stuff

def simple_entity(x,y,e_type):
    return entity(x,y,1,1,e_type)

def flip(img,boolean=True):
    return pygame.transform.flip(img,boolean,False)
 
def blit_center(surf,surf2,pos):
    x = int(surf2.get_width()/2)
    y = int(surf2.get_height()/2)
    surf.blit(surf2,(pos[0]-x,pos[1]-y))
 
class entity(object):
    global animation_database, animation_higher_database
   
    def __init__(self,x,y,size_x,size_y,e_type): # x, y, size_x, size_y, type
        self.x = x
        self.y = y
        self.size_x = size_x
        self.size_y = size_y
        self.obj = physics_obj(x,y,size_x,size_y)
        self.animation = None
        self.image = None
        self.animation_frame = 0
        self.animation_tags = []
        self.flip = False
        self.offset = [0,0]
        self.rotation = 0
        self.type = e_type # used to determine animation set among other things
        self.action_timer = 0
        self.action = ''
        self.set_action('idle') # overall action for the entity
        self.entity_data = {}
        self.alpha = None
        self.life = 5
        #self.time = 0
        self.score = 0
 
    def set_pos(self,x,y):
        self.x = x
        self.y = y
        self.obj.x = x
        self.obj.y = y
        self.obj.rect.x = x
        self.obj.rect.y = y
 
    def update_life(self, value):
    	self.life += value
    	if self.life <=0:
    		self.life = 5
    		self.x = 260
    		self.y = self.y - 50
    		self.score -= 10
 
    def move(self,momentum,platforms,ramps=[]):
        collisions = self.obj.move(momentum,platforms,ramps)
        self.x = self.obj.x
        self.y = self.obj.y
        return collisions
 
    def rect(self):
        return pygame.Rect(self.x,self.y,self.size_x,self.size_y)
 
    def set_flip(self,boolean):
        self.flip = boolean
 
    def set_animation_tags(self,tags):
        self.animation_tags = tags
 
    def set_animation(self,sequence):
        self.animation = sequence
        self.animation_frame = 0
 
    def set_action(self,action_id,force=False):
        if (self.action == action_id) and (force == False):
            pass
        else:
            self.action = action_id
            anim = animation_higher_database[self.type][action_id]
            self.animation = anim[0]
            self.set_animation_tags(anim[1])
            self.animation_frame = 0

    def get_entity_angle(entity_2):
        x1 = self.x+int(self.size_x/2)
        y1 = self.y+int(self.size_y/2)
        x2 = entity_2.x+int(entity_2.size_x/2)
        y2 = entity_2.y+int(entity_2.size_y/2)
        angle = math.atan((y2-y1)/(x2-x1))
        if x2 < x1:
            angle += math.pi
        return angle

    def get_center(self):
        x = self.x+int(self.size_x/2)
        y = self.y+int(self.size_y/2)
        return [x,y]
 
    def clear_animation(self):
        self.animation = None
 
    def set_image(self,image):
        self.image = image
 
    def set_offset(self,offset):
        self.offset = offset
 
    def set_frame(self,amount):
        self.animation_frame = amount
 
    def handle(self):
        self.action_timer += 1
        self.change_frame(1)
 
    def change_frame(self,amount):
        self.animation_frame += amount
        if self.animation != None:
            while self.animation_frame < 0:
                if 'loop' in self.animation_tags:
                    self.animation_frame += len(self.animation)
                else:
                    self.animation = 0
            while self.animation_frame >= len(self.animation):
                if 'loop' in self.animation_tags:
                    self.animation_frame -= len(self.animation)
                else:
                    self.animation_frame = len(self.animation)-1
 
    def get_current_img(self):
        if self.animation == None:
            if self.image != None:
                return flip(self.image,self.flip)
            else:
                return None
        else:
            return flip(animation_database[self.animation[self.animation_frame]],self.flip)

    def get_drawn_img(self):
        image_to_render = None
        if self.animation == None:
            if self.image != None:
                image_to_render = flip(self.image,self.flip).copy()
        else:
            image_to_render = flip(animation_database[self.animation[self.animation_frame]],self.flip).copy()
        if image_to_render != None:
            center_x = image_to_render.get_width()/2
            center_y = image_to_render.get_height()/2
            image_to_render = pygame.transform.rotate(image_to_render,self.rotation)
            if self.alpha != None:
                image_to_render.set_alpha(self.alpha)
            return image_to_render, center_x, center_y
 
    def display(self,surface,scroll):
        image_to_render = None
        if self.animation == None:
            if self.image != None:
                image_to_render = flip(self.image,self.flip).copy()
        else:
            image_to_render = flip(animation_database[self.animation[self.animation_frame]],self.flip).copy()
        if image_to_render != None:
            center_x = image_to_render.get_width()/2
            center_y = image_to_render.get_height()/2
            image_to_render = pygame.transform.rotate(image_to_render,self.rotation)
            if self.alpha != None:
                image_to_render.set_alpha(self.alpha)
            blit_center(surface,image_to_render,(int(self.x)-scroll[0]+self.offset[0]+center_x,int(self.y)-scroll[1]+self.offset[1]+center_y))
    
    def display_stats(self, surface, img):
    	#display hearts
    	for i in range(self.life):
    		location = (16 + i*16, 16)
    		surface.blit(img, location)
    	font = pygame.font.Font('data/Roboto-Regular.ttf', 10)
    	text_img = font.render('Score: ' + str(self.score), True, (0, 0, 0))
    	surface.blit(text_img, (150, 20))
    	return

# animation stuff

global animation_database
animation_database = {}
 
global animation_higher_database
animation_higher_database = {}
 
# a sequence looks like [[0,1],[1,1],[2,1],[3,1],[4,2]]
# the first numbers are the image name(as integer), while the second number shows the duration of it in the sequence
def animation_sequence(sequence,base_path,colorkey=(255,255,255),transparency=255):
    global animation_database
    result = []
    for frame in sequence:
        image_id = base_path + base_path.split('/')[-2] + '_' + str(frame[0])
        image = pygame.image.load(image_id + '.png').convert()
        image.set_colorkey(colorkey)
        image.set_alpha(transparency)
        animation_database[image_id] = image.copy()
        for i in range(frame[1]):
            result.append(image_id)
    return result
 
 
def get_frame(ID):
    global animation_database
    return animation_database[ID]
 
def load_animations(path):
    global animation_higher_database, e_colorkey
    f = open(path + 'entity_animations.txt','r')
    data = f.read()
    f.close()
    for animation in data.split('\n'):
        sections = animation.split(' ')
        anim_path = sections[0]
        entity_info = anim_path.split('/')
        entity_type = entity_info[0]
        animation_id = entity_info[1]
        timings = sections[1].split(';')
        tags = sections[2].split(';')
        sequence = []
        n = 0
        for timing in timings:
            sequence.append([n,int(timing)])
            n += 1
        anim = animation_sequence(sequence,path + anim_path,e_colorkey)
        if entity_type not in animation_higher_database:
            animation_higher_database[entity_type] = {}
        animation_higher_database[entity_type][animation_id] = [anim.copy(),tags]

# particles

def particle_file_sort(l):
    l2 = []
    for obj in l:
        l2.append(int(obj[:-4]))
    l2.sort()
    l3 = []
    for obj in l2:
        l3.append(str(obj) + '.png')
    return l3

global particle_images
particle_images = {}

def load_particle_images(path):
    global particle_images, e_colorkey
    file_list = os.listdir(path)
    for folder in file_list:
        try:
            img_list = os.listdir(path + '/' + folder)
            img_list = particle_file_sort(img_list)
            images = []
            for img in img_list:
                images.append(pygame.image.load(path + '/' + folder + '/' + img).convert())
            for img in images:
                img.set_colorkey(e_colorkey)
            particle_images[folder] = images.copy()
        except:
            pass

class particle(object):

    def __init__(self,x,y,particle_type,motion,decay_rate,start_frame,custom_color=None):
        self.x = x
        self.y = y
        self.type = particle_type
        self.motion = motion
        self.decay_rate = decay_rate
        self.color = custom_color
        self.frame = start_frame

    def draw(self,surface,scroll):
        global particle_images
        if self.frame > len(particle_images[self.type])-1:
            self.frame = len(particle_images[self.type])-1
        if self.color == None:
            blit_center(surface,particle_images[self.type][int(self.frame)],(self.x-scroll[0],self.y-scroll[1]))
        else:
            blit_center(surface,swap_color(particle_images[self.type][int(self.frame)],(255,255,255),self.color),(self.x-scroll[0],self.y-scroll[1]))

    def update(self):
        self.frame += self.decay_rate
        running = True
        if self.frame > len(particle_images[self.type])-1:
            running = False
        self.x += self.motion[0]
        self.y += self.motion[1]
        return running
        

# other useful functions

def swap_color(img,old_c,new_c):
    global e_colorkey
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img,(0,0))
    surf.set_colorkey(e_colorkey)
    return surf


#need to setup setting IBM account#############################################3
def get_rand(l, n):
	#check number range if fine
	l = list(l)
	temp = []
	#backend = Aer.get_backend('qasm_simulator')
	length = math.ceil(math.log2(len(l)))
	for i in range(n):
		qc = QuantumCircuit(1, 1)
		qc.h(0)
		qc.measure(0, 0)
		job = simulate(qc, shots = length, get='memory')
		temp2 = 0
		for x in range(length):
			temp2 = temp2*2 + int(job[x])
		temp2 = temp2%len(l)
		temp.append(l[temp2])
	return temp

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init() # initiates pygame
pygame.mixer.set_num_channels(64)

pygame.display.set_caption('looq')

WINDOW_SIZE = (1200,800)
white = (255, 255, 255)
black = (0, 0, 0)
red = (200, 0, 0)

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate the window

display = pygame.Surface((300,200)) # used as the surface for rendering, which is scaled

moving_right = False
moving_left = False
vertical_momentum = 0
air_timer = 0

true_scroll = [0,0]

LOOP_NO = 0

#text stuff
font_player = pygame.font.Font('data/Roboto-Regular.ttf', 9)
font_instruct = pygame.font.Font('data/Roboto-Regular.ttf', 9)
font_virus = pygame.font.Font('data/Roboto-Regular.ttf', 9)
font_title = pygame.font.Font('data/Roboto-Regular.ttf', 30)
fonts = {'player':font_player, 'instruct':font_instruct, 'virus': font_virus, 'title': font_title}

#messages
msg_count = 0
msg_check = True
f = open('data/msg.txt', 'r')
data = f.read()
f.close()
msg_list = data.split('\n')

#instructions
f = open('data/instructions.txt', 'r')
data = f.read()
f.close()
instruct_list = data.split('\n')

load_animations('data/images/entities/')


#resource loading
grass_img = pygame.image.load('data/images/grass.png')
dirt_img = pygame.image.load('data/images/dirt.png')
plant_img = pygame.image.load('data/images/plant.png').convert()
plant_img.set_colorkey((255,255,255))

tile_index = {1:grass_img,
              2:dirt_img,
              3:plant_img
              }

player_img = pygame.image.load('data/images/player.png')
virus_img = pygame.image.load('data/images/virus.png').convert()
virus_img.set_colorkey((255, 255, 255))

msg_box = pygame.image.load('data/images/msg_box.png').convert()
msg_box.set_colorkey(white)

sun_img = pygame.image.load('data/images/sun.png').convert()
sun_img.set_colorkey((255, 255, 255))

heart_img = pygame.image.load('data/images/heart.png').convert()
heart_img.set_colorkey((255, 255, 255))

bug_img = pygame.image.load('data/images/bug.png').convert()
bug_img.set_colorkey(white)
bug_img_green = pygame.image.load('data/images/bug_green.png').convert()
bug_img_green.set_colorkey(white)
bug_img_red = pygame.image.load('data/images/bug_red.png').convert()
bug_img_red.set_colorkey(white)
bug_img_yellow = pygame.image.load('data/images/bug_yellow.png').convert()
bug_img_yellow.set_colorkey(white)
bug_img_bin = pygame.image.load('data/images/bin.png')

fireball_img = pygame.image.load('data/images/fireball.png').convert()
fireball_img.set_colorkey(white)

bug_index = {1:bug_img, 2:bug_img_red, 3:bug_img_yellow, 4: bug_img_bin, 5:bug_img_green}

jump_sound = pygame.mixer.Sound('data/audio/jump.wav')
grass_sounds = [pygame.mixer.Sound('data/audio/grass_0.wav'),pygame.mixer.Sound('data/audio/grass_1.wav')]
grass_sounds[0].set_volume(0.2)
grass_sounds[1].set_volume(0.2)

pygame.mixer.music.load('data/audio/music.wav')
pygame.mixer.music.play(-1)

grass_sound_timer = 0

#loading map and tile list as global
def load_map(path):
	f = open(path+'.txt', 'r')
	data = f.read()
	f.close()
	data = data.split('\n')
	game_map = []
	for row in data:
		game_map.append(list(row))
	return game_map

game_map = load_map('data/map')
bug_list = []
def render_map(disp):
	disp.fill((146,244,255))
	sun_rect = pygame.Rect(480 - scroll[0], 50 - scroll[1], sun_img.get_width(), sun_img.get_height())
	disp.blit(sun_img,sun_rect)
	tile_rects = []
	y = 0
	for layer in game_map:
		x = 0
		for tile in layer:
			if tile == '1':
				disp.blit(dirt_img,(x*16 - scroll[0],y*16 - scroll[1]))
			if tile == '2':
				disp.blit(grass_img,(x*16 - scroll[0],y*16 - scroll[1]))
			if tile in ['1', '2']:
				tile_rects.append(pygame.Rect(x*16, y*16,16,16))
			x += 1
		y += 1
	for item in bug_list:
		disp.blit(item.image, (item.x - scroll[0], item.y - scroll[1]))
		#tile_rects.append(item.rect())
	return tile_rects

def disp_text(font_type, text, disp, location = (150, 100), col1 = white, col2 = black):
	if font_type == 'virus':
		col1 = red
	
	text_img = fonts[font_type].render(text, True, col1)
	text_rect = text_img.get_rect()
	text_rect.center = location
	disp.blit(text_img, text_rect)
	return

def disp_update(disp, FPS = 60):
	screen.blit(pygame.transform.scale(disp,WINDOW_SIZE),(0,0))
	pygame.display.update()
	clock.tick(FPS)

class bug():
	def __init__(self, x, y, bug_type = 1, count = 0):
		self.x = x
		self.y = y
		self.image = bug_index[bug_type]
		self.size_x = self.image.get_width()
		self.size_y = self.image.get_height()
		self.state = bug_type
		self.ID = count
	def rect(self):
		return pygame.Rect(self.x,self.y,self.size_x,self.size_y)
	def apply_super(self):
		self.state = 2
		copy1 = bug(self.x, self.y, 2, self.ID)
		copy2 = bug(self.x, self.y, 2, self.ID)
		copy1.x -= 16
		copy2.x += 16
		copy1.image = bug_index[copy1.state]
		copy2.image = bug_index[copy2.state]
		bug_list.append(copy1)
		bug_list.append(copy2)
		return

class fireball():
	def __init__(self, x, y, fire_type = 'super', flip = False, life = 80):
		self.x = x
		self.y = y
		self.image = fireball_img
		self.size_x = self.image.get_width()
		self.size_y = self.image.get_height()
		self.life = life
		self.speed = 1
		self.direction = flip
		self.type = fire_type
	def rect(self):
		return pygame.Rect(self.x,self.y,self.size_x,self.size_y)
	def update(self):
		self.life -= 1
		if self.life == 0:
			return -1
		self.x += (-self.speed) if self.direction else self.speed
		return 1

def add_bugs(number = 10):
	randomlist = get_rand(range(26, 128), number)
	bug_list = []
	global bug_count
	y = 0
	for layer in game_map:
		x = 0
		for tile in layer:
			if tile == '2' and x in randomlist:
				bug_list.append(bug(x*16, (y-1)*16, 1, bug_count))
				bug_count +=1
				randomlist.remove(x)
			x += 1
		y += 1
	return bug_list

def glitch_screen(n):
	randx = get_rand(range(0, 19), n)
	randy = get_rand(range(0, 12), n)
	
	for i in range(0, n):
		display.blit(bug_index[4], pygame.Rect(randx[i]*16, randy[i]*16, 16, 16))
		disp_update(display, int(n/5))

player = entity(500,100,5,13,'player')
######################################################################################################
#beginning sequence
while LOOP_NO == 0:
	display.fill(black)
	disp_text('instruct', instruct_list[0], display, (150, 150))
	if msg_list[msg_count] == 'NEXT':
		msg_count += 1
		LOOP_NO = 1
		display.fill(black)
		disp_text('title', 'looq', display, (150, 100))
		disp_update(display, 0.4)
		break
	msg = msg_list[msg_count].split(':')
	
	disp_text(msg[0], msg[1], display, (150, 100))
	for event in pygame.event.get(): # event loop
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == KEYDOWN:
			if event.key == K_RETURN:
				LOOP_NO = 1
				display.fill(black)
				disp_text('title', 'looq', display, (150, 100))
				disp_update(display, 0.4)
				msg_count = 12
				break
			if event.key == K_SPACE:
				msg_count += 1
	disp_update(display, 60)

msg_count = 12
msg = msg_list[msg_count].split(':')
glitch_screen(50)

show_instruct = True
#first game loop
while LOOP_NO == 1: # game loop
	if grass_sound_timer > 0:
		grass_sound_timer -= 1
	if player.x < 260:
		player_disp = player.x - 2208
		player.set_pos(2208, player.y)
		true_scroll[0] = true_scroll[0] - player_disp
	if player.x > 2208:
		player_disp = player.x - 260
		player.set_pos(260, player.y)
		true_scroll[0] = true_scroll[0] - player_disp
		msg_count = 19
		msg_check = True
		msg = msg_list[msg_count].split(':')
		LOOP_NO = 2
	if player.x > 400:
		show_instruct = False
	
	true_scroll[0] += (player.x-true_scroll[0]-152)/20
	#print(true_scroll[0])
	true_scroll[1] += (player.y-true_scroll[1]-106)/20
	scroll = true_scroll.copy()
	scroll[0] = int(scroll[0])
	scroll[1] = int(scroll[1])
	tile_rects = []
	#drawing background objects
	tile_rects = render_map(display)
	
	display.blit(virus_img, (300-32, 200-32))
	display.blit(player_img, (8, 200 - 24))
	if msg_check:
		display.blit(msg_box, (50, 200 - 32))
		#msg = msg_list[msg_count].split(':')
		disp_text(msg[0], msg[1], display, (150, 200-16), black)
		disp_text('instruct', instruct_list[2], display, (150, 200 - 8), black)
	if show_instruct:
		disp_text('player', instruct_list[1], display, (150, 50), black)
	player_movement = [0,0]
	if moving_right == True:
		player_movement[0] += 2
	if moving_left == True:
		player_movement[0] -= 2
	player_movement[1] += vertical_momentum
	vertical_momentum += 0.2
	if vertical_momentum > 3:
		vertical_momentum = 3
	
	if player_movement[0] == 0:
		player.set_action('idle')
	if player_movement[0] > 0:
		player.set_flip(False)
		player.set_action('run')
	if player_movement[0] < 0:
		player.set_flip(True)
		player.set_action('run')
	
	collision_types = player.move(player_movement,tile_rects)
	
	if collision_types['bottom'] == True:
		air_timer = 0
		vertical_momentum = 0
		if player_movement[0] != 0:
			if grass_sound_timer == 0:
				grass_sound_timer = 30
				random.choice(grass_sounds).play()
	else:
		air_timer += 1
	player.change_frame(1)
	player.display(display,scroll)
	player.display_stats(display, heart_img)
	
	for event in pygame.event.get(): # event loop
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == KEYDOWN:
			if event.key == K_m:
				pygame.mixer.music.fadeout(1000)
			if event.key == K_d:
				moving_right = True
			if event.key == K_a:
				moving_left = True
			if event.key == K_w:
				if air_timer < 6:
					jump_sound.play()
					vertical_momentum = -5
			if event.key == K_SPACE:
				if msg_check:
					msg = msg_list[msg_count].split(':')
					if msg[0] == 'NEXT':
						msg_check = False
					msg_count += 1
		if event.type == KEYUP:
			if event.key == K_d:
				moving_right = False
			if event.key == K_a:
				moving_left = False
	disp_update(display, 60)

#need to add plain bugs

bug_count = 0
bug_list = add_bugs(10)
fire_list = []
flag1 = True #first collision of fire and error
flag2 = True #first collision of player and super error
show_instruct = True

#while loop 2 superposition gun
while LOOP_NO == 2:
	player_disp = 0
	if grass_sound_timer > 0:
		grass_sound_timer -= 1
	if player.x < 260:
		player_disp = player.x - 2208
		player.set_pos(2208, player.y)
		true_scroll[0] = true_scroll[0] - player_disp
	if player.x > 2208:
		player_disp = player.x - 260
		player.set_pos(260, player.y)
		true_scroll[0] = true_scroll[0] - player_disp
	
	true_scroll[0] += (player.x-true_scroll[0]-152)/20
	#print(true_scroll[0])
	true_scroll[1] += (player.y-true_scroll[1]-106)/20
	scroll = true_scroll.copy()
	scroll[0] = int(scroll[0])
	scroll[1] = int(scroll[1])
	tile_rects = []
	
	#drawing background and otherobjects
	tile_rects = render_map(display)
	
	display.blit(virus_img, (300-32, 200-32))
	display.blit(player_img, (8, 200 - 24))
	if msg_check:
		display.blit(msg_box, (50, 200 - 32))
		#msg = msg_list[msg_count].split(':')
		if msg[0] != 'NEXT':
			disp_text(msg[0], msg[1], display, (150, 200-16), black)
			disp_text('instruct', instruct_list[2], display, (150, 200 - 8), black)
	
	if show_instruct:
		disp_text('player', instruct_list[3], display, (150, 50), black)
	elif flag2:
		disp_text('player', instruct_list[4], display, (150, 50), black)
	player_movement = [0,0]
	if moving_right == True:
		player_movement[0] += 2
	if moving_left == True:
		player_movement[0] -= 2
	player_movement[1] += vertical_momentum
	vertical_momentum += 0.2
	if vertical_momentum > 3:
		vertical_momentum = 3
	
	if player_movement[0] == 0:
		player.set_action('idle')
	if player_movement[0] > 0:
		player.set_flip(False)
		player.set_action('run')
	if player_movement[0] < 0:
		player.set_flip(True)
		player.set_action('run')
	
	collision_types = player.move(player_movement,tile_rects)
	
	if collision_types['bottom'] == True:
		air_timer = 0
		vertical_momentum = 0
		if player_movement[0] != 0:
			if grass_sound_timer == 0:
				grass_sound_timer = 30
				random.choice(grass_sounds).play()
	else:
		air_timer += 1
	player.change_frame(1)
	player.display(display,scroll)
	player.display_stats(display, heart_img)
	
	for fire in fire_list:
		display.blit(fire.image, (fire.x - player_disp - scroll[0], fire.y - player_disp - scroll[1]))
		check = fire.update()
		if check == -1:
			fire_list.remove(fire)
	
	#checking if any collisions of error and fire
	for bug1 in bug_list:
		for fire in fire_list:
			if fire.rect().colliderect(bug1.rect()) and bug1.state == 1:
				if fire.type == 'super':
					bug1.apply_super()
					bug_list.remove(bug1)
					if flag1:
						msg_count = 32
						msg_check = True
						flag1 = False
				fire_list.remove(fire)
		if player.rect().colliderect(bug1.rect()):
			if bug1.state == 1:
				player.update_life(-1)
				player.set_pos(player.x - 16, player.y - 16)
			elif bug1.state == 2:
				rand_bug = get_rand([0, 1], 1)[0]
				templist = []
				for bug2 in bug_list:
					if bug2.ID == bug1.ID:
						bug2.state = 4
						bug2.image = bug_index[4]
						templist.append(bug2)
				bug_list.remove(templist[rand_bug])
				player.score += 20
				if flag2:
					msg_count = 37
					msg_check = True
					flag2 = False
					#LOOP_NO +=1
	
	if player.score >= 100:
		LOOP_NO +=1
	
	for event in pygame.event.get(): # event loop
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == KEYDOWN:
			if event.key == K_m:
				pygame.mixer.music.fadeout(1000)
			if event.key == K_d:
				moving_right = True
			if event.key == K_a:
				moving_left = True
			if event.key == K_s:
				fire_list.append(fireball(player.x, player.y, flip = player.flip))
				show_instruct = False
			if event.key == K_w:
				if air_timer < 6:
					jump_sound.play()
					vertical_momentum = -5
			if event.key == K_SPACE:
				if msg_check:
					msg = msg_list[msg_count].split(':')
					if msg[0] == 'NEXT':
						msg_check = False
					msg_count += 1
		if event.type == KEYUP:
			if event.key == K_d:
				moving_right = False
			if event.key == K_a:
				moving_left = False
	disp_update(display, 60)

glitch_screen(50)
moving_right = False
moving_left = False
msg_count = 46
flag = False

#darkness
while LOOP_NO == 3:
	display.fill(black)
	disp_text('instruct', instruct_list[0], display, (150, 150))
	if msg_list[msg_count] == 'NEXT':
		msg_count += 1
		LOOP_NO = 4
		display.fill(black)
		disp_text('title', 'looq', display, (150, 100))
		disp_update(display, 0.4)
		break
	msg = msg_list[msg_count].split(':')
	
	disp_text(msg[0], msg[1], display, (150, 100))
	for event in pygame.event.get(): # event loop
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == KEYDOWN:
			if event.key == K_RETURN and msg_count is not 53:
				msg_count = 53
				flag = True
			if event.key == K_SPACE and msg_count is not 53:
				msg_count += 1
			if msg_count == 53:
				if event.key == K_y:
					LOOP_NO = 4
					msg_count = 58
					break
				if event.key == K_n:
					LOOP_NO = 5
					msg_count = 55
					break
	disp_update(display, 60)

fire_list = []
fire2_list = []
hold_ID = -1
ent_count = 0
show_instruct = True
show_instruct2 = False

bug_list.extend(add_bugs(10))

#fight back loop
while LOOP_NO == 4:
	player_disp = 0
	if grass_sound_timer > 0:
		grass_sound_timer -= 1
	if player.x < 260:
		player_disp = player.x - 2208
		player.set_pos(2208, player.y)
		true_scroll[0] = true_scroll[0] - player_disp
	if player.x > 2208:
		player_disp = player.x - 260
		player.set_pos(260, player.y)
		true_scroll[0] = true_scroll[0] - player_disp
	
	true_scroll[0] += (player.x-true_scroll[0]-152)/20
	#print(true_scroll[0])
	true_scroll[1] += (player.y-true_scroll[1]-106)/20
	scroll = true_scroll.copy()
	scroll[0] = int(scroll[0])
	scroll[1] = int(scroll[1])
	tile_rects = []
	
	#drawing background and otherobjects
	tile_rects = render_map(display)
	
	display.blit(virus_img, (300-32, 200-32))
	display.blit(player_img, (8, 200 - 24))
	if msg_check and (msg_list[msg_count].split(':')[0] != 'NEXT'):
		display.blit(msg_box, (50, 200 - 32))
		msg = msg_list[msg_count].split(':')
		disp_text(msg[0], msg[1], display, (150, 200-16), black)
	
	if show_instruct:
		disp_text('player', instruct_list[5], display, (150, 50), black)
	if show_instruct2:
		disp_text('player', instruct_list[6], display, (150, 50), black)
	
	player_movement = [0,0]
	if moving_right == True:
		player_movement[0] += 2
	if moving_left == True:
		player_movement[0] -= 2
	player_movement[1] += vertical_momentum
	vertical_momentum += 0.2
	if vertical_momentum > 3:
		vertical_momentum = 3
	
	if player_movement[0] == 0:
		player.set_action('idle')
	if player_movement[0] > 0:
		player.set_flip(False)
		player.set_action('run')
	if player_movement[0] < 0:
		player.set_flip(True)
		player.set_action('run')
	
	collision_types = player.move(player_movement,tile_rects)
	
	if collision_types['bottom'] == True:
		air_timer = 0
		vertical_momentum = 0
		if player_movement[0] != 0:
			if grass_sound_timer == 0:
				grass_sound_timer = 30
				random.choice(grass_sounds).play()
	else:
		air_timer += 1
	player.change_frame(1)
	player.display(display,scroll)
	player.display_stats(display, heart_img)
	
	for fire in fire_list:
		display.blit(fire.image, (fire.x - player_disp - scroll[0], fire.y - player_disp - scroll[1]))
		check = fire.update()
		if check == -1:
			fire_list.remove(fire)
	
	for fire in fire2_list:
		display.blit(fire.image, (fire.x - player_disp - scroll[0], fire.y - player_disp - scroll[1]))
		check = fire.update()
		if check == -1:
			fire2_list.remove(fire)
	
	#checking if any collisions of error and fire
	flag3 = False
	for bug1 in bug_list:
		for fire in fire_list:
			if fire.rect().colliderect(bug1.rect()) and bug1.state == 1:
				if fire.type == 'super':
					bug1.apply_super()
					bug_list.remove(bug1)
				fire_list.remove(fire)
		for fire in fire2_list:
			if fire.rect().colliderect(bug1.rect()) and bug1.state == 4:
				player.score += 5
				bug1.state = 5
				bug1.image = bug_index[5]
				if hold_ID != -1:
					bug1.ID = hold_ID
					hold_ID = -1
				else:
					hold_ID = bug1.ID
				if show_instruct2:
					show_instruct = False
		if player.rect().colliderect(bug1.rect()):
			if bug1.state == 1:
				player.update_life(-1)
				player.set_pos(player.x - 16, player.y - 16)
			elif bug1.state == 2:
				rand_bug = get_rand([0, 1], 1)[0]
				templist = []
				for bug2 in bug_list:
					if bug2.ID == bug1.ID:
						bug2.state = 4
						bug2.image = bug_index[4]
						templist.append(bug2)
				bug_list.remove(templist[rand_bug])
				player.score += 20
			elif bug1.state == 5:
				for bug2 in bug_list:
					if bug2.state == 5 and bug2.ID == bug1.ID and bug1 is not bug2:
						player.score +=20
						ent_count +=1
						bug_list.remove(bug2)
						bug_list.remove(bug1)
						flag3 = True
						break
			if flag3:
				break
	
	if ent_count >= 5:
		LOOP_NO = 6
		msg_count = 64
		msg_check = True
		break
	
	for event in pygame.event.get(): # event loop
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == KEYDOWN:
			if event.key == K_m:
				pygame.mixer.music.fadeout(1000)
			if event.key == K_d:
				moving_right = True
			if event.key == K_a:
				moving_left = True
			if event.key == K_s:
				fire_list.append(fireball(player.x, player.y, flip = player.flip))
			if event.key == K_e:
				fire2_list.append(fireball(player.x, player.y, fire_type = 'ent', flip = player.flip))
				show_instruct = False
				if show_instruct:
					show_instruct = False
					show_instruct2 = True
			if event.key == K_w:
				if air_timer < 6:
					jump_sound.play()
					vertical_momentum = -5
			if event.key == K_SPACE:
				if msg_check:
					msg = msg_list[msg_count].split(':')
					if msg[0] == 'NEXT':
						msg_check = False
					msg_count += 1
		if event.type == KEYUP:
			if event.key == K_d:
				moving_right = False
			if event.key == K_a:
				moving_left = False
	disp_update(display, 60)

#ending loop
msg_check = True
while LOOP_NO == 5:
	display.fill(black)
	disp_text('instruct', instruct_list[0], display, (150, 150))
	if msg_list[msg_count] == 'NEXT':
		display.fill(black)
		disp_text('title', 'looq', display, (150, 100))
		disp_update(display, 0.4)
		break
	msg = msg_list[msg_count].split(':')
	
	disp_text(msg[0], msg[1], display, (150, 100))
	
	if msg_count == 56:
		disp_text('player', str(player.score), display, (150, 120))
		msg_check = False
	for event in pygame.event.get(): # event loop
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == KEYDOWN:
			if msg_check:
				if event.key == K_RETURN:
					msg_count = 56
				if event.key == K_SPACE:
					msg_count += 1
			else:
				if event.key == K_RETURN or event.key == K_SPACE:
					glitch_screen(50)
					LOOP_NO = 7
					pygame.quit()
					sys.exit()
	disp_update(display, 60)

while LOOP_NO == 6:
	display.fill(black)
	disp_text('instruct', instruct_list[0], display, (150, 150))
	if msg_list[msg_count] == 'NEXT':
		display.fill(black)
		disp_text('title', 'looq', display, (150, 100))
		disp_update(display, 0.4)
		break
	msg = msg_list[msg_count].split(':')
	
	disp_text(msg[0], msg[1], display, (150, 100))
	
	if msg_count == 68:
		disp_text('player', str(player.score), display, (150, 120))
		msg_check = False
	for event in pygame.event.get(): # event loop
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		if event.type == KEYDOWN:
			if msg_check:
				if event.key == K_RETURN:
					msg_count = 68
				if event.key == K_SPACE:
					msg_count += 1
			else:
				if event.key == K_RETURN or event.key == K_SPACE:
					glitch_screen(50)
					LOOP_NO = 7
					pygame.quit()
					sys.exit()
	disp_update(display, 60)
