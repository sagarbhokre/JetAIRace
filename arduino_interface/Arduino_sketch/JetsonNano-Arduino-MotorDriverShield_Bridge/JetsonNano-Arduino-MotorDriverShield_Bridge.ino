/*
  Interface to control motor driver shield using jetson Nano
  Language: Wiring/Arduino

  This program receives command signals from Jetson Nano and controls motor driver shield
  connected to Arduino Uno
  
  The circuit:
  - Motor driver shield connected to 2 motors 1 and 2
  - Arduino Uno connected to Jetson Nano via USB port


  references: 
    https://learn.adafruit.com/adafruit-motor-shield/using-dc-motors
    http://blog.rareschool.com/2019/05/five-steps-to-connect-jetson-nano-and.html
    https://github.com/JetsonHacksNano/installArduinoIDE
  created 16 Feb 2020
  by Sagar Bhokre
*/

#include <AFMotor.h> 

int defaultSpeed = 50;  // Range 0 - 255

AF_DCMotor lMotor(1);
AF_DCMotor rMotor(2);

void setup() {
  // start serial port at 115200 bps:
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }

  lMotor.setSpeed(defaultSpeed);
  rMotor.setSpeed(defaultSpeed);
}

#define MAX_STR_SIZE (256)
char inChArr[MAX_STR_SIZE+1];
char printbuf[MAX_STR_SIZE];
int lSpeed, rSpeed;
char lDir, rDir;

void loop() {
  //byte size = Serial.readBytes(input, MAX_STR_SIZE);
  // if we get a valid byte, read analog ins:
  if (Serial.available() > 0) {
    int bytes = Serial.readBytesUntil('\n', inChArr, MAX_STR_SIZE);

    if(inChArr[0] == 'L') {
      // Input command string "L:+1 R:+3"
      lSpeed = inChArr[3] - '0';
      rSpeed = inChArr[8] - '0';
      lDir = inChArr[2];
      rDir = inChArr[7];
      
      sprintf(printbuf, "[Arduino] %s -- %c%d %c%d", inChArr, lDir, lSpeed, rDir, rSpeed);

      lMotor.setSpeed(lSpeed*25.5);
      rMotor.setSpeed(rSpeed*25.5);

      if(lDir == '+') {
        lMotor.run(FORWARD);
      }
      else {
        lMotor.run(BACKWARD);
      }

      if(rDir == '+') {
        rMotor.run(FORWARD);
      }
      else {
        rMotor.run(BACKWARD);
      }

      /*
      if(lSpeed > 4) {
        digitalWrite(LED_BUILTIN, HIGH);
      }
      else {
        digitalWrite(LED_BUILTIN, LOW);
      }*/
    }
    else if(inChArr[0] == 'A') { //Handshake pattern
      sprintf(printbuf, "[Arduino] A");
    }
    else {
      sprintf(printbuf, "[Arduino] Unknown command");
      digitalWrite(LED_BUILTIN, HIGH);
    }
    
    Serial.println(printbuf);
    Serial.flush();
  }
}
