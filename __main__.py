import pygame
import pygame._sdl2.controller
import time

import ledwall
print = ledwall.print



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

running = True
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


clock = pygame.time.Clock()
tick = 0


class Application:
    def __init__(self):
        self.running = True

    def render(self):
        output.fill((0, 0, 0))
        ledwall.compose()

    def controls(self):
        events = pygame.event.get()

        for e in events:
            if e.type==pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        pass


app = Application()

while app.running:
    app.render()
    app.controls()
    app.update()

    clock.tick(60)
    tick += 1

    if tick >= 60 * 4:
        ledwall.cls()
