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
FLY_ACCEL  = 0.1
FLY_MAXSPEED = 1.5


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
parser = argparse.ArgumentParser(prog='Pumpkin Pit')
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

tiles = {'#': pygame.image.load('gfx/platform.png'),
         '&': pygame.image.load('gfx/magic-potion.png'),
         'o': pygame.image.load('gfx/ammo.png'),
         }


level = ['                ',
         '                ',
         '                ',
         '                ',
         '##    ####    ##',
         '                ',
         '                ',
         '   ##      ##   ',
         '                ',
         ' &            & ',
         '####        ####',
         '                ',
         '                ',
         '      ####      ',
         '   o        o   ',
         '  ###      ###  ',
         '                ',
         '                ',
         '#######  #######',
         '                ',
         ]

LEV_W = len(level[0])
LEV_H = len(level)



pygame.mixer.init()

sounds = {'pickup_01': pygame.mixer.Sound('sfx/pickup_01.wav'),
          'pickup_02': pygame.mixer.Sound('sfx/pickup_02.wav'),
          'pickup_03': pygame.mixer.Sound('sfx/pickup_03.wav'),
          'ghost_01': pygame.mixer.Sound('sfx/ghost_01.wav'),
          'intro_01': pygame.mixer.Sound('sfx/intro_01.wav'),
          'walking_bg': pygame.mixer.Sound('sfx/walking_bg.wav'),
          'event_01': pygame.mixer.Sound('sfx/event_01s.wav'),
          'event_04': pygame.mixer.Sound('sfx/event_04.wav')}


pygame.mixer.music.load('sfx/grumblin_01l.wav')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(loops=-1)


PLAYER_KEYS = [(pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP),
               (pygame.K_d, pygame.K_a, pygame.K_s, pygame.K_w),
               ]

RIGHT = 0
LEFT = 1
DOWN = 2
UP = 3

def setLevelTile(x, y, tile):
    level[y] = level[y][:x] + tile + level[y][x+1:]


class Player:
    def __init__(self, x, y, number):
        self.x = x
        self.y = y

        self.prev_y = y

        self.xdir = 0
        self.ydir = 0
        self.xspeed = 0
        self.yspeed = 0

        self.ground = False

        self.facedir = 'left'       # 'left' or 'right'

        self.number = number
        self.state = 'pumpkin'      # 'pumpkin' or 'ghost'

        self.ammo = 0

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

    def moveUp(self):
        if self.state == 'pumpkin':
            if not self.ground:
                return
        self.ydir = -1

    def stopUp(self):
        if self.ydir < 0:
            self.ydir = 0

    def moveDown(self):
        if self.state == 'ghost':
            self.ydir = 1

    def stopDown(self):
        if self.ydir > 0:
            self.ydir = 0

    def becomeGhost(self):
        self.state = 'ghost'

        self.ydir = 0
        self.yspeed = 0

        sounds['pickup_02'].play()

    def becomePumpkin(self):
        self.state = 'pumpkin'

        self.ydir = 0
        self.yspeed = 0

        sounds['event_04'].play()

    def fallDown(self):
        self.ydir = 1
        self.yspeed += FALL_ACCEL
        if self.yspeed >= 4:
            self.yspeed = 4

        self.ground = False

    def update(self):
        tempx = self.x
        tempy = self.y

        if self.state == 'ghost':
            if self.xdir > 0 and self.xspeed < FLY_MAXSPEED:
                self.xspeed += FLY_ACCEL
            if self.xdir < 0 and self.xspeed > -FLY_MAXSPEED:
                self.xspeed -= FLY_ACCEL
            if self.ydir > 0 and self.yspeed < FLY_MAXSPEED:
                self.yspeed += FLY_ACCEL
            if self.ydir < 0 and self.yspeed > -FLY_MAXSPEED:
                self.yspeed -= FLY_ACCEL
        else:
            if self.xdir > 0:
                self.xspeed = WALK_SPEED
            elif self.xdir < 0:
                self.xspeed = -WALK_SPEED
            else:
                self.xspeed = 0

            if self.ydir > 0:
                pass
            elif self.ydir < 0:
                pass
            else:
                self.yspeed = 0
        
        tempx += self.xspeed
        tempy += self.yspeed

        if tempx > ledwall.SCR_W - 16:
            tempx = ledwall.SCR_W - 16
        if tempx < 0:
            tempx = 0

        self.x = tempx
        self.y = tempy

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

            # -- pumpkin movement (just walking)
            if self.state == 'pumpkin':
                # check if player is colliding with a floor
                if level[cy][cx] != '#':
                    # no collision - fall down...
                    self.fallDown()
                else:
                    # collision
                    # check if player was still above the floor in last update
                    if level[py][px] != '#':
                        # stop falling
                        self.ydir = 0
                        # clamp to floor
                        self.y = (cy -1) * 16
                        self.ground = True
                    else:
                        # player was already in floor tile -> keep falling...                    # no collision - fall down...
                        if int(self.y) != self.y:   # ...but only if not exactly on the edge!
                            self.fallDown()

            # -- ghost movement (flying)

            elif self.state == 'ghost':
                pass

            # check if player collects something
            if level[cy][cx] == '&':
                # magic potion
                if self.state == 'pumpkin':
                    self.becomeGhost()
                else:
                    self.becomePumpkin()

                setLevelTile(cx, cy, ' ')

            elif level[cy][cx] == 'o':
                # ammo
                sounds['pickup_03'].play()
                self.ammo += 1
                setLevelTile(cx, cy, ' ')
        
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

        ledwall.drawText('PUMPKIN PIT', 0, 1, (192, 255, 0), 1, center=True)

    def update(self):
        for player in self.players:
            player.update()

    def keyPress(self, key):
        for i in range(2):
            if key == PLAYER_KEYS[i][LEFT]:
                self.players[i].moveLeft()
            elif key == PLAYER_KEYS[i][RIGHT]:
                self.players[i].moveRight()
            elif key == PLAYER_KEYS[i][UP]:
                self.players[i].moveUp()
            elif key == PLAYER_KEYS[i][DOWN]:
                self.players[i].moveDown()

    def keyRelease(self, key):
        for i in range(2):
            if key == PLAYER_KEYS[i][LEFT]:
                self.players[i].stopLeft()
            elif key == PLAYER_KEYS[i][RIGHT]:
                self.players[i].stopRight()
            elif key == PLAYER_KEYS[i][UP]:
                self.players[i].stopUp()
            elif key == PLAYER_KEYS[i][DOWN]:
                self.players[i].stopDown()


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
