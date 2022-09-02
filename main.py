import pygame
import random
from pygame import mixer
pygame.mixer.pre_init(44100,-16,512)
mixer.init()
pygame.init()

# Game configuration variables
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
RED = (192,55,55)
WHITE = (255,255,255)
GREEN = (55,192,135)
BLACK = (0,0,0)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Time Bomb!')
programIcon = pygame.image.load('img/bomb.png').convert_alpha()
pygame.display.set_icon(programIcon)
pygame.mouse.set_visible(0)
clock = pygame.time.Clock()
FPS = 60
run = True
playing = False
lost = False
main_menu = True
font = pygame.font.SysFont('Futura',30)
lives = 3
level = 0
points = 0
speed = 0
max_speed = 8
timewarp_ticks = 0
bullets = 6

# Functions
def draw_rules():
    screen.fill(BLACK)
    screen.blit(rules_img,((0,0)))

def draw_text(text,font,text_col,x,y):
    img = font.render(text,True,text_col)
    screen.blit(img,(x,y))

def draw_bg():
    screen.fill(BLACK)
    screen.blit(bg_img,((0,0)))

def get_bird():
    bird_group.empty()
    height = random.randrange(15,350)
    if (level % 2) == 0: # even levels left to right
        bird = Bird(-100,height)
    else: # odd levels right to left
        bird = Bird(SCREEN_WIDTH+100,height)
    bird_group.add(bird)

