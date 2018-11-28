import pygame
import serial
import sys, glob
from keyboardClass import rewireKeyboard

class testGame(object):

    def __init__(self, max_key_force=2.):
        # initialize pygame and graphics
        pygame.init()
        self.max_key_force = max_key_force
        self.pygame_keyboard = pygame.joystick.Joystick(0)
        self.clock = pygame.time.Clock()
        self.FRAME_RATE = 60
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 800, 800
        # keyboard must be declared BEFORE screen initialized
        self.keyboard = rewireKeyboard(self.pygame_keyboard)
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.BG_COLOR = 40,40,40
        self.KEY_BG_COLOR = 20,20,20
        self.KEY_FORCE_COLOR = 150,150,150
        self.KEY_DOWN_COLOR = 40,150,40
        self.KEY_HEIGHT = 0.8*self.SCREEN_HEIGHT
        self.KEY_WIDTH = 0.15*self.SCREEN_HEIGHT
        self.KEY_PRESS_WIDTH = 0.025*self.SCREEN_HEIGHT

    def check_input(self):
        self.keyboard.update_inputs()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.quit()
                if event.key == pygame.K_a: self.teensy.write('00')
                if event.key == pygame.K_b: self.teensy.write('10')
                if event.key == pygame.K_c: self.teensy.write('20')
                if event.key == pygame.K_z: self.keyboard.set_zero_force()
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
        if self.keyboard.keydown[key_num]:
            draw_center_rect(self.screen,
                         self.KEY_WIDTH+self.KEY_PRESS_WIDTH,
                         self.KEY_HEIGHT+self.KEY_PRESS_WIDTH,
                         self.KEY_DOWN_COLOR,
                         .5*self.SCREEN_WIDTH+xpos,
                         0.5*self.SCREEN_HEIGHT)
        draw_center_rect(self.screen,
                     self.KEY_WIDTH,
                     self.KEY_HEIGHT,
                     self.KEY_BG_COLOR,
                     .5*self.SCREEN_WIDTH+xpos,
                     0.5*self.SCREEN_HEIGHT)
        draw_bottom_rect(self.screen,
             self.KEY_WIDTH,
             # self.keyboard.force_ratio[key_num]*self.KEY_HEIGHT,
             self.keyboard.force[key_num]/self.max_key_force*self.KEY_HEIGHT,
             self.KEY_FORCE_COLOR,
             .5*self.SCREEN_WIDTH+xpos,
             0.5*self.SCREEN_HEIGHT+0.5*self.KEY_HEIGHT) 

    def draw_background(self):
        self.screen.fill(self.BG_COLOR)

    def quit(self):
        sys.exit()

def draw_center_rect(screen, width, height, color, xpos, ypos):
    rect = pygame.Rect(xpos-0.5*width,
                       ypos-0.5*height,
                       width,
                       height)
    pygame.draw.rect(screen, color, rect)        

def draw_bottom_rect(screen, width, height, color, xpos, ypos):
    rect = pygame.Rect(xpos-0.5*width,
                       ypos,
                       width,
                       height)
    rect.bottom = ypos
    pygame.draw.rect(screen, color, rect)        

if __name__ == "__main__":
    game = testGame()
    game.run()
