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
#include <SoftwareSerial.h>
SoftwareSerial ss(4, 5); //4 - белоголубой

#define TRIG 10 //Module pins
#define ECHO 11

HMC5883L compass;
MPU6050 mpu;

float heading1;
float heading2;
float heading_med;
float heading_between;



float GLOBAL_DEPTH;
int COURSE_HMC = 0;
int TIME_GET_COURSE = 100; //время опроса датчика

unsigned long start_hmc;
unsigned long start_depth;
int TIME_GET_DEPTH = 100; //время опроса датчика

const int BUFFER_SIZE = 100;
char buf[BUFFER_SIZE];






int8_t TEMPERATURE_WATER = 17;










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

  ss.begin(9600);
  ss.setTimeout(10);

  //pinMode(TRIG, OUTPUT);
  //pinMode(ECHO, INPUT);
  
}




void loop()
{
  if (millis() - start_hmc >= TIME_GET_COURSE){
    getMeasure();
    start_hmc = millis();
  }

  if (ss.available() > 0) {

    int rlen = ss.readBytesUntil('\n', buf, BUFFER_SIZE);
    PrintString(rlen);
  }
  
  //Serial.println(getDepth(0));
}


float getDepth(boolean typeSolid)
{
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(12);
  digitalWrite(TRIG, LOW);
  
  unsigned long distance_sm = pulseIn(ECHO, HIGH, 20000); //таймаут. За 34.4 мс сигнал в воде пройдет 50 метров. 

  float tempKoef = getSpeedKoeff(TEMPERATURE_WATER, typeSolid); //0 - это воздух. Для Воды - 1
  
  float distance = distance_sm/tempKoef/2;

  return distance;
}



float getSpeedKoeff(int8_t currTemp, boolean typeSolid)
{
  float Koeff;
  if(typeSolid == 1){
    if (currTemp < 5) {
      Koeff = 7.0;
    }
    else if (currTemp >= 33) {
      Koeff = 6.5;
    }
    else if (currTemp >= 5 && currTemp < 11) {
      Koeff = 6.9;
    }
    else if (currTemp >= 11 && currTemp < 17) {
      Koeff = 6.8;
    }
    else if (currTemp >= 17 && currTemp < 24) {
      Koeff = 6.7;
    }
    else if (currTemp >= 24 && currTemp < 33) {
      Koeff = 6.6;
    }
    else if (currTemp >= 33) {
      Koeff = 6.5;
    }
  }
  else if(typeSolid == 0){
    Koeff = 29.0;
  }
  return Koeff;
}




void PrintString(int rlen)
{
    //Serial.println(buf);
    char* is;
    char strFound[10] = "$GPRMC";
    char beginStr[20] = "$SDDBT,64.6,f,";
    char endStr[20] = ",M,10.77,F*32";  
    is = strstr(buf, strFound);
  
    if ( (is > 0) && (strncmp(buf, strFound, 6) == 0) ) {
      //char strFound[150] = "$GPRMC,112309.00,A,5540.93083,N,03752.72685,E,0.588,42,190822,,,D*70";
      boolean strt = false;
      char okstr[150] = "";
      int zpt = 0;
      char curs[10];
      itoa(COURSE_HMC, curs, DEC);

      for(int i = 0; i < rlen; i++){
        int qnt = strlen(okstr);
        
        if(buf[i] == ','){
          zpt++;
        }
        if(zpt==8 && strt == false){
          strt = true;
          okstr[qnt] = ',';
          strcat(okstr, curs);
          
        }
        if(zpt<8 || zpt>=9){
          okstr[qnt] = buf[i];
        }
      }

      Serial.println(okstr);
      float all_depth = GLOBAL_DEPTH + 5.23; //base + dist_cm + ost100/100;
      //Serial.println("$SDDBT,64.6,f,19.09,M,10.77,F*32");
      Serial.print(beginStr); Serial.print(all_depth, 2); Serial.println(endStr);
    }

  memset(buf, 0, sizeof(buf));
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
    
    COURSE_HMC = int(before_heading_med);
    //Serial.println(before_heading_med);
    
    if (before_heading_between < 30){
      heading_med = before_heading_med;
    }
  }

  // Convert to degrees
  heading1 = heading1 * 180/M_PI;
  heading2 = heading2 * 180/M_PI;

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
