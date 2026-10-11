import pygame
import pygame._sdl2.controller
import argparse
import time
import random

import ledwall


# -- game parameters

WALK_SPEED = 1
FALL_ACCEL = 0.15
FLY_ACCEL  = 0.1
FLY_MAXSPEED = 1.5
SHOT_SPEED = 8
WIN_SCORE = 1


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

if not 'DEBUG' in dir():
    DEBUG = False

# read settings from command line
parser = argparse.ArgumentParser(prog='Pumpkin Pit')
parser.add_argument('--rendermode', default=None, help='possible modes: plain, led, wide, square, arcade')
parser.add_argument('--debug', default=False, help='enter debug mode')
args = parser.parse_args()

if args.rendermode:
    RENDER_MODE = args.rendermode

if DEFAULT_BRIGHTNESS is None:
    if RENDER_MODE == 'led':
        DEFAULT_BRIGHTNESS = -4
    else:
        DEFAULT_BRIGHTNESS = 0

if args.debug:
    DEBUG = args.debug

if DEBUG:
    print = ledwall.print


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

DEADZONE = 0.4


# -- graphic resources

sprites = {'p1 left': pygame.image.load('gfx/pumpkin1-left.png'),
           'p1 right': pygame.image.load('gfx/pumpkin1-right.png'),
           'p2 left': pygame.image.load('gfx/pumpkin2-left.png'),
           'p2 right': pygame.image.load('gfx/pumpkin2-right.png'),
           'g1_1 left': pygame.image.load('gfx/ghost1_left_1.png'),
           'g1_1 right': pygame.transform.flip(pygame.image.load('gfx/ghost1_left_1.png'),True, False),
           'g2_1 left': pygame.image.load('gfx/ghost1_left_2.png'),
           'g2_1 right': pygame.transform.flip(pygame.image.load('gfx/ghost1_left_2.png'),True, False),
           'g3_1 left': pygame.image.load('gfx/ghost1_left_3.png'),
           'g3_1 right': pygame.transform.flip(pygame.image.load('gfx/ghost1_left_3.png'),True, False),
           'g4_1 left': pygame.image.load('gfx/ghost1_left_4.png'),
           'g4_1 right': pygame.transform.flip(pygame.image.load('gfx/ghost1_left_4.png'),True, False),
           'g5_1 left': pygame.image.load('gfx/ghost1_left_5.png'),
           'g5_1 right': pygame.transform.flip(pygame.image.load('gfx/ghost1_left_5.png'),True, False),
           'g1_2 left': pygame.image.load('gfx/ghost2_left_1.png'),
           'g1_2 right': pygame.transform.flip(pygame.image.load('gfx/ghost2_left_1.png'),True, False),
           'g2_2 left': pygame.image.load('gfx/ghost2_left_2.png'),
           'g2_2 right': pygame.transform.flip(pygame.image.load('gfx/ghost2_left_2.png'),True, False),
           'g3_2 left': pygame.image.load('gfx/ghost2_left_3.png'),
           'g3_2 right': pygame.transform.flip(pygame.image.load('gfx/ghost2_left_3.png'),True, False),
           'g4_2 left': pygame.image.load('gfx/ghost2_left_4.png'),
           'g4_2 right': pygame.transform.flip(pygame.image.load('gfx/ghost2_left_4.png'),True, False),
           'g5_2 left': pygame.image.load('gfx/ghost2_left_5.png'),
           'g5_2 right': pygame.transform.flip(pygame.image.load('gfx/ghost2_left_5.png'),True, False),
           'shot': pygame.image.load('gfx/shot.png'),
           'dead': pygame.image.load('gfx/dead.png'),
           }

tiles = {'#': pygame.image.load('gfx/platform.png'),
         '&': pygame.image.load('gfx/magic-potion.png'),
         'o': pygame.image.load('gfx/ammo.png'),
         }


# -- level stuff

level_1 = ['                ',
           '                ',
           '                ',
           'o              o',
           '##    ####    ##',
           '                ',
           '                ',
           '   ##      ##   ',
           '                ',
           ' &            & ',
           '####        ####',
           '                ',
           '      o  o      ',
           '      ####      ',
           '                ',
           '  ###      ###  ',
           '                ',
           '                ',
           '######    ######',
           '                ',
           ]

