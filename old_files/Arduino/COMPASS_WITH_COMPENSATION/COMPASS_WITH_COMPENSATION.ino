#include <Wire.h>
#include <HMC5883L.h>
#include <MPU6050.h>
#include <String.h>


HMC5883L compass;
MPU6050 mpu;

float heading1;
float heading2;

#define Filter_read 200  //!!! только четное число сколько читать значений из АЦП для работы фильтра.Выбрано 20 для частоты 10 Гц или 200 для 1Гц
#define Filter_get  1  //!!! только четное число или единица сколько взять  значений  для расчета среднего фильтром
long filter_heading2;  //для получения множества значений raw из регистра преобразования АЦП после чтения по значениям Filter_read и Filter_get

String str_hdm;
String STR_CRC_XOR ="";


void setup()
{
  Serial.begin(9600);
  Serial.println("HMC5883L_compensation_MPU6050_next_7_1000ms.ino");//*******************************************************************************

  // Initialize MPU6050
  while(!mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_2G))
  {
    delay(500);
  }

  // Initialize Initialize HMC5883L
  while (!compass.begin())
  {
    delay(500);
  }

  // Set measurement range
  compass.setRange(HMC5883L_RANGE_1_3GA);

  // Set measurement mode
  compass.setMeasurementMode(HMC5883L_CONTINOUS);

  // Set data rate
  compass.setDataRate(HMC5883L_DATARATE_30HZ);

  // Set number of samples averaged
  compass.setSamples(HMC5883L_SAMPLES_8);

  // Set calibration offset. See HMC5883L_calibration.ino
  compass.setOffset(95,-117,-3); 
}


void loop()
{
  filter_heading_calc ();
  hdmSentenceMake();
  Serial.print("heading1: ");
  Serial.print(heading1);
  Serial.print(":::");
  Serial.print("heading2: ");
  Serial.print(heading2);
  Serial.print(":::"); 
  Serial.println(str_hdm);
}















// No tilt compensation
float noTiltCompensate(Vector mag)
{
  float heading = atan2(mag.YAxis, mag.XAxis);
  return heading;
}
 

// Tilt compensation
float tiltCompensate(Vector mag, Vector normAccel)
{
  // Pitch & Roll 
  
  float roll;
  float pitch;
  
  roll = asin(normAccel.YAxis);
  pitch = asin(-normAccel.XAxis);

  if (roll > 0.78 || roll < -0.78 || pitch > 0.78 || pitch < -0.78)
  {
    return -1000;
  }
  
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

// Correct angle
float correctAngle(float heading)
{
  if (heading < 0) { heading += 2 * PI; }
  if (heading > 2 * PI) { heading -= 2 * PI; }

  return heading;
}





 void get_heading(){
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
 
  
  // Correct for heading < 0deg and heading > 360deg
  heading1 = correctAngle(heading1);
  heading2 = correctAngle(heading2);

  // Convert to degrees
  heading1 = heading1 * 180/M_PI; //noTiltCompensate(mag)
  heading2 = heading2 * 180/M_PI; //tiltCompensate(mag, acc)
   
 }

//______________________________________________________________________________________________________________________________
void filter_heading_calc () {                  // подпрограмма считывания и фильтрации значений  
  
  float sortedValues[Filter_read];              //назначили  массив с sortedValues[Filter_read] 
  for (int i = 0; i < Filter_read; i++) {       //цикл от 0 до Filter_read
      
again: get_heading();                            // идем на подпрограмму получения данных из АЦП в переменную ltw
      
      if ((heading2 / heading2) != 1 ) {
        //Serial.println("*************fuck***************");
        goto again;
      }
    
      
      float value = heading2 ;                         //value получает значение одного измерения raw ads  
      int j;                                    //переменная "j" куда вставлять значение при сортировке
      if (value < sortedValues[0] || i == 0) {  //если полученое значение valve < sortedValues[0] или это самое начало "i",то 
         j = 0;                                 //"j"= 0 это первая позиция 
      }                                         //конец  if
       else {                                   //иначе
          for (j = 1; j < i; j++) {             //цикл j от 1 до j < i искать "j"
           if (sortedValues[j - 1] <= value && sortedValues[j] >= value) { //ищем место"j" в sortedValues[]куда вставить value
             break;                                                        //"j" найдено,остановить выполнение цикла
           }                                    //конец if
          }                                     //конец цикла j
       }                                        //конец else
         
       for (int k = i; k > j; k--) {            //все значения от "i" до "j" (вниз к--) нужно поднять на одну позицию вверх
       sortedValues[k] = sortedValues[k - 1];   //чтобы освободить место "j" для valve
       }                                        //конец цикла
       sortedValues[j] = value;                 //вставить считаное valve в sortedValues[] в позицию "j"
  }                                             //конец цикла от 0 до Filter_read
  
   
 //расчет среднего знач из Filter_get. Эти значения взяты после отброса лишних значений
  float filter_heading = 0;
  
  if (Filter_get%2 == 0)                       //если Filter_get четное, то считаем так
     // четное
      { 
      for (int i = Filter_read / 2 - Filter_get/2; i < (Filter_read / 2 + Filter_get/2); i++) {
      filter_heading += sortedValues[i];
      }
      heading2 = filter_heading / Filter_get;
      }
  if (Filter_get == 1)                        ////если Filter_get =1, то не считаем а берем из середины одно значение
  {
    byte nomb = Filter_read / 2;  
    heading2 = sortedValues[nomb];
  }
  
     
}
//__________________________________________________________________________________________________
 void hdmSentenceMake(){
   char Sentence [20];
   byte XOR;
   STR_CRC_XOR ="";
   str_hdm = "$HCHDM,";
   str_hdm += String(heading2,1);
   str_hdm += ",M*";
   str_hdm.toCharArray(Sentence, str_hdm.length() + 1);
   
   //считать XOR все символы кроме $ , и стоп на *
   int i;
   for (XOR = 0, i = 0; i < sizeof(Sentence); i++)
   {
   if (Sentence[i] == '*') break;
   if (Sentence[i] != '$' ) XOR ^= Sentence[i];
  
   }
  
   if (XOR < 0x10) str_hdm +="0";  
   STR_CRC_XOR = String(XOR, HEX);
   STR_CRC_XOR.toUpperCase();
   str_hdm += STR_CRC_XOR;
  
    
 }
//__________________________________________________________________________________________________
