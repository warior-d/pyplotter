import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata


data_url = 'djer.csv'
#contour_data = pd.read_csv(data_url)
data = np.genfromtxt(data_url,
                    delimiter=",", dtype=float)

x = data[:,0]
y = data[:,1]
z = data[:,2]


print(y)