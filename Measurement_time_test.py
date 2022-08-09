import numpy as np
import time
from PIC_Lab_instruments.instruments.sourcemeter import HHI_PIConnect
import matplotlib.pyplot as plt


ip_PIConnet = '192.168.2.116'

input_value = np.arange(0.5, 50.1, 0.5) * 1e-3 #A
mess_value = np.zeros(len(input_value))

pcx = HHI_PIConnect(ip_PIConnet)
'''
start_time = time.process_time()
for (ii, val) in enumerate(input_value):
    pcx.setlevel('vc1', val)
    mess_value[ii] = pcx.measure('vc1', 'i')

ende_time = time.process_time()
'''

plt.figure(1, (4,3))
plt.plot(input_value, input_value)
plt.show()







