#include <algorithm>
#include <math.h>

// analog read
const int NUM_BUTTONS = 4;
float MAX_ANALOG_VOLTAGE = 3.3;
int MAX_ANALOG_VALUE = 8192;
int ANALOG_READ_RESOLUTION = 13;
float VOLTAGE_AT_MIN_FORCE[] = {0.0, 0.0, 0.0, 0.0};
float VOLTAGE_AT_MAX_FORCE[] = {3.3, 3.3, 3.3, 3.3};
float MAX_FORCE = 15.0; // newtons
int MAX_ANALOG_OUT = 1023;
float MAX_FORCE_OUT = 5.0; // newtons
// float MAX_FORCE_OUT = 15.0; // newtons
// float MAX_FORCE_OUT = 2.0; // newtons

// declare input pins
int forcePins[] = {A13, A12, A14, A15};
 
// force input params
int forceValues[NUM_BUTTONS];
float forceVoltages[NUM_BUTTONS];
float forceNewtons[NUM_BUTTONS];
int forceOutValues[NUM_BUTTONS];

void setup() {
  analogReadResolution(ANALOG_READ_RESOLUTION);
}

void loop() {

  // force outputs
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
