import numpy as np
import time
from PIC_Lab_instruments.instruments.sourcemeter import HHI_PIConnect
import matplotlib.pyplot as plt

from measurement_driver import *


ip_PIConnet = '172.16.32.252'

input_value = np.arange(0.5, 50.1, 0.5) * 1e-3 #A
mess_value = np.zeros(len(input_value))

pcx = HHI_PIConnect(ip_PIConnet)

time_start = time.time()
process_start_time = time.process_time()


pcx.setlevel('vs1', 1)
val = pcx.measure('vs1', 'i')
print(val)

print('input length: %d' %(len(input_value)))


for (ii, val) in enumerate(input_value):
    pcx.setlevel('vs1', val)
    mess_value[ii] = pcx.measure('vs1', 'i')


process_ende_time = time.process_time()
time_ende = time.time()

print('whole process time old: %f' %(process_ende_time-process_start_time))
print('wohle time old: %d' %(time_ende - time_start))


conn_test()


set_vs1(5000)
print('Messung: ' + get_vs1())

time_start = time.time()
for (ii, val) in enumerate(input_value):
    set_vs1(val)
    mess_value[ii] = get_vs1()

time_ende = time.time()

print("Measurement Function time new: %f" %(time_ende - time_start))


plt.figure(1, (4,3))
plt.plot(input_value, mess_value)
plt.show()

pcx = PIConnet("172.16.32.252")

time_start = time.time()
for (ii, val) in enumerate(input_value):
    pcx.set_value(val)
    mess_value[ii] = pcx.get_value()

time_ende = time.time()
print("Measurement Object time new: %f" %(time_ende - time_start))



