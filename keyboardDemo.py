import pygame
import serial
import sys, glob
from pygame.gfxdraw import aacircle
from keyboardClass import rewireKeyboard
import numpy as np

def draw_filled_aacircle(screen, radius, color, xpos, ypos):
    pygame.gfxdraw.filled_circle(screen,
                                 int(xpos),
                                 int(ypos),
                                 int(radius),
                                 color)
    pygame.gfxdraw.aacircle(screen,
                            int(xpos),
                            int(ypos),
                            int(radius),
                            color)

class testGame(object):

    def __init__(self, max_key_force=0.5):
        # initialize pygame and graphics
        pygame.init()
        self.pygame_keyboard = pygame.joystick.Joystick(0)
        self.clock = pygame.time.Clock()
        self.FRAME_RATE = 60
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 800, 800
        # keyboard must be declared BEFORE screen initialized
        self.keyboard = rewireKeyboard(self.pygame_keyboard)
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.BG_COLOR = 40,40,40
        self.KEY_BG_COLOR = 100,100,100
        self.KEY_FORCE_COLOR = 150,150,150
        self.KEY_DOWN_COLOR = 40,150,40
        self.KEY_BAD_COLOR = 150,40,40
        self.KEY_MIN_DIAMETER = 0.025*self.SCREEN_HEIGHT
        self.KEY_MAX_DIAMETER = 0.15*self.SCREEN_HEIGHT
        self.KEY_DIAMETER_RANGE = self.KEY_MAX_DIAMETER-self.KEY_MIN_DIAMETER
        self.KEY_OUTLINE_SIZE = 0.0075*self.SCREEN_HEIGHT

        # force logic
        self.max_key_force = max_key_force
        self.min_key_force = 0.015
        self.target_key_force = 0.3
        self.force_scaling_powers = [.5, .75, .9, 1, 1.5]
        self.force_scaling_power = self.force_scaling_powers[1]

    def check_input(self):
        self.keyboard.update_inputs()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.quit()
                if event.key == pygame.K_a: self.keyboard.send_stimulus('0P0')
                if event.key == pygame.K_b: self.keyboard.send_stimulus('1P0')
                if event.key == pygame.K_c: self.keyboard.send_stimulus('2P0')
                if event.key == pygame.K_z: self.keyboard.set_zero_force()
                if event.key == pygame.K_f:
                    self.force_scaling_powers = np.roll(self.force_scaling_powers,-1)
                    self.force_scaling_power = self.force_scaling_powers[0]
            elif event.type == pygame.KEYUP:
                pass

    def run(self):
        while True:
            time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)
            self.check_input()
            self.draw_background()
            for key in range(4):
                self.draw_key(key,0.2*self.SCREEN_WIDTH*(key-1.5))
            pygame.display.flip()

    def draw_key(self,key_num,xpos):
        draw_filled_aacircle(self.screen,
            0.5*self.KEY_MAX_DIAMETER+self.KEY_OUTLINE_SIZE,
            self.KEY_BG_COLOR,
            .5*self.SCREEN_WIDTH+xpos,
            0.5*self.SCREEN_HEIGHT)
        draw_filled_aacircle(self.screen,
            0.5*self.KEY_MAX_DIAMETER,
            self.BG_COLOR,
            .5*self.SCREEN_WIDTH+xpos,
            0.5*self.SCREEN_HEIGHT)

        display_ratio = self.keyboard.force[key_num]/self.max_key_force
        display_ratio = np.power(max(0,display_ratio), self.force_scaling_power)
        key_size = 0.5*display_ratio*self.KEY_DIAMETER_RANGE
        key_size = 0.5*self.KEY_MIN_DIAMETER+key_size
        key_size = max(0.5*self.KEY_MIN_DIAMETER,min(key_size,0.5*self.KEY_MAX_DIAMETER))
        if self.keyboard.force[key_num] < self.min_key_force:
            key_color = self.KEY_BAD_COLOR
        elif self.keyboard.force[key_num] > self.target_key_force:
            key_color = self.KEY_DOWN_COLOR
        else:
            key_color = self.KEY_FORCE_COLOR
        draw_filled_aacircle(self.screen,
            key_size,
            key_color,
            .5*self.SCREEN_WIDTH+xpos,
            0.5*self.SCREEN_HEIGHT)

    def draw_background(self):
        self.screen.fill(self.BG_COLOR)

    def quit(self):
        sys.exit()

if __name__ == "__main__":
    game = testGame()
    game.run()
