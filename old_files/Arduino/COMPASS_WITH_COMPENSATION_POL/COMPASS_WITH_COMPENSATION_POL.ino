/*
  Tilt compensated HMC5883L + MPU6050 (GY-86 / GY-87). Output for HMC5883L_compensation_processing.pde
  Read more: http://www.jarzebski.pl/arduino/czujniki-i-sensory/3-osiowy-magnetometr-hmc5883l.html
  GIT: https://github.com/jarzebski/Arduino-HMC5883L
  Web: http://www.jarzebski.pl
  (c) 2014 by Korneliusz Jarzebski
*/

#include <Wire.h>
#include <HMC5883L.h>
#include <MPU6050.h>

HMC5883L compass;
MPU6050 mpu;

float heading1;
float heading2;
float heading_med;
float heading_between;


int COURSE_HMC = 0;
int TIME_GET_COURSE = 100; //время опроса датчика
unsigned long start_hmc;


void setup()
{
  Serial.begin(9600);

  while(!mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_2G))
  {
    delay(500);
  }
  // Enable bypass mode
  mpu.setI2CMasterModeEnabled(false);
  mpu.setI2CBypassEnabled(true) ;
  mpu.setSleepEnabled(false);
  
  while (!compass.begin())
  {
    delay(500);
  }
  compass.setRange(HMC5883L_RANGE_1_3GA);
  compass.setMeasurementMode(HMC5883L_CONTINOUS);
  compass.setDataRate(HMC5883L_DATARATE_30HZ);
  compass.setSamples(HMC5883L_SAMPLES_8);

  compass.setOffset(95,-117,-3);

  Serial.print("offcet: ");
  Serial.println(mpu.getAccelOffsetX());
}




void loop()
{
  if (millis() - start_hmc >= TIME_GET_COURSE){
    getMeasure();
    start_hmc = millis();
  }
}






void getMeasure(){

  // Read vectors
  Vector mag = compass.readNormalize();
  Vector acc = mpu.readScaledAccel();  

  // Calculate headings
  heading1 = noTiltCompensate(mag);
  heading2 = tiltCompensate(mag, acc);
  
  if (heading2 == -1000)
  {
    heading2 = heading1;
  }


  float declinationAngle = (11.0 + (43.0 / 60.0)) / (180 / M_PI);
  heading1 += declinationAngle;
  heading2 += declinationAngle;
  
  heading1 = correctAngle(heading1);
  heading2 = correctAngle(heading2);


  if (!isnan(heading1) and !isnan(heading2)){
    float medium_sin = sin(heading1) + sin(heading2);
    float medium_cos = cos(heading1) + cos(heading2);
    float medium_rad = atan2(medium_sin, medium_cos);
    medium_rad = correctAngle(medium_rad);
    float before_heading_med = medium_rad*180/M_PI;

    float between_rad = acos(cos(heading1)*cos(heading2) + sin(heading1)*sin(heading2));
    between_rad = correctAngle(between_rad);
    float before_heading_between = between_rad*180/M_PI;

    if (before_heading_between < 30){
      heading_med = before_heading_med;
    }
  }




  // Convert to degrees
  heading1 = heading1 * 180/M_PI; 
  heading2 = heading2 * 180/M_PI; 

  // Output
  Serial.print(heading1);
  Serial.print("  :   ");
  Serial.print(heading2);
  Serial.print("  :   ");
  Serial.println(heading_med);
}
























float noTiltCompensate(Vector mag)
{
  float heading = atan2(mag.YAxis, mag.XAxis);
  return heading;
}
 

float tiltCompensate(Vector mag, Vector normAccel)
{
  
  float roll;
  float pitch;
  
  roll = asin(normAccel.YAxis);
  pitch = asin(-normAccel.XAxis);

  
    // Some of these are used twice, so rather than computing them twice in the algorithem we precompute them before hand. 
  float cosRoll = cos(roll);
  float sinRoll = sin(roll);  
  float cosPitch = cos(pitch);
  float sinPitch = sin(pitch);
  
  // Tilt compensation
  float Xh = mag.XAxis * cosPitch + mag.ZAxis * sinPitch;
  float Yh = mag.XAxis * sinRoll * sinPitch + mag.YAxis * cosRoll - mag.ZAxis * sinRoll * cosPitch;
 
  float heading = atan2(Yh, Xh);
    
  return heading;
}


float correctAngle(float heading)
{
  if (heading < 0) { heading += 2 * PI; }
  if (heading > 2 * PI) { heading -= 2 * PI; }

  return heading;
}
