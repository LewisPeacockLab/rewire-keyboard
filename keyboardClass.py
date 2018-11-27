import serial, glob, time, os
import numpy as np
import pygame

class rewireKeyboard(object):

    def __init__(self, pygame_keyboard, full_range_force=2.,
            key_down_force=0.4, key_up_force=0.3, min_key_force=0.1,
            num_keys=4, time_history_points=100):
        self.pygame_keyboard = pygame_keyboard
        self.pygame_keyboard.init()

        # initialize generic state
        self.num_keys = num_keys
        self.time_history_points = time_history_points
        self.keydown = np.full(self.num_keys, False)
        self.force_ratio = np.zeros(self.num_keys)
        self.raw_force = np.zeros(self.num_keys)
        self.force = np.zeros(self.num_keys)
        self.zero_force = np.zeros(self.num_keys)
        self.raw_force_history = np.zeros((self.time_history_points, self.num_keys))

        # force values for scaling (Newtons)
        self.full_range_force = full_range_force
        self.key_down_force = key_down_force
        self.key_up_force = key_up_force 
        self.min_key_force = min_key_force

        # sending to teensy 
        if os.name == 'nt':
            import win32com.client
            wmi = win32com.client.GetObject("winmgmts:")
            for device in wmi.InstancesOf("Win32_SerialPort"):
                if device.Description == 'USB Serial Device':
                    teensy_device = device.Name.split('(')[1].split(')')[0]
                    self.teensy_device = device.Name.split('(')[1].split(')')[0]
        else:
            self.teensy_device = glob.glob('/dev/tty.*usb*')[0]
        self.teensy = serial.Serial(self.teensy_device)

    def update_inputs(self):
        self.raw_force_history = np.roll(self.raw_force_history, -1, 0)
        for key in range(self.num_keys):
            self.force_ratio[key] = max(0,min(.5*(1+self.pygame_keyboard.get_axis(key)),1))
            self.raw_force[key] = self.full_range_force*self.force_ratio[key]
            self.raw_force_history[0,key] = self.raw_force[key]
            self.force[key] = self.raw_force[key]-self.zero_force[key]
            if not(self.keydown[key]) and (self.force[key] >= self.key_down_force):
                self.keydown[key] = True
            if self.keydown[key] and (self.force[key] <= self.key_up_force):
                    self.keydown[key] = False

    def send_stimulus(self, stimulus_code='0P0'):
        # stimulus code follows:
        # finger pair, order (positive or negative), and timing
        # for 4 fingers, we have pairs '0', '1', or '2'
        # for order we can be positive (right first) or negative (left first)
        # for timing we have from '0' to '9' - up to 10 timings (hardcoded in firmware)
        self.teensy.write(stimulus_code)

    def set_zero_force(self):
        self.zero_force[:] = np.mean(self.raw_force_history,0)