level_2 =['                ',
          '                ',
          '                ',
          '       oo       ',
          '###    ##    ###',
          '                ',
          '     &    &     ',
          '   ##########   ',
          '                ',
          '                ',
          '####        ####',
          '                ',
          '                ',
          '                ',
          '       oo       ',
          '   ### ## ###   ',
          '                ',
          '                ',
          '  ## ####### ## ',
          '                ',
          ]

level_3 = ['                ',
         '                ',
         '                ',
         '                ',
         '##    ####    ##',
         '                ',
         '    o      o    ',
         '   ##      ##   ',
         '                ',
         '                ',
         '#######  #######',
         '                ',
         'o      &       o',
         '#     ####     #',
         '                ',
         ' ###        ### ',
         '                ',
         '                ',
         '#####      #####',
         '                ',
         ]

levels = [level_1, level_2, level_3]
level = []

def initLevel(number):
    level.clear()

    for line in levels[number]:
        level.append(line)

levelnumber = -1

LEV_W = len(level_1[0])
LEV_H = len(level_1)

def setLevelTile(x, y, tile):
    level[y] = level[y][:x] + tile + level[y][x+1:]

def findFreeRandomSpot():
    while True:
        y = int(random.random() * LEV_H)
        if '#' in level[y]:
            while True:
                x = int(random.random() * LEV_W)
                if level[y][x] == '#':
                    if level[y -1][x] == ' ':
                        return x, y -1

# -- sound stuff

pygame.mixer.init()

sounds = {'pickup_01': pygame.mixer.Sound('sfx/pickup_01.wav'),
          'pickup_02': pygame.mixer.Sound('sfx/pickup_02.wav'),
          'pickup_03': pygame.mixer.Sound('sfx/pickup_03.wav'),
          'ghost_01': pygame.mixer.Sound('sfx/ghost_01.wav'),
          'intro_01': pygame.mixer.Sound('sfx/intro_01.wav'),
          'walking_bg': pygame.mixer.Sound('sfx/walking_bg.wav'),
          'spawn_ammo': pygame.mixer.Sound('sfx/spawn_ammo.wav'),
          'shoot_01': pygame.mixer.Sound('sfx/shoot_01.wav'),
          'hit_02': pygame.mixer.Sound('sfx/hit_02.wav'),
          'event_01': pygame.mixer.Sound('sfx/event_01s.wav'),
          'event_03': pygame.mixer.Sound('sfx/event_03.wav'),
          'event_04': pygame.mixer.Sound('sfx/event_04.wav')}


pygame.mixer.music.load('sfx/grumblin_01l.wav')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(loops=-1)


# -- constants and stuff

PLAYER_KEYS = [(pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP, pygame.K_RCTRL),
               (pygame.K_d, pygame.K_a, pygame.K_s, pygame.K_w, pygame.K_TAB),
               ]

clock = pygame.time.Clock()
tick = 0

RIGHT = 0
LEFT = 1
DOWN = 2
UP = 3
SHOOT = 4

events = []
timers = []
shots = []

def createTimer(name, timeout):
    timer = Timer(name, timeout)
    timers.append(timer)


# -- the actual game code
class Timer:
    def __init__(self, name, timeout):
        self.name = name
        self.timeout = timeout
        self.count = 0

    def update(self):
        self.count += 1

    def isDue(self):
        if self.count >= self.timeout:
            return True
        
        return False
    
    def reset(self):
        self.count = 0


class Shot:
    def __init__(self, x, y, xdir, firestarter):
        self.x = x
        self.y = y
        self.xdir = xdir

        self.firestarter = firestarter

    def draw(self, output):
        output.blit(sprites['shot'], (self.x, self.y))

    def update(self):
        self.x += self.xdir * SHOT_SPEED

    def checkCollision(self, player):
        if player.state in ('dead', 'dying'):
            return

        if self.x > player.x -6 and self.x < player.x + 16 -6:
            if self.y > player.y -4 and self.y < player.y + 16 -4:
                if player.getHit():
                    self.firestarter.getPoint()
                if player.state == 'pumpkin':
                    sounds['event_04'].play()
                else:
                    sounds['hit_02'].play()


