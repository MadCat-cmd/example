# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 11:48:03 2022

@author: cardenasgiraldo
"""

import os, datetime, re, copy, sys, keyring

sys.path.append(r"C:\Users\fou\Documents\Python Scripts")
sys.path.append(r"C:\Users\fou\Documents\Python Scripts\verhaegh\measurement_scripts")
sys.path.append(r"\\3WCJ423\Users\fou\Documents\Python Scripts\WV_MPW")


from PIC_Lab_instruments.sourcemeter.Keithley_260X         import Keithley_260X

# from pympw import Mover
from umf.measurements import VI

import numpy as np
import pyvisa as visa
import matplotlib.pyplot as plt
import sys

try:
    rm.last_status
except NameError:
    rm = visa.ResourceManager() 

#%% Create instruments
keithley1 = Keithley_260X(rm.open_resource("GPIB::26"))


dev_channel = 'a'


#%% do the good old DB stuff:
    
# from jofuncs import finddevice
from foubase import connection, measurements, devices, chips

username = 'giraldo'
host = "172.16.29.181"
name_db='foubase'
connex = connection.Mysql_Connection(name_db="foubase", username="giraldo", host="172.16.29.181")
connex.connect(password="12358")
#%%get devices from DB

device_template = devices.Device(connex)
device_template["MasksetName"]  = "MPW24"

# device_template["DeviceType"]   = "HHI_PDDC"
# device_template["DeviceType"]   = "HHI_DFB"
# device_template["DeviceType"]   = "HHI_EOBias"
# device_template["DeviceType"]   = "HHI_EOPMTWSection"
# device_template["DeviceType"]   = "HHI_PDRF"
# device_template["DeviceType"]   = "HHI_SOA"
# device_template["DeviceType"]   = "HHI_DBR"

# device_template["ChipNumber"]   = 1
# device_template["DeviceNumber"] = 1
# device_template["ChipName"]     = "MPW24_108"
# device_template["Bar"]          = "D_1"


devices_found = devices.get_devices_fromTemplate(device_template, connex)
#devices_found = [dev for dev in devlist if "twin" in dev["DeviceName"].lower()]          #for twin WG in EOBias section
#devices_found = [dev for dev in devlist if "twin" not in dev["DeviceName"].lower()]      #for solo WG in EOBias section
DUT = devices_found[0].get_chip()                                                         # get the ChipUT
DUT_ID = DUT["IDDevice"]
#DUT.plot([devices_found[0]["IDDevice"]])                                                 #Plot a map of the ChipUT

#%%I(V) sweep

'''INPUT'''

voltages = np.arange(-2,2.001, 0.01)
''''''''

keithley1.setup(channel     = dev_channel, supply_mode = "voltage",  i_limit     = 1,  v_limit     = 6.0, beeper = False)

currents = np.zeros_like(voltages)


keithley1.output(dev_channel, True)

for vv, voltage in enumerate(voltages):
    keithley1.setlevel(dev_channel, voltage)
    currents[vv] = keithley1.measure(dev_channel, 'i')

keithley1.output(dev_channel, False)


#%% V(I) sweep
'''INPUT'''
# currents = np.arange(0,0.1001, 0.0005)
# ''''''''
# keithley1.setup(channel = dev_channel, supply_mode = "current", i_limit = 0.5,  v_limit= 40.0, beeper = False)

# voltages = np.zeros_like(currents)

# keithley1.output(dev_channel, True)

# for cc, current in enumerate(currents):
#     keithley1.setlevel(dev_channel, current)
#     voltages[cc] = keithley1.measure(dev_channel, 'v')
    
# keithley1.output(dev_channel, False)


#%%plot

plt.rcParams["figure.dpi"] = 200

rescolor = plt.cm.viridis(.7)
vcolor = plt.cm.viridis(.4)
resistance = np.gradient(voltages)/np.gradient(currents)

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title("I(V) of " + DUT["DeviceName"].split('_')[1] + "#" + str(int(DUT["DeviceNumber"])))
#ax.set_title("I(V)")

#ax2 = ax.twinx()
ax.set_xlabel("Voltage [V]", fontweight='bold')  
ax.tick_params(axis='y', colors=vcolor)
#ax2.tick_params(axis='y', colors=rescolor)
ax.set_ylabel("Current [mA]", fontweight='bold',  color = vcolor)


ax.plot(voltages, currents*1e3, color = vcolor)
#ax2.plot(voltages, resistance, color = rescolor)



# ax2.grid(0)

#ax2.set_ylabel("Differential Resistance [Ω]", fontweight = "bold", color = rescolor)
#ax2.set_ylim(0,80)
#ax.set_ylim(-0.1, 30)
#ax.set_xticks(np.arange(0, 3.1, 0.5))
#ax.set_yticks(np.arange(0, 34e-3, 5e-3))

plt.pause(2)
# sys.exit()
#%% #%% save to DB:
DUT_test = devices.get_device_fromIDs([DUT_ID], connex)[0]
DUT_test.load_measurements()

before = len(DUT_test.measurements)

    
meas_vi = measurements.Measurement(connex, "vi")
for meas in [meas_vi]:
    meas.meas_attrs["WaferName"] = "MPW23#83"  # Masksetname + WAFERRUN #1,2,3...
    meas.meas_attrs["Date"] = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'%Y-%m-%d %H:%M:%S')
    meas.meas_attrs["Station"] = "PIC_Lab1"
    meas.meas_attrs["Temp"] = [20]
    meas.meas_attrs["Operator"] = "giraldo"
    meas.meas_attrs["Pulsewidth"] = 1.0
    meas.meas_attrs["Pulseperiod"] = 1.0
    meas.meas_attrs["PulseCW"] = 0
    meas.device = DUT
    
    meas.meas_attrs["Comments"] = "Actphast back grating"
    #hier kommentieren z.B. back or front grating
    
meas_vi.datasets.append([currents, voltages, ])  


# CHECK = input(f"--- Measured {DUT['DeviceName']}#{DUT['DeviceNumber']}, ENTER - continue")

meas_vi.write_sql()

DUT_test = devices.get_device_fromIDs([DUT_ID], connex)[0]
DUT_test.load_measurements()

after = len(DUT_test.measurements)
if after == before + 1:
    print('Successfully uploaded')
    
#%% Delete a Measurement:
# meas.meas_attrs["IDMeasuremen"] # get the Measurement ID as output
#measurements.delete_IDs_in_sql(connex,[meas_vi.meas_attrs["IDMeasurement"]])  # introduce (-1) and Enter, Delete I(V) Measurement
#measurements.delete_IDs_in_sql(connex,[meas.meas_attrs["IDMeasurement"]])     # introduce (-1) and Enter, Delete last Measurement in general