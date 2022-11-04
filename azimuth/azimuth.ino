#include <QMC5883LCompass.h>

QMC5883LCompass compass;

void setup() {
  Serial.begin(9600);
  compass.init();
  compass.setCalibration(-1462, 1711, -1596, 1578, -1648, 1558);
  compass.setSmoothing(10,true); 
}

void loop() {

  int a;
  
  compass.read();
  
  a = compass.getAzimuth();

  Serial.print(" Azimuth: ");
  Serial.print(a);
  Serial.println();
  delay(250);
}
