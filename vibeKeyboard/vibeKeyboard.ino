#include <algorithm>
#include <math.h>

#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SerialFlash.h>

#include "AudioSample_250_20_firstwav.h"
#include "AudioSample_250_20_secondwav.h"

// audio output
AudioPlayMemory          playWav1;
AudioPlayMemory          playWav2;
AudioOutputAnalogStereo  audioOutput;
AudioConnection          patchCord1(playWav1, 0, audioOutput, 0);
AudioConnection          patchCord2(playWav2, 0, audioOutput, 1);

// analog read
const int NUM_BUTTONS = 4;
float MAX_ANALOG_VOLTAGE = 3.3;
int MAX_ANALOG_VALUE = 8192;
int ANALOG_READ_RESOLUTION = 13;
float VOLTAGE_AT_MIN_FORCE[] = {0.62, 0.65, 0.6, 0.6};
float VOLTAGE_AT_MAX_FORCE[] = {3.3, 3.3, 3.3, 3.3};
float MAX_FORCE = 14.709975; // newtons
int MAX_ANALOG_OUT = 1023;
float MAX_FORCE_OUT = 8.0; // newtons

// declare input pins
int forcePins[] = {A14, A15, A0, A8};
 
// force input params
int forceValues[NUM_BUTTONS];
float forceVoltages[NUM_BUTTONS];
float forceNewtons[NUM_BUTTONS];
int forceOutValues[NUM_BUTTONS];

// analog write
int ANALOG_WRITE_RESOLUTION = 12;

bool toneLatches[] = {false, false, false};

int shutdownPins[] = {28, 27, 26, 25};
bool activeStatus[] = {false, false, false, false};

// serial communication variables
char fingerMessage;
char timingMessage;
bool incomingStim = false;
int numFingerConditions = 3;
int numTimingConditions = 3;
char fingerMessageCodes[] = {'0', '1', '2'};
char timingMessageCodes[] = {'0', '1', '2'};

// vibrator output params
float phase = 0.0;
float twopi = 3.14159 * 2;
float frequency = 250.; // Hz

float sinmagnituderatio = 0.1;
float sinmagnitude = sinmagnituderatio * pow(2,ANALOG_WRITE_RESOLUTION);
float sinoffsetratio = 0.01;
float sinoffset = sinoffsetratio * pow(2,ANALOG_WRITE_RESOLUTION);

void setup() {
  analogReadResolution(ANALOG_READ_RESOLUTION);
  analogWriteResolution(ANALOG_WRITE_RESOLUTION);

  // initialize the digital output pins:
  for (int i=0; i<NUM_BUTTONS; i++){
    pinMode(shutdownPins[i], OUTPUT);
    digitalWrite(shutdownPins[i], HIGH);
  }

  // audio
  AudioMemory(12);

  // serial communication
  Serial.begin(9600);

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
  if (Serial.available() > 1)
    {
      fingerMessage = Serial.read();
      timingMessage = Serial.read();
      incomingStim = true;
      for (int fingerCondition=0; fingerCondition<numFingerConditions; fingerCondition++){
        if (fingerMessage == fingerMessageCodes[fingerCondition])
          {
            fingerMessage = fingerCondition;
            break;
          }
        }
      for (int timingCondition=0; timingCondition<numTimingConditions; timingCondition++){
        if (timingMessage == timingMessageCodes[timingCondition])
          {
            timingMessage = timingCondition;
            break;
          }
        }
    }

  // stims
  if (incomingStim == true)
    {
      incomingStim = false;
      switch (fingerMessage)
        {
          case 0:
            digitalWrite(shutdownPins[0], HIGH);
            digitalWrite(shutdownPins[1], HIGH);
            digitalWrite(shutdownPins[2], LOW);
            digitalWrite(shutdownPins[3], LOW);
            break;
          case 1:
            digitalWrite(shutdownPins[0], LOW);
            digitalWrite(shutdownPins[1], HIGH);
            digitalWrite(shutdownPins[2], HIGH);
            digitalWrite(shutdownPins[3], LOW);
            break;
          case 2:
            digitalWrite(shutdownPins[0], LOW);
            digitalWrite(shutdownPins[1], LOW);
            digitalWrite(shutdownPins[2], HIGH);
            digitalWrite(shutdownPins[3], HIGH);
            break;
        }
        switch (timingMessage)
        {
          case 0:
            playWav1.play(AudioSample_250_20_secondwav);
            playWav2.play(AudioSample_250_20_firstwav);
            break;
          case 1:
            playWav1.play(AudioSample_250_20_secondwav);
            playWav2.play(AudioSample_250_20_firstwav);
            break;
          case 2:
            playWav1.play(AudioSample_250_20_secondwav);
            playWav2.play(AudioSample_250_20_firstwav);
            break;
        }

    }

}
