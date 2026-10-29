#include <ESP32Servo.h> 

Servo servo1;
Servo servo2;
Servo servo3;

int angle1 = 90;
int angle2 = 90;
int angle3 = 90;
String inputString = "";

void setup() {
  Serial.begin(115200); 
  servo1.attach(18);    
  servo2.attach(19);     
  servo3.attach(21);     

  servo1.write(angle1);
  servo2.write(angle2);
  servo3.write(angle3);

  Serial.println("ESP32 3-Servo Control Ready");
}

void loop() {
  while (Serial.available() > 0) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      parseData(inputString);
      inputString = "";
    } else {
      inputString += inChar;
    }
  }
}

void parseData(String data) {
  int firstComma = data.indexOf(',');
  int secondComma = data.indexOf(',', firstComma + 1);

  if (firstComma > 0 && secondComma > firstComma) {
    int x = data.substring(0, firstComma).toInt();
    int y = data.substring(firstComma + 1, secondComma).toInt();
    int z = data.substring(secondComma + 1).toInt();

    // Constrain values between 0 and 180 degrees
    x = constrain(x, 0, 180);
    y = constrain(y, 0, 180);
    z = constrain(z, 0, 180);

    // Move the servos
    servo1.write(180 - x); 
    servo2.write(180 - y);
    servo3.write(z);

    // Debug print
    Serial.print("Servo1: ");
    Serial.print(x);
    Serial.print(" | Servo2: ");
    Serial.print(y);
    Serial.print(" | Servo3: ");   
    Serial.println(z);
  }
}
