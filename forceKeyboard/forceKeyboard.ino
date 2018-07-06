#include <Bounce.h>
#include <algorithm>
#include <math.h>

int DEBUG = 0; // set to 1 for serial debug output

int DEBOUNCE_TIME = 5;
float MAX_ANALOG_VOLTAGE = 3.3;
int MAX_ANALOG_VALUE = 8192;
int ANALOG_READ_RESOLUTION = 13;
float VOLTAGE_AT_MIN_FORCE = 0.63;
float VOLTAGE_AT_MAX_FORCE = 3.3;
float MAX_FORCE = 14.709975; // newtons
int MAX_ANALOG_OUT = 1023;
float MAX_FORCE_OUT = 2.0; // newtons

int buttonPin = A3; // select the input pin for the button
int forcePin = A6;

Bounce pushButton = Bounce(buttonPin, DEBOUNCE_TIME);
 
int buttonState = 0; // variable for reading the pushbutton status
int forceValue = 0;
float forceVoltage = 0;
float forceNewtons = 0;
int forceOutValue = 0;

void setup() {
  if (DEBUG) {
    Serial.begin(57600);
  }
  // initialize the pushbutton pin as an input:
  pinMode(buttonPin, INPUT_PULLUP);
}

void loop() {
  analogReadResolution(ANALOG_READ_RESOLUTION);
  pushButton.update();
  if (pushButton.fallingEdge()) {
    Keyboard.press(KEY_1);
  }
  else if (pushButton.risingEdge()) {
    Keyboard.release(KEY_1);
  }
  forceValue = analogRead(forcePin);
  forceVoltage = MAX_ANALOG_VOLTAGE*(float)forceValue/float(MAX_ANALOG_VALUE);
  forceNewtons = {MAX_FORCE*(forceVoltage-VOLTAGE_AT_MIN_FORCE)
    /(VOLTAGE_AT_MAX_FORCE-VOLTAGE_AT_MIN_FORCE)};

  forceOutValue = (float)MAX_ANALOG_OUT*(forceNewtons/MAX_FORCE_OUT);
  forceOutValue = (int)max(0,min(forceOutValue,MAX_ANALOG_OUT));
  Joystick.X(forceOutValue);

  if (DEBUG) {
    Serial.print(forceNewtons);
    Serial.print(" N, ");
    Serial.print(forceVoltage);
    Serial.print(" V\n");
  }
}
