#include <algorithm>
#include <math.h>

#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SerialFlash.h>
#include <SD.h>

// audio output
AudioPlaySdWav           playWav;
AudioOutputAnalogStereo  audioOutput;
AudioConnection          patchCord1(playWav, 0, audioOutput, 0);
AudioConnection          patchCord2(playWav, 1, audioOutput, 1);

// analog read
const int NUM_BUTTONS = 4;
float MAX_ANALOG_VOLTAGE = 3.3;
int MAX_ANALOG_VALUE = 8192;
int ANALOG_READ_RESOLUTION = 13;
float VOLTAGE_AT_MIN_FORCE[] = {0.6, 0.6, 0.6, 0.6};
float VOLTAGE_AT_MAX_FORCE[] = {1.05, 1.75, 1.75, 1.05};
float MAX_FORCE = 10.7873; // newtons
int MAX_ANALOG_OUT = 1023;
float MAX_FORCE_OUT = 8.0; // newtons

// declare input pins
int forcePins[] = {A14, A15, A0, A8};
 
// force input params
int forceValues[NUM_BUTTONS];
float forceVoltages[NUM_BUTTONS];
float forceNewtons[NUM_BUTTONS];
int forceOutValues[NUM_BUTTONS];

// control of shutdown pins
int shutdownPins[] = {28, 27, 26, 25};

// serial communication variables
char fingerMessage;
char orderMessage;
char timingMessage;
bool incomingStim = false;
int numFingerConditions = 3;
int numOrderConditions  = 2;
int numTimingConditions = 6;
char fingerMessageCodes[] = {'0', '1', '2'};
char orderMessageCodes[]  = {'P', 'N'};
char timingMessageCodes[] = {'0', '1', '2', '3', '4', '5'};
char wavFileName[] = "P0.WAV";

void setup() {
  analogReadResolution(ANALOG_READ_RESOLUTION);

  // initialize the digital output pins:
  for (int i=0; i<NUM_BUTTONS; i++){
    pinMode(shutdownPins[i], OUTPUT);
    digitalWrite(shutdownPins[i], HIGH);
  }

  // serial communication
  Serial.begin(9600);

  // audio
  AudioMemory(12);
  if (!(SD.begin(BUILTIN_SDCARD))) {
    // stop here, but print a message repetitively
    while (1) {
      Serial.println("Unable to access the SD card");
      delay(500);
    }
  }
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

  // checking serial
  if (Serial.available() > 2)
    {
      fingerMessage = Serial.read();
      orderMessage = Serial.read();
      timingMessage = Serial.read();
      incomingStim = true;
    }
  if (incomingStim == true)
    {
      incomingStim = false;
      handleStim(fingerMessage, orderMessage, timingMessage);
    }
}

void handleStim(char fingerMessage, char orderMessage, char timingMessage)
{
  // select stimulators based on finger message
  if (fingerMessage == fingerMessageCodes[0]) {
    digitalWrite(shutdownPins[0], HIGH);
    digitalWrite(shutdownPins[1], HIGH);
    digitalWrite(shutdownPins[2], LOW);
    digitalWrite(shutdownPins[3], LOW);
  }
  else if (fingerMessage == fingerMessageCodes[1]) {
    digitalWrite(shutdownPins[0], LOW);
    digitalWrite(shutdownPins[1], HIGH);
    digitalWrite(shutdownPins[2], HIGH);
    digitalWrite(shutdownPins[3], LOW);
    // for center finger pair, need to flip the sign
    if (orderMessage == orderMessageCodes[0]) {
      orderMessage = orderMessageCodes[1];
    }
    else if (orderMessage == orderMessageCodes[1]) {
      orderMessage = orderMessageCodes[0];
    }
  }
  else if (fingerMessage == fingerMessageCodes[2]) {
    digitalWrite(shutdownPins[0], LOW);
    digitalWrite(shutdownPins[1], LOW);
    digitalWrite(shutdownPins[2], HIGH);
    digitalWrite(shutdownPins[3], HIGH);
  }

  // play audio
  wavFileName[0] = orderMessage;
  wavFileName[1] = timingMessage;

  playWav.play(wavFileName);
}
