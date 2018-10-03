#include <algorithm>
#include <math.h>

// analog read
int NUM_BUTTONS = 4;
float MAX_ANALOG_VOLTAGE = 3.3;
int MAX_ANALOG_VALUE = 8192;
int ANALOG_READ_RESOLUTION = 13;
float VOLTAGE_AT_MIN_FORCE[] = {0.3, 0.3, 0.3, 0.3};
float VOLTAGE_AT_MAX_FORCE[] = {3.3, 3.3, 3.3, 3.3};
float MAX_FORCE = 14.709975; // newtons
int MAX_ANALOG_OUT = 1023;
float MAX_FORCE_OUT = 8.0; // newtons

// declare input pins
int forcePins[] = {A20, A18, A8, A6}; // !FIXTHIS (based on layout)

// analog write
int ANALOG_WRITE_RESOLUTION = 12;

// declare output pins
// int forcePins[] = {A20, A18, A8, A6}; // !FIXTHIS (add analog output pins)
 
int forceValues[NUM_BUTTONS];
float forceVoltages[NUM_BUTTONS];
float forceNewtons[NUM_BUTTONS];
int forceOutValues[NUM_BUTTONS];

void setup() {
  analogReadResolution(ANALOG_READ_RESOLUTION);
  analogWriteResolution(ANALOG_WRITE_RESOLUTION);
}

/*

def get_sin_output(amplitude, time) {
  return amplitude*math.sin(time)
}

def deliver_stims(finger1, finger2, time_offset) {
  return amplitude*math.sin(time)
}

*/

void loop() {
  for (int i=0; i<NUM_BUTTONS; i++){
    forceValues[i] = analogRead(forcePins[i]);
    forceVoltages[i] = MAX_ANALOG_VOLTAGE*(float)forceValues[i]/float(MAX_ANALOG_VALUE);
    forceNewtons[i] = {MAX_FORCE*(forceVoltages[i]-VOLTAGE_AT_MIN_FORCE[i])
      /(VOLTAGE_AT_MAX_FORCE[i]-VOLTAGE_AT_MIN_FORCE[i])};

    forceOutValues[i] = (float)MAX_ANALOG_OUT*(forceNewtons[i]/MAX_FORCE_OUT);
    forceOutValues[i] = (int)max(0,min(forceOutValues[i],MAX_ANALOG_OUT));
  }
  Joystick.X(forceOutValues[0]);
  Joystick.Y(forceOutValues[1]);
  Joystick.Z(forceOutValues[2]);
  Joystick.Zrotate(forceOutValues[3]);
}
