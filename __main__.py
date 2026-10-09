import pygame
import pygame._sdl2.controller
import time
import random

import ledwall
print = ledwall.print


# -- LED WALL initialization stuff

# read settings from settings.py
# use default values if no settings.py exists
try:
    from settings import *
except ImportError:
    pass

if not 'RENDER_MODE' in dir():
    # 'led' = for led wall output
    # 'plain' = for pc/laptop or testing
    # 'sim' = led simulation for uli (deprecated)
    # 'arcade' = for toolbox arcade cabinet
    # 'square' = for square displays
    RENDER_MODE = 'led'

if not 'DEFAULT_BRIGHTNESS' in dir():
    if RENDER_MODE == 'led':
        BRIGHTNESS = -4
    else:
        BRIGHTNESS = 0

DEADZONE = 0.4

output = ledwall.initScreen(RENDER_MODE)
ledwall.setBrightnessValue(BRIGHTNESS)


print('init game controllers...')
pygame._sdl2.controller.init()
joymode = None

if not pygame._sdl2.controller.get_count():
    print('no controllers detected')
else:
    joymode = 'controller'
    print('found controllers:')
    for i in range(pygame._sdl2.controller.get_count()):
        joy = pygame._sdl2.controller.Controller(i)
        print(' - ' + joy.as_joystick().get_name())

if not joymode:    # use joystick lib as fallback
    pygame.joystick.init()
    if not pygame.joystick.get_count():
        print('no joystick detected')
    else:
        joymode = 'joystick'
        print('found joysticks:')
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            print(' - ' + joy.get_name())



# -- the actual game

clock = pygame.time.Clock()
tick = 0

sprites = {'p1 left': pygame.image.load('gfx/pumpkin1-left.png'),
           'p1 right': pygame.image.load('gfx/pumpkin1-right.png'),
           'p2 left': pygame.image.load('gfx/pumpkin2-left.png'),
           'p2 right': pygame.image.load('gfx/pumpkin2-right.png'),
           'g1 left': pygame.image.load('gfx/ghost1-left.png'),
           'g1 right': pygame.image.load('gfx/ghost1-right.png'),
           'g2 left': pygame.image.load('gfx/ghost2-left.png'),
           'g2 right': pygame.image.load('gfx/ghost2-right.png'),
           }


class Player:
    def __init__(self, x, y, number):
        self.x = x
        self.y = y

        self.xdir = 0
        self.ydir = 0

        self.facedir = 'left'       # 'left' or 'right'

        self.number = number
        self.state = 'pumpkin'      # 'pumpkin' or 'ghost

    def draw(self, output):
        key = '%s%i %s' % (self.state[0], self.number, self.facedir)
        sprite = sprites[key]
        output.blit(sprite, (self.x, self.y))

    def update(self):
        pass


class Game:
    def __init__(self):
        self.player1 = Player(32, 32, 1)
        self.player2 = Player(ledwall.SCR_W - 32 - 16, 32, 2)

        self.player1.facedir = 'right'
        self.player2.facedir = 'left'

    def render(self):
        self.player1.draw(output)
        self.player2.draw(output)

    def update(self):
        pass


class Application:
    def __init__(self):
        self.running = True

        self.game = Game()

    def render(self):
        output.fill((0, 0, 0))

        self.game.render()

        ledwall.compose()

    def controls(self):
        events = pygame.event.get()

        for e in events:
            if e.type==pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False

                if e.key == pygame.K_F1:
                    BRIGHTNESS -= 1
                    ledwall.setBrightnessValue(BRIGHTNESS)
                    
                elif e.key == pygame.K_F2:
                    BRIGHTNESS = min(BRIGHTNESS + 1, 0)
                    ledwall.setBrightnessValue(BRIGHTNESS)
                    
                elif e.key == pygame.K_F5:
                    ledwall.enableOverlay(not ledwall.showOverlay)
                elif e.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

    def update(self):
        self.game.update()


app = Application()

while app.running:
    app.render()
    app.controls()
    app.update()

    clock.tick(60)
    tick += 1

    if tick >= 60 * 4:
        ledwall.cls()
