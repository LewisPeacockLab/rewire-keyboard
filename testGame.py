import pygame
import sys

class testGame(object):

    def __init__(self):
        # initialize pygame and graphics
        pygame.init()
        self.force_keyboard = pygame.joystick.Joystick(0)
        self.force_keyboard.init()
        self.clock = pygame.time.Clock()
        self.FRAME_RATE = 60
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 800, 800
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.BG_COLOR = 40,40,40
        self.KEY_BG_COLOR = 20,20,20
        self.KEY_FORCE_COLOR = 150,150,150
        self.KEY_DOWN_COLOR = 40,150,40
        self.KEY_HEIGHT = 0.8*self.SCREEN_HEIGHT
        self.KEY_WIDTH = 0.2*self.SCREEN_HEIGHT
        self.KEY_PRESS_WIDTH = 0.05*self.SCREEN_HEIGHT

        # initialize logic
        self.keydown = False
        self.force_ratio = 0

    def check_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: self.keydown = True
                elif event.key == pygame.K_ESCAPE: self.quit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_1: self.keydown = False
        self.force_ratio = max(0,min(.5*(1+self.force_keyboard.get_axis(0)),1))

    def run(self):
        while True:
            time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)
            self.check_input()
            self.draw_background()
            self.draw_key()
            pygame.display.flip()

    def draw_key(self):
        if self.keydown:
            draw_center_rect(self.screen,
                         self.KEY_WIDTH+self.KEY_PRESS_WIDTH,
                         self.KEY_HEIGHT+self.KEY_PRESS_WIDTH,
                         self.KEY_DOWN_COLOR,
                         .5*self.SCREEN_WIDTH,
                         0.5*self.SCREEN_HEIGHT)
        draw_center_rect(self.screen,
                     self.KEY_WIDTH,
                     self.KEY_HEIGHT,
                     self.KEY_BG_COLOR,
                     .5*self.SCREEN_WIDTH,
                     0.5*self.SCREEN_HEIGHT)
        draw_bottom_rect(self.screen,
             self.KEY_WIDTH,
             self.force_ratio*self.KEY_HEIGHT,
             self.KEY_FORCE_COLOR,
             .5*self.SCREEN_WIDTH,
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
