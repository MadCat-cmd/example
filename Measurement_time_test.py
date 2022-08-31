import numpy as np
import time
from PIC_Lab_instruments.instruments.sourcemeter import HHI_PIConnect
import matplotlib.pyplot as plt

from measurement_driver import *


ip_PIConnet = '172.16.32.252'

input_value = np.arange(0.5, 100.1, 0.5) * 1e-3 #A
input_value2 = input_value * 1000
input_value2 = input_value2.astype(int)
#print(input_value2)
mes_value = np.zeros(len(input_value))

pcx = HHI_PIConnect(ip_PIConnet)

time_start = time.time()
process_start_time = time.process_time()


pcx.setlevel('vs1', 1)
val = pcx.measure('vs1', 'i')

print('input length: %d' %(len(input_value)))


for (ii, val) in enumerate(input_value):
    pcx.setlevel('vs1', val)
    mes_value[ii] = pcx.measure('vs1', 'i')


process_ende_time = time.process_time()
time_ende = time.time()

print('process time to measure %f' %(process_ende_time-process_start_time))
print('time to measure: %d' %(time_ende - time_start))


conn_test()

'''
set_vs1(5000)
print('Messung: ' + get_vs1())

time_start = time.time()
for (ii, val) in enumerate(input_value):
    set_vs1(val)
    mes_value[ii] = get_vs1()

time_ende = time.time()

print("Measurement Function time: %f" %(time_ende - time_start))
'''


pcx = PIConnet("172.16.32.252")
'''
#object set get test
time_start = time.time()
for (ii, val) in enumerate(input_value):
    pcx.set_value("vs1", val)
    mes_value[ii] = pcx.get_value("vs1")

time_ende = time.time()
print("Measurement Object set/get time new: %f" %(time_ende - time_start))

#object set_get test

time_start = time.time()
for (ii, val) in enumerate(input_value):
    mes_value[ii] = pcx.set_get_value("vs1", val)

time_ende = time.time()
print("Measurement Object set_get time new: %f" %(time_ende - time_start))
'''


time_start = time.time()
mes_vec = pcx.channel_sweep("vs1", input_value2)
time_ende = time.time()

print("new sweep time: %f" %(time_ende - time_start))

plt.figure(1, (4, 3))
plt.plot(input_value2, mes_vec)
#plt.plot(input_value2, mes_value)
plt.show()


pcx2 = PIConnect2(ip_PIConnet)
pcx2.set_channel_cmd("vs1", input_value2)
time_start = time.time()
result_array = pcx2.channel_sweep("vs1")
time_stop = time.time()
print("pcx2 sweep: %d" %(time_stop-time_start))

'''
plt.figure(2, (4, 3))
plt.plot(input_value, result_array)
plt.show()
'''

