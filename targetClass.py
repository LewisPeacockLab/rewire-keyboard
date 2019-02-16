import pygame
from pygame.gfxdraw import aacircle
import numpy as np

BG_COLOR = 40,40,40
KEY_BG_COLOR_DARKER = 70,70,70
KEY_BG_COLOR = 100,100,100
KEY_FORCE_COLOR = 150,150,150
KEY_DOWN_COLOR = 40,150,40
KEY_BAD_COLOR = 150,40,40

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

def draw_center_oval(screen, width, height, color, xpos, ypos):
    xpos = int(xpos)
    ypos = int(ypos)
    rect = pygame.Rect(xpos-int(0.5*width),
                       ypos-int(0.5*height),
                       2*int(0.5*width)+1,
                       2*int(0.5*height))
    pygame.draw.rect(screen, color, rect)
    draw_filled_aacircle(screen, int(0.5*width), color, xpos, ypos+int(0.5*height))
    draw_filled_aacircle(screen, int(0.5*width), color, xpos, ypos-int(0.5*height))

def draw_bottom_oval(screen, width, height, color, xpos, ypos):
    xpos = int(xpos)
    ypos = int(ypos)
    rect = pygame.Rect(xpos-int(0.5*width),
                       ypos-2*int(0.5*height),
                       2*int(0.5*width)+1,
                       2*int(0.5*height))
    pygame.draw.rect(screen, color, rect)
    draw_filled_aacircle(screen, int(0.5*width), color, xpos, ypos)
    draw_filled_aacircle(screen, int(0.5*width), color, xpos, ypos-int(height))

class target(object):

    def __init__(self, screen, target_finger=0, target_force=1,
            target_type='trigger',
            force_scaling_power=0.75, start_time=-0.2,
            duration=0.3, velocity=350, key_spacing=200, min_width=20,
            max_width=120, max_force=2, overforce=1.5, screen_width=400, screen_height=400):

        # geometry and timing
        self.screen = screen
        self.target_finger = target_finger
        self.target_force = target_force
        self.target_type = target_type # 'trigger', 'keep_over', 'keep_under'
        self.force_scaling_power = force_scaling_power
        self.start_time = start_time
        self.time = self.start_time
        self.duration = duration
        self.velocity = velocity
        self.x_offset = 0.5*screen_width
        self.y_offset = 0.5*screen_height
        self.color = KEY_BG_COLOR
        self.min_width = min_width
        self.max_width = max_width
        self.max_force = max_force
        self.overforce = overforce
        self.key_spacing = key_spacing
        self.set_finger(self.target_finger)
        self.set_geometry(self.target_force, self.duration, self.velocity)
        self.update(time_passed=0)

        # target state
        self.max_force_seen = 0
        self.min_force_seen = 0

    def set_finger(self, target_finger=0):
        self.target_finger = target_finger
        self.xpos = self.x_offset+self.key_spacing*(self.target_finger-1.5)

    def set_geometry(self, target_force, duration, velocity):
        display_ratio = target_force/self.max_force
        display_ratio = np.power(display_ratio, self.force_scaling_power)
        self.width = self.min_width+display_ratio*(self.max_width-self.min_width)
        self.height = duration*velocity 

    def reset(self):
        self.update(-self.time+self.start_time)

    def update(self, time_passed, in_force=0):
        self.time += time_passed
        self.ypos = self.time*self.velocity+self.y_offset
        if self.target_type == 'trigger':
            self.update_trigger_target(in_force)
        elif self.target_type == 'keep_over':
            self.update_trigger_keep_over(in_force)
        elif self.target_type == 'keep_under':
            self.update_trigger_keep_under(in_force)

    def update_trigger_target(self, in_force=0):
        if self.time <= 0:
            self.max_force_seen=0
            self.color = KEY_BG_COLOR
        elif (self.time > 0) and (self.time <= self.duration):
            if in_force > self.max_force_seen:
                self.max_force_seen = in_force
                if self.max_force_seen >= self.overforce:
                    self.color = KEY_BAD_COLOR
                elif self.max_force_seen >= self.target_force:
                    self.color = KEY_DOWN_COLOR
        elif self.time > self.duration:
            if self.max_force_seen < self.target_force:
                self.color = KEY_BAD_COLOR

    def update_trigger_keep_over(self, in_force=0):
        if self.time <= 0:
            self.min_force_seen=self.target_force
            self.max_force_seen=0
            self.color = KEY_BG_COLOR
        elif (self.time > 0) and (self.time <= self.duration):
            if in_force < self.min_force_seen:
                self.min_force_seen = in_force
                if self.min_force_seen < self.target_force:
                    self.color = KEY_BAD_COLOR
            if in_force > self.max_force_seen:
                self.max_force_seen = in_force
                if self.max_force_seen >= self.overforce:
                    self.color = KEY_BAD_COLOR

        # elif self.time > self.duration:
        #     if self.min_force_seen >= self.target_force:
        #         self.color = KEY_DOWN_COLOR

    def update_trigger_keep_under(self, in_force=0):
        if self.time <= 0:
            self.max_force_seen=0
            self.color = KEY_BG_COLOR_DARKER
        elif (self.time > 0) and (self.time <= self.duration):
            if in_force > self.max_force_seen:
                self.max_force_seen = in_force
                if self.max_force_seen >= self.target_force:
                    self.color = KEY_BAD_COLOR
        # elif self.time > self.duration:
        #     if self.max_force_seen < self.target_force:
        #         self.color = KEY_DOWN_COLOR

    def draw(self):
        if self.ypos < 4*self.y_offset: # safety factor to not draw out of bounds
            draw_bottom_oval(self.screen, self.width, self.height,
                self.color, self.xpos, self.ypos)

class repeatTargetList(object):
    def __init__(self, screen, target_finger=0, target_force=1,
            target_type='trigger',
            force_scaling_power=0.75, start_time_list=[0],
            duration=0.3, velocity=350, key_spacing=200, min_width=10,
            max_width=100, max_force=2, overforce=1.5, screen_width=400, screen_height=400):
        self.targets = []
        for idx in range(len(start_time_list)):
            self.targets.append(target(screen,
                target_finger=target_finger,
                target_force=target_force,
                target_type=target_type,
                force_scaling_power=force_scaling_power,
                start_time=start_time_list[idx],
                duration=duration,
                velocity=velocity,
                key_spacing=key_spacing,
                min_width=min_width,
                max_width=max_width,
                max_force=max_force,
                overforce=overforce,
                screen_width=screen_width,
                screen_height=screen_height))

    def update_all(self, time_passed, force_in_vector):
        for target_instance in self.targets:
            target_instance.update(time_passed, force_in_vector[target_instance.target_finger])

    def set_target_finger(self, target_finger=0):
        for target_instance in self.targets:
            target_instance.set_finger(target_finger)

    def draw_all(self):
        for target_instance in self.targets:
            target_instance.draw()

    def draw_all_ordered(self):
        draw_first_bools = np.full(len(self.targets),False)
        for idx, target_instance in enumerate(self.targets):
            draw_first_bools[idx]=((target_instance.color==KEY_BG_COLOR)
                or (target_instance.color==KEY_BG_COLOR_DARKER))
            if draw_first_bools[idx]: target_instance.draw()
        for idx in np.where(draw_first_bools==False)[0]:
            self.targets[idx].draw()

    def reset_all(self):
        for target_instance in self.targets:
            target_instance.reset()

# class keepWithinBounds(object):
#     def __init__(self, screen, target_finger=0, start_time=0,
#             duration=0.3, velocity=350, xpos=200, width=100, screen_height=400):
#         pass
