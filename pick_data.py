# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 15:47:36 2021

@author: fou
"""

import os, datetime, re, copy, sys, keyring, time
from foubase import connection, devices, measurements, evaluations, chips, common
import pympw


import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

# plt.style.use('C:/Users/hogan/Anaconda3/Lib/site-packages/foubase/fouPlotStyle.mplstyle')
scale_factor = 0.6

#%%access

#username = 'hogan'
username = 'chen'
host = "172.16.29.181"
#name_db='foubase'
name_db = "fouwaste"
connex = connection.Mysql_Connection(username=username, host=host, name_db=name_db) # OR jones gets his own DB account
#connex.connect("1234")# enter pw here
connex.connect("1q2w3e4r")# enter pw here

#%% device Template
wafernames = ["MPW25#101"]
wafernames = ["MPW22#113"]
#bar = "A_3"
bar = "A_1"


devices_template = devices.Device(connex)
devices_template["MasksetName"] = wafernames[0].split('#')[0]
devices_template["Bar"] = bar

devices_found = devices.get_devices_fromTemplate(devices_template, connex)

devices_measured = devices.load_measurements_deviceList(connex, devices_found)

#%% get different measurement

VIs = []



for dev in devices_measured:

    for meas in dev.measurements:
        if meas.meas_attrs["MeasurementType"] == "vi":
            VIs.append(meas)



#%% plot

wafers =  ["MPW22#51"]

fig = plt.figure()
ax = fig.add_subplot(111)
# ax_twin = ax.twinx()


ax.set_xlabel(u"Current [mA]")
ax.set_ylabel(u"Voltage [V]", color = cm.viridis(0.3))
ax.set_title(f"VI WVel {wafers} {bar}") #" Modejumps: " + str(eva.eval_attrs["Modejumps"]))

for mm, meas in enumerate(VIs):

    if meas.meas_attrs["WaferName"] not in wafers:
        continue

    ax.plot(meas.datasets[0][0] * 1e3, meas.datasets[0][1],
            color=cm.turbo((round(meas.device['WL_L'] * 1e9) - 1520) / 100),
            label=f"{round(meas.device['WL_L'] * 1e9)} nm",
            linewidth=1)  # , label =  f"{int(meas.device['WL_L']*1e6)} nm")

    print("Meas Attribute: {}".format(meas.meas_attrs["WaferName"]))

plt.show()