class Player:
    def __init__(self, x, y, number):
        self.x = x
        self.y = y

        self.startx = x
        self.starty = y

        self.prev_y = y

        self.xdir = 0
        self.ydir = 0
        self.xspeed = 0
        self.yspeed = 0

        self.ground = True
        self.roll = 0

        self.facedir = 'left'       # 'left' or 'right'

        self.number = number
        self.state = 'pumpkin'      # 'pumpkin' or 'ghost', 'dying' or 'dead'

        self.score = 0
        self.ammo = 0

        self.blink = True
        timers.append(Timer('PLAYER %s STOP BLINKING' % self.number, 30))

    def draw(self, output):
        if self.blink:
            if tick % 16 < 8:
                return

        if self.state == 'dying':
            key = 'dead'
        elif self.state == 'dead':
            return
        else:
            key = '%s%i %s' % (self.state[0], self.number, self.facedir)

        if self.state == 'ghost'and self.number == 1:
            if tick % 32 < 8:
                key = 'g1_1 %s' %(self.facedir)
            elif tick % 32 < 14:
                key = 'g2_1 %s' %(self.facedir)
            elif tick % 32 < 22:
                key = 'g3_1 %s' %(self.facedir)
            elif tick % 32 < 30:
                key = 'g4_1 %s' %(self.facedir)
            else:
                key = 'g5_1 %s' %(self.facedir)

        elif self.state == 'ghost' and self.number == 2:
            if tick % 32 < 8:
                key = 'g1_2 %s' %(self.facedir)
            elif tick % 32 < 14:
                key = 'g2_2 %s' %(self.facedir)
            elif tick % 32 < 22:
                key = 'g3_2 %s' %(self.facedir)
            elif tick % 32 < 30:
                key = 'g4_2 %s' %(self.facedir)
            else:
                key = 'g5_2 %s' %(self.facedir)
        
        sprite = sprites[key]

        if self.state == 'pumpkin':
            sprite = pygame.transform.rotate(sprite, 90 * round(self.roll))

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
        if self.state == 'ghost':
            if self.ydir > 0:
                self.ydir = 0

    def shoot(self):
        if self.ammo == 0:
            return
        if self.state in ('dying', 'dead'):
            return

        self.ammo -= 1
        sounds['shoot_01'].play()
        
        shot = Shot(self.x, self.y, 1 if self.facedir == 'right' else -1, self)
        shots.append(shot)

    def becomeGhost(self):
        self.state = 'ghost'

        self.xspeed = 0
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

    def getHit(self):
        if self.blink:
            return False

        if self.state == 'ghost':
            self.state = 'pumpkin'
            self.blink = True
            timers.append(Timer('PLAYER %s STOP BLINKING' % self.number, 30))
            return False
        else:
            self.kill()
            return True

    def kill(self):
        self.state = 'dying'
        events.append('PLAYER %s DIED' % self.number)

    def respawn(self):
        self.x = self.startx
        self.y = self.starty
        self.state = 'pumpkin'
        self.ammo = 0

        self.blink = True
        timers.append(Timer('PLAYER %s STOP BLINKING' % self.number, 60))

    def getPoint(self):
        self.score += 1

        if self.score == WIN_SCORE:
            events.append('PLAYER %s WINS' % self.number)

    def update(self):
        if self.state in ('dying', 'dead'):
            return

        if self.ground:
            self.roll -= 0.15 * self.xdir
        if self.ydir < 0.0:
            self.roll = 0.0

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
                self.yspeed = -1
            else:
                self.yspeed = 0
        
        tempx += self.xspeed
        tempy += self.yspeed

        if tempx > ledwall.SCR_W - 16:
            tempx = ledwall.SCR_W - 16
        if tempx < 0:
            tempx = 0

        if self.state == 'ghost':
            if tempy > ledwall.SCR_H - 16:
                tempy = ledwall.SCR_H - 16
            if tempy < 0:
                tempy = 0

        self.x = tempx
        self.y = tempy

        # -- gravity check

        # get current tiles BELOW player
        cx1 = int(self.x + 3) // 16
        cx2 = int(self.x + 13) // 16
        cy = int(self.y + 16) // 16

        # get previous tile for double-check
        px1 = int(self.x + 3) // 16
        px2 = int(self.x + 13) // 16
        py = int(self.prev_y + 16) // 16

        # save old y for next frame
        self.prev_y = self.y

        if cy < LEV_H:

            # -- pumpkin movement (just walking)
            if self.state == 'pumpkin':
                # check if player is colliding with a floor
                if level[cy][cx1] != '#' and level[cy][cx2] != '#':
                    # no collision - fall down...
                    self.fallDown()
                else:
                    # collision
                    # check if player was still above the floor in last update
                    if level[py][px1] != '#' and level[py][px2] != '#':
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

            # -- check if player collects something

            # get current tile again, this time not BELOW player
            cx = int(self.x + 8) // 16
            cy = int(self.y + 8) // 16

            if level[cy][cx] == '&':
                # magic potion
                if self.state == 'pumpkin':
                    self.becomeGhost()
                else:
                    self.becomePumpkin()

                setLevelTile(cx, cy, ' ')

                events.append('MAGIC POTION COLLECTED')

            elif level[cy][cx] == 'o':
                # ammo
                sounds['pickup_03'].play()
                if self.ammo >= 5:
                    self.ammo = 5
                else:
                    self.ammo += 1
                setLevelTile(cx, cy, ' ')

                events.append('AMMO COLLECTED')
        
        # -- fall through screen border
        if self.y > ledwall.SCR_H + 16:
            self.y = -16


