//////////////////////////////////////////////////////////
//// SuperK Varia ND filter motor control
//// v0.9, 13th October 2016 (created: 17th August 2016)
//// Jeffrey Lidgard, jeffrey.lidgard@physics.ox.ac.uk
//// University of Oxford, Department of Physics
//////////////////////////////////////////////////////////

// Requires the AFMotor library (https://github.com/adafruit/Adafruit-Motor-Shield-library)
// And AccelStepper with AFMotor support, v1.53: http://www.airspayce.com/mikem/arduino/AccelStepper/ old v1.2:(https://github.com/adafruit/AccelStepper)
// Public domain!
#include <AccelStepper.h>
#include <AFMotor.h>

//misc variables:
AF_Stepper motor1(200, 2);
int delayInterval = 5;  //delay value in milliseconds
const int homePin = A0;   //home signal connected to analog pin 0
boolean homeState = false;
String readCommand, readType, readValue;
int readValueInt;
  
// you can change these to DOUBLE or INTERLEAVE or MICROSTEP!
// wrappers for the first motor!
void forwardstep1() {  
  motor1.onestep(FORWARD, SINGLE);
}
void backwardstep1() {  
  motor1.onestep(BACKWARD, SINGLE);
}
AccelStepper stepper1(forwardstep1, backwardstep1);

void setup() {

  //setup channels:
  Serial.begin(57600); //initialize serial communication at 57600 bits per second:

  stepper1.setMaxSpeed(10.0);
  stepper1.setAcceleration(1.0);

  pinMode(homePin, INPUT);
  homeState = digitalRead(homePin); //get the initial state of the home pin (should be ON)
  //Serial.print("Initial read Home state:");Serial.println(homeState);  
  
  // wait for things to stabilize
  delay(100);
}

void readHome(){
    homeState = digitalRead(homePin); //reads the analog input pin
}

void goHome(){

      if (stepper1.isRunning()==false) {
        
        stepper1.setMaxSpeed( 10 );
        stepper1.setSpeed( 10 );
        stepper1.move( 500 );
      
        while ( (homeState==false) && (stepper1.distanceToGo()>0) ) {
  
          if (stepper1.runSpeed()) {
            readHome();
          }
          Serial.print("Seeking home, position: ");Serial.println(stepper1.currentPosition());
          delay(10);
        }
        stepper1.stop();
        stepper1.setCurrentPosition( 0 );
        if (homeState = true) {
          Serial.println("At home");
        }
        else if (stepper1.distanceToGo()==0) {
          Serial.println("Failed to find home");
        }
      }
      else {
        Serial.println("Motor already moving");
      }
}

String readSerial(){

  String readCommand;
  while (Serial.available()) {
    delay(10);  //delay to allow buffer to fill
    if (Serial.available() >0 ) {
      char c = Serial.read();  //gets one byte from serial buffer
      readCommand += c; //makes the string readString
    }
  }
  return readCommand;
}

void loop() {

  //main program delay
  delay(delayInterval); //delay by 1/x Hz (note the ultimate run rate is also effected by various functions)
  
  readCommand = readSerial();

  if (readCommand.length() >0) {
    //Serial.print("ReadCommand: ");Serial.println(readCommand); //see what was received
 
    readType = readCommand.substring(0, 1);
    //Serial.print("Type: ");Serial.println(readType); //check type received
    
    if (readCommand.length()>1) {
      readValue = readCommand.substring(1, readCommand.length() );
      readValueInt = readValue.toInt();
      //Serial.print("Value: ");Serial.println(readValueInt); //check value received
    }
    else {
       readValue = "";
       readValueInt = 0;
    }

    //now choose
    if (readType == "a") { // Report current position.
      Serial.print("Position: "); Serial.println( stepper1.currentPosition() );
    }
    if (readType == "b") { // Report motor speed.
      Serial.print("Speed: "); Serial.println( stepper1.speed() );
    }
    if (readType == "c") { // Set max motor speed.
      stepper1.setMaxSpeed( readValue.toInt() );
    }
    if (readType == "d") { // Set position.
      stepper1.moveTo( readValueInt );
      stepper1.runToPosition();
    }
    if (readType == "e") { // Set home position.
      stepper1.setCurrentPosition( readValueInt );
    }
    if (readType == "f") { // Get home position.
      readHome();
      Serial.print("Home sensor: "); Serial.println( homeState );
    }
    if (readType == "g") { // Stop running.
      stepper1.stop();
    }
    if (readType == "h") { // Check to see if the motor is currently running.
      Serial.print("isRunning: "); Serial.println( stepper1.isRunning() );
    }
    if (readType == "i") { // Set motor acceleration.
      stepper1.setAcceleration( readValue.toInt() );
    }
    if (readType == "j") { // Report max motor speed.
      Serial.print("Max Speed: "); Serial.println( stepper1.maxSpeed() );
    }
    if (readType == "k") { // Report connected
      goHome();
    }
    if (readType == "z") { // Report connected
      Serial.println("Connected.");
    }
  }

}
