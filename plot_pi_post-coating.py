# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 12:52:50 2023

@author: heibach
"""


from foubase import connection, measurements, devices

#connex = connection.Mysql_Connection("foubase","heibach")
#connex.connect()

username = 'chen'
host = "172.16.29.181"
name_db='foubase'
connex = connection.Mysql_Connection(username=username, host=host, name_db=name_db) # OR jones gets his own DB account
#connex.connect("1234")# enter pw here
connex.connect("1q2w3e4r")# enter pw here

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
#%%
templ = {"MasksetName":"MPW27", "Bar":"C_4","DeviceType":"HHI_DFB"}
devs_ = devices.get_devices_fromTemplate_al(templ, connex)
devs = devices.load_measurements_deviceList_al(connex, devs_)
wafername = "MPW27#152"
devs_comp = [d for d in devs if 
             len([m for m in d.measurements if m.meas_attrs["MeasurementType"]=="pi" 
                  and "pd_ref," in m.meas_attrs["Comments"] and m.meas_attrs["WaferName"]==wafername])>1 ]
devs_comp = sorted(devs_comp, key = lambda x:(x["WL_L"], x["yPos"]))

chp = devs_comp[0].get_chip_al()
chp_xmin = chp["xPos"]
chp_xmax = chp["xPos"]+chp["Length"]
chp_ymin = chp["yPos"]
chp_ymax = chp["yPos"]+chp["Width"]

comment_string = "2nd pass"
#%%
for i,d in enumerate(devs_comp[32:33]):
    r = (i//5)%4
    c = i%5
    meas_pre = [m for m in d.measurements if m.meas_attrs["WaferName"]==wafername 
                and "pd_ref," in m.meas_attrs["Comments"] and comment_string
                not in m.meas_attrs["Comments"]][0]
    meas_post = [m for m in d.measurements if m.meas_attrs["WaferName"]==wafername 
                and "pd_ref," in m.meas_attrs["Comments"] and comment_string
                in m.meas_attrs["Comments"]][0]
    if r==c==0:
        fig, ax= plt.subplots(4,5, figsize=(35,27))
    fig.suptitle(f"{d['Bar']}, {wafername}", fontweight = "bold")
    
    axx = ax[r,c].twiny()
    axy = axx.twinx()
    axx.set_xlim(0, (chp_xmax-chp_xmin)/1e3)
    axx.xaxis.tick_top()
    axy.set_ylim(0, (chp_ymax-chp_ymin)/1e3)
    axy.grid(visible=False)
    axx.grid(visible=False)
    if r == 0:
        axx.set_xlabel("x Position on Chip [mm]", fontweight = "bold")
    if c == 4:
        axy.set_ylabel("y Position on Chip [mm]", fontweight = "bold")
    d_x = d["xPos"]-chp_xmin
    d_y = d["yPos"]-chp_ymin
    
    ax[r,c].plot(meas_pre.datasets[0][0]*1e3, meas_pre.datasets[0][1]*1e3, color = plt.cm.viridis(0.2))
    ax[r,c].plot(meas_post.datasets[0][0]*1e3, meas_post.datasets[0][1]*1e3, color = plt.cm.viridis(0.5), linestyle="dotted", linewidth = 2.5)
    ax[r,c].set_title(f"{int(d['WL_L']*1e9)} nm")
    d_axpos = (d_x/(chp_xmax-chp_xmin)*ax[r,c].get_xlim()[1], d_y/(chp_ymax-chp_ymin)*ax[r,c].get_ylim()[1])
    ax[r,c].scatter(*d_axpos, color = "r", marker = "x")
    if r==3:
        ax[r,c].set_xlabel("Laser Current [mA]", fontweight = "bold")
    if c==0:
        ax[r,c].set_ylabel("Laser Power [mW]", fontweight = "bold")
    if c ==0 and r ==0:
        handles = [Line2D([0],[0], color = plt.cm.viridis(0.2), label = "1st Sweep"), Line2D([0],[0], color = plt.cm.viridis(0.5), linestyle = "dotted", linewidth = 2.5,label = "2nd Sweep"), plt.scatter([0],[0], color = "r", marker = "x", label = "Device Position")]
        ax[r,c].legend(handles = handles, loc = "upper left")

    plt.show()