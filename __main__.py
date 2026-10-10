import pygame
import pygame._sdl2.controller
import argparse
import time
import random

import ledwall
print = ledwall.print


# -- game parameters

WALK_SPEED = 1
FALL_ACCEL = 0.15


# -- settings

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
    RENDER_MODE = 'plain'

if not 'DEFAULT_BRIGHTNESS' in dir():
    DEFAULT_BRIGHTNESS = None

# read settings from command line
parser = argparse.ArgumentParser(prog='Toolbox Hexagon')
parser.add_argument('--rendermode', default=None, help='possible modes: plain, led, wide, square, arcade')
args = parser.parse_args()

if args.rendermode:
    RENDER_MODE = args.rendermode

if DEFAULT_BRIGHTNESS is None:
    if RENDER_MODE == 'led':
        DEFAULT_BRIGHTNESS = -4
    else:
        DEFAULT_BRIGHTNESS = 0

DEADZONE = 0.4


# -- LED WALL initialization stuff
output = ledwall.initScreen(RENDER_MODE)
ledwall.setBrightnessValue(DEFAULT_BRIGHTNESS)


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

tiles = {'#': pygame.image.load('gfx/platform.png')
         }


level = ['                ',
         '                ',
         '                ',
         '                ',
         '                ',
         '##    ####    ##',
         '                ',
         '                ',
         '   ##      ##   ',
         '                ',
         '                ',
         '####        ####',
         '                ',
         '                ',
         '      ####      ',
         '                ',
         '  ###      ###  ',
         '                ',
         '                ',
         '#######  #######',
         ]

LEV_W = len(level[0])
LEV_H = len(level)


PLAYER_KEYS = [(pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP),
               (pygame.K_d, pygame.K_a, pygame.K_s, pygame.K_w),
               ]

RIGHT = 0
LEFT = 1
DOWN = 2
UP = 3


class Player:
    def __init__(self, x, y, number):
        self.x = x
        self.y = y

        self.prev_y = y

        self.xdir = 0
        self.ydir = 0

        self.facedir = 'left'       # 'left' or 'right'

        self.number = number
        self.state = 'pumpkin'      # 'pumpkin' or 'ghost

    def draw(self, output):
        key = '%s%i %s' % (self.state[0], self.number, self.facedir)
        sprite = sprites[key]
        output.blit(sprite, (self.x, self.y))

    def moveLeft(self):
        self.xdir = -1
        self.facedir = 'left'

    def stopLeft(self):
        if self.xdir < 0:
            self.xdir = 0

    def moveRight(self):
        self.xdir = 1
        self.facedir = 'right'

    def stopRight(self):
        if self.xdir > 0:
            self.xdir = 0

    def update(self):
        self.x += self.xdir * WALK_SPEED
        self.y += self.ydir * WALK_SPEED

        # -- gravity check

        # get current tile
        cx = int(self.x + 8) // 16
        cy = int(self.y + 16) // 16

        # get previous tile for double-check
        px = int(self.x + 8) // 16
        py = int(self.prev_y + 16) // 16

        # save old y for next frame
        self.prev_y = self.y

        if cy < LEV_H:
            # check if player is colliding with a floor
            if level[cy][cx] == ' ':
                # no collision - fall down...
                self.ydir += FALL_ACCEL
                if self.ydir >= 4:
                    self.ydir = 4
            else:
                # collision
                # check if player was still above the floor in last update
                if level[py][px] == ' ':
                    # stop falling
                    self.ydir = 0
                    # clamp to floor
                    self.y = (cy -1) * 16
                else:
                    # player was already in floor tile -> keep falling...                    # no collision - fall down...
                    if int(self.y) != self.y:   # ...but only if not exactly on the edge!
                        self.ydir += FALL_ACCEL
                        if self.ydir >= 4:
                            self.ydir = 4
        
        # -- fall through screen border
        if self.y > ledwall.SCR_H + 16:
            self.y = -16


class Game:
    def __init__(self):
        self.player1 = Player(48, 240, 1)
        self.player2 = Player(ledwall.SCR_W - 48 - 16, 240, 2)

        self.player1.facedir = 'right'
        self.player2.facedir = 'left'

        self.players = [self.player1, self.player2]

    def render(self):
        for y in range(LEV_H):
            for x in range(LEV_W):
                tile = level[y][x]
                if tile in tiles:
                    output.blit(tiles[tile], (x * 16, y * 16))

        self.player1.draw(output)
        self.player2.draw(output)

    def update(self):
        for player in self.players:
            player.update()

    def keyPress(self, key):
        for i in range(2):
            if key == PLAYER_KEYS[i][LEFT]:
                self.players[i].moveLeft()
            elif key == PLAYER_KEYS[i][RIGHT]:
                self.players[i].moveRight()

    def keyRelease(self, key):
        for i in range(2):
            if key == PLAYER_KEYS[i][LEFT]:
                self.players[i].stopLeft()
            elif key == PLAYER_KEYS[i][RIGHT]:
                self.players[i].stopRight()


class Application:
    def __init__(self):
        self.running = True

        self.game = Game()

    def render(self):
        output.fill((0, 0, 0))

        self.game.render()

        ledwall.compose()

    def controls(self):
        global BRIGHTNESS

        events = pygame.event.get()

        for e in events:
            if e.type==pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False

                elif e.key == pygame.K_F1:
                    BRIGHTNESS -= 1
                    ledwall.setBrightnessValue(BRIGHTNESS)
                    
                elif e.key == pygame.K_F2:
                    BRIGHTNESS = min(BRIGHTNESS + 1, 0)
                    ledwall.setBrightnessValue(BRIGHTNESS)
                    
                elif e.key == pygame.K_F5:
                    ledwall.enableOverlay(not ledwall.showOverlay)
                elif e.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

                else:
                    self.game.keyPress(e.key)
            elif e.type == pygame.KEYUP:
                self.game.keyRelease(e.key)
                        


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