def get_trays():
    tray_group.empty()
    for num in range(0,lives):
        tray_rect = tray_img.get_rect()
        tray_height = tray_img.get_height()
        tray_rect.x = (SCREEN_WIDTH//2)-(tray_height*2)
        tray_rect.y = SCREEN_HEIGHT-(125)+((tray_height*2)*num)
        tray = Tray(tray_rect.x,tray_rect.y)
        tray_group.add(tray)

def start_level():
    global bullets
    bullets = 6
    get_bird()
    bomb_group.empty()
    total_bombs = level+4
    bombs_created = 0
    global speed
    if speed < max_speed:
        speed = 2.80+(level*.10)
    else:
        speed = max_speed
    for num in range(0,total_bombs):
        while bombs_created < total_bombs:
            bomb_rect = bomb_img.get_rect()
            bomb_height = bomb_img.get_height()
            bomb_rect.x = random.randrange(0,15)*bomb_height
            bomb_rect.y = random.randrange(-12-level,-1)*bomb_height
            attempted_y = bomb_rect.y
            if duplicate_y_check(attempted_y):
                bomb = Bomb(bomb_rect.x,bomb_rect.y)
                bomb_group.add(bomb)
                bombs_created += 1

def duplicate_y_check(attempted_y):
    bomb_y_list = []
    for bomb in bomb_group:
        hbo_rect = bomb.image.get_rect(y = bomb.y)
        bomb_y_list.append(hbo_rect.y)
    if attempted_y in bomb_y_list:
        return False
    else:
        return True

# Classes
class Button():
    def __init__(self,x,y,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
    def draw(self):
        action = False
        # get mouse position
        pos = pygame.mouse.get_pos()
        # check mouseover and click conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        # draw button
        screen.blit(self.image,self.rect)
        return action

class TimeWarp():
    def __init__(self,x,y,timewarp_ticks,max_timewarp):
        self.x = x
        self.y = y
        self.timewarp_ticks = timewarp_ticks
        self.max_timewarp = max_timewarp

    def draw(self,timewarp_ticks):
        # update with new timewarp_ticks
        self.timewarp_ticks = timewarp_ticks
        # calculate ratio
        if timewarp_ticks != 0:
            ratio = self.timewarp_ticks / self.max_timewarp
        else:
            ratio = 0
        pygame.draw.rect(screen,BLACK,(self.x-2,self.y-2,154,24))
        pygame.draw.rect(screen,RED,(self.x,self.y,150,20))
        pygame.draw.rect(screen,GREEN,(self.x,self.y,150*ratio,20))

class Tray(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = tray_img
        self.x = x
        self.y = y
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        self.x = mouse_pos[0]-int((self.width//2))
        if self.x > SCREEN_WIDTH-self.width:
            self.x = SCREEN_WIDTH-self.width
        if self.x <= 0:
            self.x = 0
        screen.blit(self.image,(self.x,self.y))

    def update(self):
        if len(bomb_group) == 0 and len(bird_group) == 0:
            global playing
            playing = False

class Bomb(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        bomb_version = random.randrange(0,2)
        if bomb_version == 0:
            self.image = bomb_img
        else:
            self.image = pygame.transform.flip(bomb_img,True,False)
        self.x = x
        self.y = y
        self.height = self.image.get_height()
        self.rect = self.image.get_rect()

    def draw(self):
        global speed
        self.y = self.y+(speed)
        screen.blit(self.image,(self.x,self.y))

    def update(self):
        self.rect = self.image.get_rect()
        self_y = self.y
        if self.y > SCREEN_HEIGHT-self.height:
            for bomb in bomb_group:
                explosion_sprite = Explosion(bomb.x,bomb.y)
                explosion_group.add(explosion_sprite)
            explosion_fx.play()
            self.kill()
            # Pause game, clear remaining bombs, lose a life, start level over
            global lost,playing,lives
            playing = False
            lost = True
            lives -= 1
            get_trays()
        if lives <= 0:
            lives = 0
            self.kill()
            bomb_group.empty()

        for tray in tray_group:
            hto_rect = tray.image.get_rect(x = tray.x,y = tray.y)
            hbo_rect = self.image.get_rect(x = self.x,y = self.y)
            if hbo_rect.colliderect(hto_rect):
                global points,timewarp_ticks
                if timewarp_ticks < 100:
                    timewarp_ticks += 1
                points += 1
                catch_fx.play()
                self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self,explosion_x,explosion_y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f'img/explosion/{num}.png').convert_alpha()
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.x = explosion_x
        self.y = explosion_y
        self.rect = self.image.get_rect()
        explosion_sprite = (self.image,(self.x,self.y))
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4
        self.counter += 1
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            # if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]

    def draw(self):
        for explosion in explosion_group:
            screen.blit(explosion.image,(explosion.x,explosion.y))

class Bird(pygame.sprite.Sprite):
    def __init__(self,bird_x,bird_y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        if (level % 2) == 0: # even levels left to right
            for num in range(1,9):
                img = pygame.image.load(f'img/bird/{num}.png').convert_alpha()
                self.images.append(img)
        else:
            for num in range(1,9):
                img = pygame.image.load(f'img/bird/{num}.png').convert_alpha()
                img = pygame.transform.flip(img,True,False)
                self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.x = bird_x
        self.y = bird_y
        self.rect = self.image.get_rect()
        bird_sprite = (self.image,(self.x,self.y))
        self.counter = 0
        self.delay_target = random.randrange(0,200)
        self.delay_counter = 0

    def update(self):
        FLAP_SPEED = 8
        self.counter += 1
        if self.counter >= FLAP_SPEED:
            self.counter = 0
            self.frame_index += 1
            # if the animation is complete then delete the explosion
            if self.frame_index >= len(self.images):
                # self.kill()
                self.frame_index = 0
            else:
                self.image = self.images[self.frame_index]

        self.delay_counter += 1
        if self.delay_counter >= self.delay_target:
            self.delay_counter = 0
            self.delay_target = 0
            if (level % 2) == 0: # even levels left to right
                for bird in bird_group:
                    bird.x += speed
                    if bird.x >= SCREEN_WIDTH+100:
                        bird.kill()
            else: # odd levels right to left
                for bird in bird_group:
                    bird.x -= speed
                    if bird.x <= -100:
                        bird.kill()

    def draw(self):
        for bird in bird_group:
            screen.blit(bird.image,(bird.x,bird.y))

# Sprite groups
tray_group = pygame.sprite.Group()
bomb_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()

# Audio
explosion_fx = pygame.mixer.Sound('sound/explosion.wav')
explosion_fx.set_volume(0.3)
catch_fx = pygame.mixer.Sound('sound/catch.wav')
catch_fx.set_volume(0.2)
shoot_fx = pygame.mixer.Sound('sound/shoot.wav')
shoot_fx.set_volume(0.2)
woosh_fx = pygame.mixer.Sound('sound/woosh.wav')
woosh_fx.set_volume(0.3)

# Game images
rules_img = pygame.image.load('img/intro2.png').convert_alpha()
start_img = pygame.image.load('img/start.png').convert_alpha()
exit_img = pygame.image.load('img/exit.png').convert_alpha()
bg_img = pygame.image.load('img/bg2.png').convert_alpha()
bomb_img = pygame.image.load('img/bomb.png').convert_alpha()
tray_img = pygame.image.load('img/tray3.png').convert_alpha()
explosion_img = pygame.image.load('img/explosion/0.png').convert_alpha()
bird_img = pygame.image.load('img/bird/0.png').convert_alpha()
bullet_img = pygame.image.load('img/bullet.png').convert_alpha()
cursor_img = pygame.image.load('img/selection.png').convert_alpha()
cursor_rect = cursor_img.get_rect()
start_button = Button(SCREEN_WIDTH-380,20,start_img)
exit_button = Button(SCREEN_WIDTH-180,20,exit_img)

# Get the initial trays
get_trays()
timewarp_bar = TimeWarp(300,35,timewarp_ticks,100)

# Main loop
while run:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if bullets > 0:
                if playing:
                    shoot_fx.play()
                    bullets -= 1
                for bird in bird_group:
                    hbird_rect = bird.image.get_rect(x = bird.x,y = bird.y)
                    if hbird_rect.collidepoint(pygame.mouse.get_pos()):
                        points += 10
                        if timewarp_ticks < 100:
                            timewarp_ticks += 10
                            if timewarp_ticks > 100:
                                timewarp_ticks = 100
                        bird.kill()
                        explosion_x = pygame.mouse.get_pos()[0]
                        explosion_y = pygame.mouse.get_pos()[1]
                        explosion_sprite = Explosion(explosion_x,explosion_y)
                        explosion_group.add(explosion_sprite)
                # Shooting a bomb:
                for bomb in bomb_group:
                    hb_rect = bomb.image.get_rect(x = bomb.x,y = bomb.y)
                    if hb_rect.collidepoint(pygame.mouse.get_pos()):
                        points += 1
                        if timewarp_ticks < 100:
                            timewarp_ticks += 1
                            if timewarp_ticks > 100:
                                timewarp_ticks = 100
                        bomb.kill()
                        explosion_x = pygame.mouse.get_pos()[0]
                        explosion_y = pygame.mouse.get_pos()[1]
                        explosion_sprite = Explosion(explosion_x,explosion_y)
                        explosion_group.add(explosion_sprite)
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and playing == False and lives > 0:
                if lost:
                    lost = False
                    start_level()
                    playing = True
                else:
                    level += 1
                    start_level()
                    playing = True
            if event.key == pygame.K_r and playing == False and lives == 0:
                lives = 3
                level = 1
                lost = False
                points = 0
                speed = 3
                playing = True
                timewarp_ticks = 0
                get_trays()
                start_level()
    if pygame.mouse.get_pressed()[2] == True:
        if playing:
            if timewarp_ticks > 0:
                woosh_fx.play()
            if timewarp_ticks > 0:
                speed = 1
                timewarp_ticks -= 0.25
            else:
                speed = 2.75+(level*.25)
    if pygame.mouse.get_pressed()[2] == False:
        speed = 2.75+(level*.25)

    if main_menu == True:
        draw_rules()
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        draw_bg()

        for tray in tray_group:
            tray.update()
            tray.draw()

        for explosion in explosion_group:
            explosion.update()
            explosion.draw()

        if playing == True:
            for bomb in bomb_group:
                bomb.update()
                bomb.draw()
            for bird in bird_group:
                bird.update()
                bird.draw()
        else:
            if lives <= 0:
                draw_text('Game Over!',font,WHITE,330,270)
                draw_text('Press [R] to restart',font,WHITE,290,290)
            else:
                draw_text('Press [Space] to continue',font,WHITE,260,270)

        draw_text(f'Points: {points}',font,WHITE,10,10)
        draw_text(f'Level: {level}',font,WHITE,700,10)
        draw_text(f'Time Warp',font,WHITE,325,10)
        timewarp_bar.draw(timewarp_ticks)

        for bullet in range(bullets):
            screen.blit(bullet_img,((500+(bullet*25),10)))

    cursor_rect.center = pygame.mouse.get_pos()
    screen.blit(cursor_img,cursor_rect)

    clock.tick(FPS)
    pygame.display.update()