class Game:
    def __init__(self):
        self.player1 = Player(48, 224, 1)
        self.player2 = Player(ledwall.SCR_W - 48 - 16, 224, 2)

        self.player1.facedir = 'right'
        self.player2.facedir = 'left'

        self.players = [self.player1, self.player2]

        self.winner = None
        self.message = ''
        self.blank = False

        global levelnumber
        levelnumber += 1
        initLevel(levelnumber % len(levels))

    def render(self):
        if self.blank:
            output.fill((0, 0, 0))
            ledwall.drawText(self.message, 0, 11, (192, 255, 0), 1, center=True)
            return

        for y in range(LEV_H):
            for x in range(LEV_W):
                tile = level[y][x]
                if tile in tiles:
                    output.blit(tiles[tile], (x * 16, y * 16))

        self.player1.draw(output)
        self.player2.draw(output)

        for shot in shots:
            shot.draw(output)

        for i in range(self.player1.ammo):
            output.blit(sprites['shot'], (-4 + i * 8, 13))
        for i in range(self.player2.ammo):
            output.blit(sprites['shot'], (ledwall.SCR_W - 11 - i * 8, 13))

        #ledwall.drawText('PUMPKIN PIT', 0, 1, (192, 255, 0), 1, center=True)

        ledwall.drawText('%02i' % self.player1.score, x=0, y=1, color=(255, 255, 255))
        ledwall.drawText('%02i' % self.player2.score, x=ledwall.SCR_W // 8 - 2, y=1, color=(255, 255, 255))

        if tick % 32 > 8:
            ledwall.drawText(self.message, 0, 11, (192, 255, 0), 1, center=True)

    def update(self):
        if not self.winner:
            # -- update players
            for player in self.players:
                player.update()

            # -- update shots
            for shot in shots:
                shot.update()

                for player in self.players:
                    if player != shot.firestarter:
                        shot.checkCollision(player)

        # -- handle events
        for e in events:
            print(e)
            if e == 'MAGIC POTION COLLECTED':
                createTimer('SPAWN MAGIC POTION', 120)
            elif e == 'AMMO COLLECTED':
                createTimer('SPAWN AMMO', 120)

            elif e == 'SPAWN MAGIC POTION':
                sounds['event_03'].play()
                self.spawnMagicPotion()
            elif e == 'SPAWN AMMO':
                sounds['spawn_ammo'].play()
                self.spawnAmmo()

            elif e == 'PLAYER 1 DIED':
                createTimer('HIDE PLAYER 1', 30)
            elif e == 'PLAYER 2 DIED':
                createTimer('HIDE PLAYER 2', 30)

            elif e == 'HIDE PLAYER 1':
                self.player1.state = 'dead'
                createTimer('RESPAWN PLAYER 1', 90)
            elif e == 'HIDE PLAYER 2':
                self.player2.state = 'dead'
                createTimer('RESPAWN PLAYER 2', 90)

            elif e == 'RESPAWN PLAYER 1':
                self.player1.respawn()
            elif e == 'RESPAWN PLAYER 2':
                self.player2.respawn()

            elif e == 'PLAYER 1 STOP BLINKING':
                self.player1.blink = False
            elif e == 'PLAYER 2 STOP BLINKING':
                self.player2.blink = False

            elif e == 'PLAYER 1 WINS':
                self.setWinner(1)
            elif e == 'PLAYER 2 WINS':
                self.setWinner(2)

            elif e == 'SHOW WINNER':
                self.message = 'PLAYER %i WINS!' % self.winner
                createTimer('BLANK SCREEN', 180)
            elif e == 'BLANK SCREEN':
                self.blank = True
                createTimer('RESTART GAME', 60)
            elif e == 'RESTART GAME':
                self.restart()

        events.clear()

        # -- handle timers
        remove = []
        for t in timers:
            t.update()

            if t.isDue():
                events.append(t.name)
                remove.append(t)

        for r in remove:
            timers.remove(r)

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
            elif key == PLAYER_KEYS[i][SHOOT]:
                self.players[i].shoot()

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

    def controllerAxisMotion(self, p, axis, value):
        if axis == pygame.CONTROLLER_AXIS_LEFTX:
            print(p, value)
            if value < 0:
                if value < -DEADZONE:
                    self.players[p].moveLeft()
                else:
                    self.players[p].stopLeft()
            elif value > 0:
                if value > DEADZONE:
                    self.players[p].moveRight()
                else:
                    self.players[p].stopRight()
            else:
                self.players[p].stopLeft()
                self.players[p].stopRight()

        elif axis == pygame.CONTROLLER_AXIS_LEFTY:
            if value < 0:
                if value < -DEADZONE:
                    self.players[p].moveUp()
                else:
                    self.players[p].stopUp()
            elif value > 0:
                if value > DEADZONE:
                    self.players[p].moveDown()
                else:
                    self.players[p].stopDown()
            else:
                self.players[p].stopUp()
                self.players[p].stopDown()

    def controllerButtonPress(self, p, button):
        if button in (pygame.CONTROLLER_BUTTON_A, pygame.CONTROLLER_BUTTON_B, pygame.CONTROLLER_BUTTON_X, pygame.CONTROLLER_BUTTON_Y):
            self.players[p].shoot()

        elif button == pygame.CONTROLLER_BUTTON_DPAD_LEFT:
            self.players[p].moveLeft()
        elif button == pygame.CONTROLLER_BUTTON_DPAD_RIGHT:
            self.players[p].moveRight()
        elif button == pygame.CONTROLLER_BUTTON_DPAD_UP:
            self.players[p].moveUp()
        elif button == pygame.CONTROLLER_BUTTON_DPAD_DOWN:
            self.players[p].moveDown()


    def controllerButtonRelease(self, p, button):
        if button == pygame.CONTROLLER_BUTTON_DPAD_LEFT:
            self.players[p].stopLeft()
        elif button == pygame.CONTROLLER_BUTTON_DPAD_RIGHT:
            self.players[p].stopRight()
        elif button == pygame.CONTROLLER_BUTTON_DPAD_UP:
            self.players[p].stopUp()
        elif button == pygame.CONTROLLER_BUTTON_DPAD_DOWN:
            self.players[p].stopDown()
    
    def spawnMagicPotion(self):
        x, y = findFreeRandomSpot()
        setLevelTile(x, y, '&')

    def spawnAmmo(self):
        x, y = findFreeRandomSpot()
        setLevelTile(x, y, 'o')

    def setWinner(self, number):
        self.winner = number
        
        shots.clear()
        events.clear()
        timers.clear()
        
        createTimer('SHOW WINNER', 60)

    def restart(self):
        self.__init__()


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

            elif e.type == pygame.CONTROLLERAXISMOTION and joymode == 'controller':
                value = max(-1, e.value / 32767)
                p = e.instance_id
                self.game.controllerAxisMotion(p, e.axis, value)

            elif e.type == pygame.CONTROLLERBUTTONDOWN and joymode == 'controller':
                p = e.instance_id
                self.game.controllerButtonPress(p, e.button)

            elif e.type == pygame.CONTROLLERBUTTONUP and joymode == 'controller':
                p = e.instance_id
                self.game.controllerButtonRelease(p, e.button)


    def update(self):
        self.game.update()


app = Application()

while app.running:
    app.render()
    app.controls()
    app.update()

    clock.tick(60)
    tick += 1

    if tick % 60 * 4 == 0:
        ledwall.cls()
