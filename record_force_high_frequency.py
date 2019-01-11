import pygame
import sys, time
from keyboardClass import rewireKeyboard

class forceRecorder(object):

    def __init__(self, max_key_force=2.):
        # initialize pygame and graphics
        pygame.init()
        self.max_key_force = max_key_force
        self.pygame_keyboard = pygame.joystick.Joystick(0)
        self.clock = pygame.time.Clock()
        self.FRAME_RATE = 1000.
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 20, 20
        # keyboard must be declared BEFORE screen initialized
        self.keyboard = rewireKeyboard(self.pygame_keyboard)
        self.screen = pygame.display.set_mode(
            (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.BG_COLOR_PASSIVE = 40,40,40
        self.BG_COLOR_ACTIVE = 40,120,40
        self.BG_COLOR = self.BG_COLOR_PASSIVE

        # force recording
        self.recording_bool = False
        self.force_file = open('logs/log_'+str(int(time.time()))+'.csv','w')
        self.force_file.write('time_passed,')
        for finger in range(4):
            self.force_file.write('force_'+str(finger))
            if finger < 3:
                self.force_file.write(',')
            else:
                self.force_file.write('\n')

    def check_input(self):
        self.keyboard.update_inputs()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.quit()
                if event.key == pygame.K_r:
                    self.recording_bool = not(self.recording_bool)
                if event.key == pygame.K_z: self.keyboard.set_zero_force()
            elif event.type == pygame.KEYUP:
                pass

    def run(self):
        while True:
            time_passed = self.clock.tick_busy_loop(self.FRAME_RATE)/1000.
            self.check_input()
            if self.recording_bool:
                self.record_force(time_passed)
            self.draw_background()
            pygame.display.flip()

    def draw_background(self):
        if self.recording_bool:
            self.BG_COLOR = self.BG_COLOR_ACTIVE
        else:
            self.BG_COLOR = self.BG_COLOR_PASSIVE
        self.screen.fill(self.BG_COLOR)

    def record_force(self, time_passed):
        self.force_file.write(str(time_passed)+',')
        for finger in range(4):
            self.force_file.write(str(self.keyboard.force[finger]))
            if finger < 3:
                self.force_file.write(',')
            else:
                self.force_file.write('\n')

    def quit(self):
        sys.exit()

if __name__ == "__main__":
    game = forceRecorder()
    game.run()
