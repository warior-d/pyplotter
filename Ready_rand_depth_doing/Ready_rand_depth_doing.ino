#include <SoftwareSerial.h>
#include <QMC5883LCompass.h>
SoftwareSerial ss(4, 5); //4 - белоголубой
QMC5883LCompass compass;
float GLOBAL_DEPTH;
int COURSE_HMC = 0;
int TIME_GET_COURSE = 100; //время опроса датчика
boolean READY_WRITE = false;
#define DEBUG 0
unsigned long start_hmc;

/*
  char* myStrings[]={
  "$GPGLL,5540.91588,N,03752.72131,E,211606.00,A,A*67",
  "$SDDBT,,,19.06,M,10.77,F*3D",
  "$TIME0,C1*7B"};
*/


/**
   Описание протокола
   https://wiki.iarduino.ru/page/NMEA-0183/

   $SDDBT,64.6,f,19.06,M,10.77,F*3D
   $TIME0,C1*7B
   Можно и так:
   $SDDBT,,,19.06,M,10.77,F*3D

  1. $ - символ начала пакета (1 байт)
  2. SDDPT — команда (5 байт)
  3. x.x - глубина в метрах, в дробном десятичном ASCII формате
  4. x.x - расстояние от передатчика до ватерлинии, в дробном
  десятичном ASCII формате
  5. * - разделитель контрольной суммы
  6. hh - контрольная сумма (2 байта)
  7. <CR><LF> - символы конца пакета (2 байта)


  НАСТРОЙКИ в DrDepth!

  COM5
  9600

  NMEA Sentence:
  GPS:      GPGLL
  Sounder:  SDDBT

  !!! Ignore NMEA cheksum

  Course vector

  RMC - Рекомендуемый минимум навигационных данных.
  VTG - Скорость и курс относительно земли.

*/



void setup() {
  Serial.begin(9600);
  ss.begin(9600);
  compass.init();
  compass.setCalibration(-1462, 1711, -1596, 1578, -1648, 1558);
  compass.setSmoothing(10,true);
}



void loop() {
  //Serial.println("$GPGLL,5504.10546,N,03848.80004,E,211606.00,A,A*67");

  if (millis() - start_hmc >= TIME_GET_COURSE){
    compass.read();
    COURSE_HMC = compass.getAzimuth();
    start_hmc = millis();
  }


  if (ss.available() > 0) {
    char c = ss.read();
    PrintString(c);
  }

}

void getDepth()
{
  int base = random(1, 10);
  GLOBAL_DEPTH = base + 0.21;
}

void PrintString(char c)
{
  static int pos;
  static char Buffer[120];
  char strFound[10] = "GPRMC";
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
      float all_depth = base + dist_cm + ost100/100;
      //Serial.println("$SDDBT,64.6,f,19.09,M,10.77,F*32");
      Serial.print(beginStr); Serial.print(all_depth, 2); Serial.println(endStr);
    }
  }

}
