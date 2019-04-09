import pygame
import serial
import sys, glob, time
from pygame.gfxdraw import aacircle
from keyboardClass import rewireKeyboard
from targetClass import repeatTargetList, draw_filled_aacircle
import numpy as np

def draw_msg(screen, text, color=(255,255,255),
         loc='center', pos=(1024/2,768/2), size=50,
         font='freesansbold.ttf'):
    font = pygame.font.Font(font, size)
    text_surf, text_rect = make_text(text, font, color)
    if loc == 'center':
        text_rect.center = pos
    elif loc == 'left':
        text_rect.center = pos
        text_rect.left = pos[0]
    elif loc == 'right':
        text_rect.center = pos
        text_rect.right = pos[0]
    screen.blit(text_surf, text_rect)

def make_text(text, font, color):
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()

class testGame(object):

    def __init__(self, max_key_force=0.5, logging_bool=False):
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
        self.KEY_OFFSET = 0.2*self.SCREEN_WIDTH

        # force logic
        self.max_key_force = max_key_force
        self.overforce = 0.375
        self.min_key_force = 0.015
        self.min_key_overforce = 0.2
        self.target_key_force = 0.25
        self.target_duration = 0.3
        self.target_velocity = 350 # pixels
        self.force_scaling_powers = [.75, .9, 1, 1.25, 1.5, .5]
        self.force_scaling_power = self.force_scaling_powers[0]
        self.debug = False

        # target logic

        # null target list to pass in so it won't display anything at beginning
        self.target_list_null = repeatTargetList(self.screen, start_time_list=[])

        self.target_finger = 0
        self.start_time_list = -np.linspace(2.5,12.5,10)
        self.target_list_active = repeatTargetList(self.screen,
            target_finger = 0,
            target_force = self.target_key_force,
            target_type = 'trigger',
            force_scaling_power = self.force_scaling_power,
            start_time_list = self.start_time_list,
            duration = self.target_duration,
            velocity = self.target_velocity,
            key_spacing = self.KEY_OFFSET,
            min_width = self.KEY_MIN_DIAMETER,
            max_width = self.KEY_MAX_DIAMETER,
            max_force = self.max_key_force,
            overforce = self.overforce,
            screen_width = self.SCREEN_WIDTH,
            screen_height = self.SCREEN_HEIGHT)

        self.target_list = self.target_list_null

        self.target_list_keep_under_active = repeatTargetList(self.screen,
            target_finger = 0,
            target_force = self.overforce,
            target_type = 'keep_under',
            force_scaling_power = self.force_scaling_power,
            start_time_list = self.start_time_list,
            duration = self.target_duration,
            velocity = self.target_velocity,
            key_spacing = 0.2*self.SCREEN_WIDTH,
            min_width = self.KEY_MIN_DIAMETER,
            max_width = self.KEY_MAX_DIAMETER,
            max_force = self.max_key_force,
            screen_width = self.SCREEN_WIDTH,
            screen_height = self.SCREEN_HEIGHT)

        self.target_list_keep_under = self.target_list_null

        self.keep_over_target_groups = []
        self.keep_over_target_groups_active = []
        self.keep_over_target_groups_null = []
        self.keep_over_target_times = -np.linspace(1.5,13.5,48)
        self.keep_over_duration = 0.6
        for finger in range(4):
            self.keep_over_target_groups_active.append(repeatTargetList(self.screen,
                target_finger = finger,
                target_force = self.min_key_force,
                target_type = 'keep_over',
                force_scaling_power = self.force_scaling_power,
                start_time_list = self.keep_over_target_times,
                duration = self.keep_over_duration,
                velocity = self.target_velocity,
                key_spacing = 0.2*self.SCREEN_WIDTH,
                min_width = self.KEY_MIN_DIAMETER,
                max_width = self.KEY_MAX_DIAMETER,
                max_force = self.max_key_force,
                # overforce = self.min_key_overforce,
                screen_width = self.SCREEN_WIDTH,
                screen_height = self.SCREEN_HEIGHT))
            self.keep_over_target_groups.append(self.target_list_null)

        # file recording
        self.logging_bool = logging_bool
        if self.logging_bool:
            self.force_file = open('logs/log_'+str(int(time.time()))+'.csv','w')
            self.force_file.write('time_passed,')
            for finger in range(4):
                self.force_file.write('force_'+str(finger))
                if finger < 3:
                    self.force_file.write(',')
                else:
                    self.force_file.write('\n')

    def set_target_finger(self, target_finger):
        self.target_list = self.target_list_active
        self.target_list.set_target_finger(target_finger)
        self.target_list.reset_all()
        self.target_list_keep_under = self.target_list_keep_under_active
        self.target_list_keep_under.set_target_finger(target_finger)
        self.target_list_keep_under.reset_all()
        for finger in range(4):
            self.keep_over_target_groups[finger]=self.keep_over_target_groups_active[finger]
            self.keep_over_target_groups[finger].reset_all()

    def check_input(self):
        self.keyboard.update_inputs()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.quit()
                if event.key == pygame.K_1:
                    self.set_target_finger(0)
                if event.key == pygame.K_2:
                    self.set_target_finger(1)
                if event.key == pygame.K_3:
                    self.set_target_finger(2)
                if event.key == pygame.K_4:
                    self.set_target_finger(3)
                if event.key == pygame.K_q: self.keyboard.send_stimulus('0P2')
                if event.key == pygame.K_w: self.keyboard.send_stimulus('0N2')
                if event.key == pygame.K_e: self.keyboard.send_stimulus('0P3')
                if event.key == pygame.K_r: self.keyboard.send_stimulus('0N3')
                if event.key == pygame.K_a: self.keyboard.send_stimulus('0P0')
                if event.key == pygame.K_s: self.keyboard.send_stimulus('0N0')
                if event.key == pygame.K_d: self.keyboard.send_stimulus('0P1')
                if event.key == pygame.K_f: self.keyboard.send_stimulus('0N1')
                if event.key == pygame.K_d: self.debug = not(self.debug)
                if event.key == pygame.K_z: self.keyboard.set_zero_force()
            elif event.type == pygame.KEYUP:
                pass

    def run(self):
        while True:
            time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)/1000.
            if self.logging_bool:
                self.record_force(time_passed)
            self.check_input()
            self.draw_background()
            if self.debug:
                draw_msg(self.screen, 'Scaling: '+str(self.force_scaling_power),
                    pos=(self.SCREEN_WIDTH*0.1,self.SCREEN_HEIGHT*0.04),
                    size=20)

            for key in range(4):
                self.draw_key_background(key)

            self.target_list_keep_under.update_all(time_passed, self.keyboard.force)
            self.target_list_keep_under.draw_all()
            for finger in range(4): self.keep_over_target_groups[finger].update_all(time_passed, self.keyboard.force)
            for finger in range(4): self.keep_over_target_groups[finger].draw_all_ordered()
            self.target_list.update_all(time_passed, self.keyboard.force)
            self.target_list.draw_all()

            for key in range(4):
                self.draw_key(key)
            pygame.display.flip()

    def draw_key_background(self, key):
        xpos = self.KEY_OFFSET*(key-1.5)
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

    def draw_key(self,key_num):
        xpos = self.KEY_OFFSET*(key_num-1.5)
        display_ratio = self.keyboard.force[key_num]/self.max_key_force
        display_ratio = np.power(max(0,display_ratio), self.force_scaling_power)
        key_size = 0.5*display_ratio*self.KEY_DIAMETER_RANGE
        key_size = 0.5*self.KEY_MIN_DIAMETER+key_size
        key_size = max(0.5*self.KEY_MIN_DIAMETER,min(key_size,0.5*self.KEY_MAX_DIAMETER))
        if self.keyboard.force[key_num] < self.min_key_force:
            key_color = self.KEY_BAD_COLOR
        elif self.keyboard.force[key_num] >= self.overforce:
            key_color = self.KEY_BAD_COLOR
        elif self.keyboard.force[key_num] >= self.target_key_force:
            key_color = self.KEY_DOWN_COLOR
        else:
            key_color = self.KEY_FORCE_COLOR
        draw_filled_aacircle(self.screen,
            key_size,
            key_color,
            .5*self.SCREEN_WIDTH+xpos,
            0.5*self.SCREEN_HEIGHT)

    def record_force(self, time_passed):
        self.force_file.write(str(time_passed)+',')
        for finger in range(4):
            self.force_file.write(str(self.keyboard.force[finger]))
            if finger < 3:
                self.force_file.write(',')
            else:
                self.force_file.write('\n')

    def draw_background(self):
        self.screen.fill(self.BG_COLOR)

    def quit(self):
        sys.exit()

if __name__ == "__main__":
    game = testGame()
    game.run()
