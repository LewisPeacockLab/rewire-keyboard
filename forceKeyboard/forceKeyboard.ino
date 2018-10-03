#include <Bounce.h>
#include <algorithm>
#include <math.h>

int DEBOUNCE_TIME = 5;
const int NUM_BUTTONS = 4;
float MAX_ANALOG_VOLTAGE = 3.3;
int MAX_ANALOG_VALUE = 8192;
int ANALOG_READ_RESOLUTION = 13;
// float VOLTAGE_AT_MIN_FORCE = 0.;
// float VOLTAGE_AT_MAX_FORCE = 3.3;
// float MAX_FORCE = 1.0; // newtons
// int MAX_ANALOG_OUT = 1023;
// float MAX_FORCE_OUT = 0.3; // newtons
float VOLTAGE_AT_MIN_FORCE[] = {0.79, 0.64, 0.67, 0.65};
float VOLTAGE_AT_MAX_FORCE = 3.3;
float MAX_FORCE = 14.709975; // newtons
int MAX_ANALOG_OUT = 1023;
float MAX_FORCE_OUT = 4.0; // newtons

// int buttonPins[] = {A3, A2, A1, A0}; // select the input pin for the button
// int forcePins[] = {A6, A8, A18, A20};
int buttonPins[] = {A0, A1, A2, A3}; // select the input pin for the button
int forcePins[] = {A20, A18, A8, A6};
int keyCodes[] = {KEY_1, KEY_2, KEY_3, KEY_4};
Bounce pushButtons[NUM_BUTTONS] = {
  Bounce(buttonPins[0], DEBOUNCE_TIME),
  Bounce(buttonPins[1], DEBOUNCE_TIME),
  Bounce(buttonPins[2], DEBOUNCE_TIME),
  Bounce(buttonPins[3], DEBOUNCE_TIME)
};
 
int forceValues[NUM_BUTTONS];
float forceVoltages[NUM_BUTTONS];
float forceNewtons[NUM_BUTTONS];
int forceOutValues[NUM_BUTTONS];

void setup() {
  // initialize the pins as an input:
  for (int i=0; i<NUM_BUTTONS; i++){
    pinMode(buttonPins[i], INPUT_PULLUP);
  }
}

void loop() {
  analogReadResolution(ANALOG_READ_RESOLUTION);
  for (int i=0; i<NUM_BUTTONS; i++){
    pushButtons[i].update();
    if (pushButtons[i].fallingEdge()) {
      Keyboard.press(keyCodes[i]);
    }
    else if (pushButtons[i].risingEdge()) {
      Keyboard.release(keyCodes[i]);
    }
    forceValues[i] = analogRead(forcePins[i]);
    forceVoltages[i] = MAX_ANALOG_VOLTAGE*(float)forceValues[i]/float(MAX_ANALOG_VALUE);
    forceNewtons[i] = {MAX_FORCE*(forceVoltages[i]-VOLTAGE_AT_MIN_FORCE[i])
      /(VOLTAGE_AT_MAX_FORCE-VOLTAGE_AT_MIN_FORCE[i])};

    forceOutValues[i] = (float)MAX_ANALOG_OUT*(forceNewtons[i]/MAX_FORCE_OUT);
    forceOutValues[i] = (int)max(0,min(forceOutValues[i],MAX_ANALOG_OUT));
  }
  Joystick.X(forceOutValues[0]);
  Joystick.Y(forceOutValues[1]);
  Joystick.Z(forceOutValues[2]);
  Joystick.Zrotate(forceOutValues[3]);
}
