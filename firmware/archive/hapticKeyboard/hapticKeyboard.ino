#include <algorithm>
#include <math.h>

// #include "AudioSampleCashregister.h"

#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SerialFlash.h>
#include "AudioSampleCashregister.h"
#include "AudioSampleKick.h"
#include "AudioSampleSnare.h"
#include "AudioSampleGong.h"

// audio output
AudioPlayMemory          playWav1;
AudioOutputAnalogStereo  audioOutput;
AudioConnection          patchCord1(playWav1, 0, audioOutput, 0);
// AudioConnection          patchCord2(playWav1, 1, audioOutput, 1);
AudioConnection          patchCord2(playWav1, 0, audioOutput, 1);

// analog read
const int NUM_BUTTONS = 4;
float MAX_ANALOG_VOLTAGE = 3.3;
int MAX_ANALOG_VALUE = 8192;
int ANALOG_READ_RESOLUTION = 13;
float VOLTAGE_AT_MIN_FORCE[] = {0.3, 0.3, 0.3, 0.3};
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

// declare output pins
int vibePins[] = {A21, A22};
bool toneLatches[] = {false, false};

int shutdownPins[] = {28, 27, 26, 25};
bool activeStatus[] = {false, false, false, false};

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
  pinMode(vibePins[0], OUTPUT);
  pinMode(vibePins[1], OUTPUT);

  // initialize the digital output pins:
  for (int i=0; i<NUM_BUTTONS; i++){
    pinMode(shutdownPins[i], OUTPUT);
    digitalWrite(shutdownPins[i], HIGH);
  }

  // audio
  AudioMemory(12);

}

void loop() {

  for (int i=0; i<NUM_BUTTONS; i++){
    forceValues[i] = analogRead(forcePins[i]);
    if (forceValues[i] > 2000)
      {
        activeStatus[i] = true;
        digitalWrite(shutdownPins[i], HIGH);
      }
    else
      {
        activeStatus[i] = false;
        digitalWrite(shutdownPins[i], LOW);
      }

    forceVoltages[i] = MAX_ANALOG_VOLTAGE*(float)forceValues[i]/float(MAX_ANALOG_VALUE);
    forceNewtons[i] = {MAX_FORCE*(forceVoltages[i]-VOLTAGE_AT_MIN_FORCE[i])
      /(VOLTAGE_AT_MAX_FORCE[i]-VOLTAGE_AT_MIN_FORCE[i])};

    forceOutValues[i] = (float)MAX_ANALOG_OUT*(forceNewtons[i]/MAX_FORCE_OUT);
    forceOutValues[i] = (int)max(0,min(forceOutValues[i],MAX_ANALOG_OUT));
  }

  if (activeStatus[0] || activeStatus[2])
    {
      if (!toneLatches[0])
        {
          // analogWrite(vibePins[0], sinmagnitude);
          playWav1.play(AudioSampleCashregister);
          toneLatches[0] = true;
          delay(200);
        }
    }
  else
    {
      if (toneLatches[0])
        {
          // analogWrite(vibePins[0], 0);
          toneLatches[0] = false;
        }
    }

  if (activeStatus[1] || activeStatus[3])
    {
      if (!toneLatches[1])
        {
          playWav1.play(AudioSampleKick);
          toneLatches[1] = true;
          delay(200);
        }
    }
  else
    {
      if (toneLatches[1])
        {
          toneLatches[1] = false;
        }
    }

  Joystick.X(forceOutValues[0]);
  Joystick.Y(forceOutValues[1]);
  Joystick.Z(forceOutValues[2]);
  Joystick.Zrotate(forceOutValues[3]);

}
