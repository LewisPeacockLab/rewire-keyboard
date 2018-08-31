import pygame
from pygame.gfxdraw import aacircle
import sys
import numpy as np

class neurofeedbackGame(object):

    def __init__(self):
        # initialize pygame and graphics
        pygame.init()
        self.clock = pygame.time.Clock()
        self.FRAME_RATE = 60
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 800, 800
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.BG_COLOR = 40,40,40
        self.KEY_BG_COLOR = 20,20,20
        self.KEY_ELECTRIC_COLOR = 60,150,150
        self.KEY_BLOOD_COLOR = 150,60,60
        self.KEY_FORCE_COLOR = 150,150,150
        self.KEY_DOWN_COLOR = 40,150,40
        self.KEY_HEIGHT = 0.7*self.SCREEN_HEIGHT
        self.KEY_WIDTH = 0.125*self.SCREEN_HEIGHT
        self.KEY_SPACING = 1.25*self.KEY_WIDTH
        self.KEY_XPOS = [-2*self.KEY_SPACING,-self.KEY_SPACING,0,self.KEY_SPACING,2*self.KEY_SPACING]
        self.HRF = 0.6*gen_hrf()
        self.MIN_ACTIVITY = 0.2
        self.NOISE_VAR = 0.05
        self.MAX_COUNT = 250.

        # initialize logic
        self.keydown = [False,False,False,False,False]
        self.neural_activity = [0,0,0,0,0]
        self.blood_flow_current = np.zeros((5,1))
        self.blood_flow_last = np.zeros((5,1))
        self.neural_activity_history = np.zeros((5,120))
        self.mode = 'electric'
        self.counter = 0

    def check_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d: self.keydown[0] = True
                if event.key == pygame.K_r: self.keydown[1] = True
                if event.key == pygame.K_t: self.keydown[2] = True
                if event.key == pygame.K_y: self.keydown[3] = True
                if event.key == pygame.K_m: self.keydown[4] = True
                if event.key == pygame.K_SPACE:
                    if self.mode == 'electric':
                        self.mode = 'blood'
                    elif self.mode == 'blood':
                        self.mode = 'electric'
                elif event.key == pygame.K_ESCAPE: self.quit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_d: self.keydown[0] = False
                if event.key == pygame.K_r: self.keydown[1] = False
                if event.key == pygame.K_t: self.keydown[2] = False
                if event.key == pygame.K_y: self.keydown[3] = False
                if event.key == pygame.K_m: self.keydown[4] = False

    def run(self):
        while True:
            time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)
            self.check_input()
            self.counter = self.counter + time_passed
            if self.counter > self.MAX_COUNT:
                self.counter = self.counter - self.MAX_COUNT

                new_neural_activity = (self.MIN_ACTIVITY+0.6*np.array(self.keydown)
                    +np.random.normal(0,self.NOISE_VAR,5))

                self.blood_flow_last = np.matmul(self.neural_activity_history,self.HRF)
                self.neural_activity_history = np.roll(self.neural_activity_history,1)
                self.neural_activity_history[:,0] = new_neural_activity
                self.blood_flow_current = np.matmul(self.neural_activity_history,self.HRF)

            continue_ratio = max(0,min(1,self.counter/self.MAX_COUNT))
            if self.mode == 'electric':
                self.neural_activity = continue_ratio*self.neural_activity_history[:,0]+(1-continue_ratio)*self.neural_activity_history[:,1]
            elif self.mode == 'blood':
                self.neural_activity = continue_ratio*self.blood_flow_current+(1-continue_ratio)*self.blood_flow_last

            self.draw_background()
            for key in range(5):
                self.draw_key(self.KEY_XPOS[key],self.keydown[key],self.neural_activity[key])
            pygame.display.flip()

    def draw_key(self, xpos, keydown, activity):
        draw_center_rect(self.screen,
                     self.KEY_WIDTH,
                     self.KEY_HEIGHT,
                     self.KEY_BG_COLOR,
                     .5*self.SCREEN_WIDTH+xpos,
                     0.5*self.SCREEN_HEIGHT-.5*self.KEY_WIDTH)
        if self.mode == 'electric':
            key_color = self.KEY_ELECTRIC_COLOR
        elif self.mode == 'blood':
            key_color = self.KEY_BLOOD_COLOR
        draw_bottom_rect(self.screen,
             self.KEY_WIDTH,
             activity*self.KEY_HEIGHT,
             key_color,
             .5*self.SCREEN_WIDTH+xpos,
             0.5*self.SCREEN_HEIGHT+0.5*self.KEY_HEIGHT-.5*self.KEY_WIDTH) 
        if keydown:
            circle_color = self.KEY_DOWN_COLOR
        else:
            circle_color = self.KEY_FORCE_COLOR
        draw_filled_aacircle(self.screen,
             self.KEY_WIDTH/2.,
             circle_color,
             .5*self.SCREEN_WIDTH+xpos,
             0.5*self.SCREEN_HEIGHT+0.5*self.KEY_HEIGHT+.25*self.KEY_WIDTH) 

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

def gen_hrf(tr=0.25, n_trs=120, c=1./6, a1=6, a2=16):
    # a1, a2: timepoints of peaks
    # c1: ratio between peak and trough
    t = tr*np.arange(n_trs) + tr*.5
    h = (np.exp(-t)*(t**(a1-1)/np.math.factorial(a1-1)
         - c*t**(a2-1)/np.math.factorial(a2-1)))
    return h/np.sum(h)

if __name__ == "__main__":
    game = neurofeedbackGame()
    game.run()
