import time

import numpy as np
from PIC_Lab_instruments.instruments.sourcemeter import HHI_PIConnect
import matplotlib.pyplot as plt

from measurement_driver import *

ip_PIConnet = '172.16.32.252'

# test of HHI_PIConnect
pcx = HHI_PIConnect(ip_PIConnet)
pcx1 = PIConnet(ip_PIConnet)
# input_value = np.arange(0.5, 100.1, 0.5) * 1e-3 #A
input_value = np.arange(0, 5., 0.025)  # '* 1e-3 #V
input_value2 = np.arange(0, 5000, 25)

mes_value = np.zeros(len(input_value)) #Ergebnis abspeichern
print("input length: %d" % (len(input_value)))
# print(input_value)

# %%

# test start
time_start = time.time()


for (ii, val) in enumerate(input_value):
    pcx.setlevel('vs1', val)
    mes_value[ii] = pcx.measure('vs1', 'i')

time_ende = time.time()

print('time to measure: %d' % (time_ende - time_start))

plt.figure(1, (4, 3))
plt.plot(input_value, mes_value)
plt.title("HHI_PIConnect")
# plt.plot(input_value2, mes_value)
plt.show()

# test end

# %%

# test PIConnect

input_value2 = np.arange(0, 5000, 25)

# test start
time_start = time.time()
mes_vec = pcx1.channel_sweep("vs1", input_value2)
time_ende = time.time()

print("time for PIConnect class: %f" % (time_ende - time_start))

plt.figure(1, (4, 3))
plt.plot(input_value2, mes_vec)
plt.title("PIConnect")
# plt.plot(input_value2, mes_value)
plt.show()
# test end

# %%

multi_mess_val = pcx1.multi_channel_set_get(("vs1", "vs2", "vs3"), 5000)
print(multi_mess_val)

pcx1.multi_channel_set(("vs1", "vs2", "vs3"), 3000)
print(pcx1.multi_channel_get(("vs1", "vs2", "vs3")))

multi_sweep_val = pcx1.multi_channel_sweep(("vs1", "vs2"), input_value2)
print(multi_sweep_val)

# %%
versuch = np.array([1, 2, 3, 4, 5])
zeit_array = np.zeros(len(versuch))
zeit_array2 = np.zeros(len(versuch))

for i in range(len(versuch)):
    time_start = time.time()
    for (ii, val) in enumerate(input_value):
        pcx.setlevel('vs1', val)
        mes_value[ii] = pcx.measure('vs1', 'i')
    time_ende = time.time()

    zeit_array[i] = time_ende - time_start

for i in range(len(versuch)):
    time_start = time.time()
    mes_vec = pcx1.channel_sweep("vs1", input_value2)
    time_ende = time.time()

    zeit_array2[i] = time_ende - time_start

print("finished ")

plt.figure(1, (4, 3))
plt.plot(versuch, zeit_array, label="obj1")
plt.plot(versuch, zeit_array2, label="obj2")
plt.title("Plot 1")
plt.show()

# %% multi_channel_sweep test

time_start = time.time()
result_arr = pcx1.multi_channel_sweep(("vs1", "vs2", "vs3"), input_value2)
time_ende = time.time()

for i in range(result_arr.shape[0]):
    plt.figure(i, (4, 3))
    plt.plot(input_value2, result_arr[i])
    plt.show()

print("elapsed time: %d" % (time_ende - time_start))

# %% multi_channel_sweep time test
versuch = np.array([1, 2, 3, 4, 5])
zeit_array3 = np.zeros(len(versuch))

for i in range(len(versuch)):
    time_start = time.time()
    result_arr = pcx1.multi_channel_sweep(("vs1", "vs2", "vs3"), input_value2)
    time_ende = time.time()

    zeit_array3[i] = time_ende - time_start

fig = plt.figure(6, (4, 3))
plt.plot(versuch, zeit_array3)
plt.show()

#%%

versuch = np.array([1, 2, 3, 4, 5])
zeit_array = np.zeros(len(versuch))
zeit_array2 = np.zeros(versuch)
print(zeit_array)