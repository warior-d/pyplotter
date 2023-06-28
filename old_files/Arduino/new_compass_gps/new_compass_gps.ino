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

HMC5883L compass;
MPU6050 mpu;

float heading1;
float heading2;
float heading_med;
float heading_between;


int8_t TEMPERATURE_WATER = 17;


float GLOBAL_DEPTH;
int COURSE_HMC = 0;
int TIME_GET_COURSE = 100; //время опроса датчика
boolean READY_WRITE = false;
#define DEBUG 0
unsigned long start_hmc;
unsigned long start_depth;
int TIME_GET_DEPTH = 100; //время опроса датчика



//SoftwareSerial mySerial(7,6); // RX, TX
unsigned char data[4]={};
float distance;


void setup()
{
  Serial.begin(9600);

  ss.begin(9600);

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

  //mySerial.begin(9600); 
}




void loop()
{
  if (millis() - start_hmc >= TIME_GET_COURSE){
    getMeasure();
    start_hmc = millis();
  }

  if (ss.available() > 0) {
    char c = ss.read();
    PrintString(c);
  }


/*
  if (mySerial.available() > 0) {
    do{
     for(int i=0;i<4;i++)
     {
       data[i]=mySerial.read();
     }
  }while(mySerial.read()==0xff);

  mySerial.flush();

  if(data[0]==0xff)
    {
      int sum;
      sum=(data[0]+data[1]+data[2])&0x00FF;
      if(sum==data[3])
      {
        distance=(data[1]<<8)+data[2];
        if(distance>30)
          {
           Serial.print("distance=");
           Serial.print(distance/10);
           Serial.println("cm");
          }else 
             {
               Serial.println("Below the lower limit");
             }
      }else Serial.println("ERROR");
     }
     delay(100);
  }
*/
  
}


void PrintString(char c)
{
  static int pos;
  static char Buffer[120];
  char strFound[10] = "$GPRMC";
  char strCourse[10] = "GPVTG";
  char* is;
  //char beginStr[20] = "$SDDBT,,,";
  char beginStr[20] = "$SDDBT,64.6,f,";
  char endStr[20] = ",M,10.77,F*32";


  if (pos >= 120) {
    pos = 0;
    READY_WRITE == true;
  }

  if (c == '$' && READY_WRITE == false) {
    pos = 0;
    Buffer[pos] = c;
    READY_WRITE = true;
  }

  if (c != '$' && READY_WRITE == true && c != '\r' && c != '\n') {
    pos = pos + 1;
    Buffer[pos] = c;
  }

  if ((c == '\r' || c == '\n') && READY_WRITE == true) {
    ss.flush();
    READY_WRITE = false;
    pos = pos + 1;
    Buffer[pos] = '\0';

    is = strstr(Buffer, strFound); //значит в Buffer набралась строка $GPRMC,112309.00,A,5540.93083,N,03752.72685,E,0.588,42,190822,,,D*70

    //если была строка "GPRMC"
    if (is > 0) {
      //char strFound[150] = "$GPRMC,112309.00,A,5540.93083,N,03752.72685,E,0.588,42,190822,,,D*70";
      boolean strt = false;
      char okstr[150] = "";
      int zpt = 0;
      char curs[10];
      itoa(COURSE_HMC, curs, DEC);
      int len = strlen(Buffer);
      for(int i = 0; i < len; i++){
        int qnt = strlen(okstr);
        
        if(Buffer[i] == ','){
          zpt++;
        }
        if(zpt==8 && strt == false){
          strt = true;
          okstr[qnt] = ',';
          strcat(okstr, curs);
          
        }
        if(zpt<8 || zpt>=9){
          okstr[qnt] = Buffer[i];
        }
      }
      /**
       * В DrDepth возможны:
       * GP GGA
       * GP RMC
       * GP GLL
       * 
         Печатать будем ТОЛЬКО
         - GPGLL строку (координаты) - как есть
         - GPVTG строку (курс + скорость) - подставляем курс, скорость не трогаем
         - SDDBT строку сотворяем заново сами :)
      */

      //Serial.println(Buffer);
      Serial.println(okstr);
      float ost = random(0, 10);
      float ost100 = random(0, 99);
      float dist_cm = ost/10;
      byte base = random(0, 3);
      float all_depth = GLOBAL_DEPTH; //base + dist_cm + ost100/100;
      //Serial.println("$SDDBT,64.6,f,19.09,M,10.77,F*32");
      Serial.print(beginStr); Serial.print(all_depth, 2); Serial.println(endStr);
    }
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
    
    COURSE_HMC = int(before_heading_med);
    //Serial.println(before_heading_med);
    
    if (before_heading_between < 30){
      heading_med = before_heading_med;
    }
  }




  // Convert to degrees
  heading1 = heading1 * 180/M_PI; 
  heading2 = heading2 * 180/M_PI; 

  /* Output
  Serial.print(heading1);
  Serial.print("  :   ");
  Serial.print(heading2);
  Serial.print("  :   ");
  Serial.println(heading_med);
*/
  


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




/*
void getDepth()
{
  int base = random(1, 10);
  GLOBAL_DEPTH = base + 0.21;
}
*/
