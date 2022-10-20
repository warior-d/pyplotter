from dateutil import parser
from datetime import *

ti = '210906.00'
tim = ti.split('.')

time = tim[0]
timeNorm = datetime.strptime(time, '%H%M%S') + timedelta(hours=3)
t = str(timeNorm)

print(str(timeNorm.time()))