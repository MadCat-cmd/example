# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 17:41:37 2022

@author: heibach
"""

from foubase import measurements, devices, connection
import numpy as np
import matplotlib.pyplot as plt
connex = connection.Mysql_Connection("foubase","heibach")
connex.connect()
#%% build measurement lists

ms_name = "DONNY3"
dev_templ = {"MasksetName":ms_name}
devs = devices.get_devices_fromTemplate_al(dev_templ, connex)
devs = devices.load_measurements_deviceList_al(connex, devs)
measlist = [m for dev in devs for m in dev.measurements]
wafers = list(set([m.meas_attrs["WaferName"] for m in measlist if int(m.meas_attrs["WaferName"].split("#")[1]) > 109]))
measlist = [m for dev in devs for m in dev.measurements if m.meas_attrs["WaferName"] in wafers]
dev_templ_wgt = {"MasksetName":ms_name,"DeviceType":"HHI_WGT"}
devs = devices.get_devices_fromTemplate_al(dev_templ_wgt, connex)
devs = devices.load_measurements_deviceList_al(connex, devs)
measlist_wgt = [m for dev in devs for m in dev.measurements if m.meas_attrs["WaferName"] in wafers]
dev_templ_iso = {"MasksetName":ms_name, "DeviceType":"HHI_ISO"}
devs = devices.get_devices_fromTemplate_al(dev_templ_iso, connex)
devs = devices.load_measurements_deviceList_al(connex, devs)
measlist_iso = [m for dev in devs for m in dev.measurements if m.meas_attrs["WaferName"] in wafers]
#%% build loss-dictionaries
mmi121 = [m for m in measlist if "MMI" in m.meas_attrs["Comments"]]
pi121 = [m for m in measlist if m.meas_attrs["MeasurementType"]=="pi"]
wafers = list(set([m.meas_attrs["WaferName"] for m in measlist if int(m.meas_attrs["WaferName"].split("#")[1]) > 109]))
distdict = {"MPW26":{"MMI":1500, "WGT":2200, "ISO":2250}, "DONNY3":{"MMI":700,"WGT":1500, "ISO":1750}} #DONNY3 700, MPW26 1500


def dfb_from_mmi(d, measlist, wn):
    dist = distdict[wn.split("#")[0]]["MMI"]
    dfb_measlist = [m for m in measlist if np.isclose(m.device["yPos"], d["yPos"], atol = 250) and np.isclose(m.device["xPos"], d["xPos"]-dist, atol=250) and m.meas_attrs["WaferName"]==wn]
    pdout = [m for m in dfb_measlist if m.meas_attrs["Comments"] == "pd_out"][0]
    pdin = [m for m in dfb_measlist if m.meas_attrs["Comments"] == "pd_in"][0]
    return [pdout, pdin]#

def dfb_from_wgt(d, measlist, wn):
    dist = distdict[wn.split("#")[0]]["WGT"]
    dfb_measlist = [m for m in measlist if np.isclose(m.device["yPos"], d["yPos"]-30, atol = 120) and np.isclose(m.device["xPos"], d["xPos"]-dist, atol=120) and m.meas_attrs["WaferName"]==wn]
    pdout = [m for m in dfb_measlist if m.meas_attrs["Comments"] == "pd_out"][0]
    pdin = [m for m in dfb_measlist if m.meas_attrs["Comments"] == "pd_in"][0]
    return [pdout, pdin]

def dfb_from_iso(d, measlist, wn):
    dist = distdict[wn.split("#")[0]]["ISO"]
    dfb_measlist = [m for m in measlist if np.isclose(m.device["yPos"], d["yPos"]-30, atol =150) and np.isclose(m.device["xPos"], d["xPos"]-dist, atol=150) and m.meas_attrs["WaferName"]==wn]
    pdout = [m for m in dfb_measlist if m.meas_attrs["Comments"] == "pd_out"][0]
    pdin = [m for m in dfb_measlist if m.meas_attrs["Comments"] == "pd_in"][0]
    return [pdout, pdin]

def mean_of_ratio(m, start_ind = 100, end_ind = 200):
    dt = m.datasets[0][1][start_ind:end_ind]
    mean = np.mean(dt)
    var = np.std(dt)
    return mean, var


def ratio_of_mean(m_out, m_in, start_ind=100, end_ind=200):
    loss_out = m_out.datasets[0][1][start_ind:end_ind]
    loss_in = m_in.datasets[0][1][start_ind:end_ind]
    mean_out = np.mean(loss_out)
    mean_in  = np.mean(loss_in)
    std_out = np.std(loss_out)
    std_in = np.std(loss_in)
    ratio= mean_out/mean_in
    print("ratio, mean_out, std_out, mean_in, std_in:")
    return ratio, mean_out, std_out, mean_in, std_in

lossdict = {k:{} for k in wafers}
for m in mmi121:
    pdout, pdin = dfb_from_mmi(m.device, pi121, m.meas_attrs["WaferName"])
    # if max(pdout.datasets[0][1][100:250])<1e-4:
    #     continue
    indx = np.where(pdout.datasets[0][1]>1e-4)
    if len(indx[0])<50:
        print(len(indx))
        continue
    ind_start = min(indx[0])
    ind_end = max(indx[0])
    wn = m.meas_attrs["WaferName"]
    bar = m.device["Bar"]
    if bar not in lossdict[wn].keys():
        lossdict[wn][bar] = {}
    
    k = str(m.device["IDDevice"])
    lossdict[wn][bar][k] = {}
    try:
        lossdict[wn][bar][k]["wl"] = int(m.meas_attrs["Comments"].split(" ")[1])
    except IndexError:
        lossdict[wn][bar][k]["wl"] = 1530
    lossdict[wn][bar][k]["meanratio"] = mean_of_ratio(m,start_ind = ind_start, end_ind = ind_end)
    lossdict[wn][bar][k]["ratiomean"] = ratio_of_mean(*dfb_from_mmi(m.device, pi121, wn), ind_start, ind_end)
    
for ind, m in enumerate(mmi121):
    if ind%9 ==0:
        fig, ax = plt.subplots(3,3, figsize = (20,20))
    pdout, pdin = dfb_from_mmi(m.device, pi121, m.meas_attrs["WaferName"])
    ax[(ind//3)%3,ind%3].plot(pdout.datasets[0][0]*1e3,pdout.datasets[0][1]*1e3, color = "g")
    ax[(ind//3)%3,ind%3].plot(pdin.datasets[0][0]*1e3,pdin.datasets[0][1]*1e3, color = "r")
    avg = (pdout.datasets[0][1]+ pdin.datasets[0][1])/2
    ax[(ind//3)%3,ind%3].plot(pdin.datasets[0][0]*1e3,avg*1e3, color = "k")
    loss = pdout.datasets[0][1]/pdin.datasets[0][1]
    ax2 = ax[(ind//3)%3,ind%3].twinx()
    ax2.plot(pdin.datasets[0][0]*1e3,np.log10(loss)*10, color = "b")
    try:
        wavelength_mmi = m.meas_attrs["Comments"].split(" ")[1]
    except IndexError:
        wavelength_mmi = "1530"
    ax[(ind//3)%3,ind%3].set_title(wavelength_mmi + "nm, " + m.device["Bar"] + ", " + m.meas_attrs["WaferName"])
    ax[(ind//3)%3,ind%3].set_xlabel("Laser Current [mA]", fontweight = "bold")
    ax2.set_ylabel("Balance [dB]", fontweight = "bold")
    ax[(ind//3)%3,ind%3].set_ylabel("Photo Current [mA]", fontweight = "bold")
    

  

#%%
balancedict ={k:{} for k in wafers}
for wn in lossdict.keys():
    for bar in lossdict[wn].keys():
        for k in lossdict[wn][bar].keys():
            wav = str(lossdict[wn][bar][k]["wl"])
            if wav not in balancedict[wn]:
                balancedict[wn][wav] = []
            if 10*np.log10(lossdict[wn][bar][k]["ratiomean"][0]) >5:
                continue
            balancedict[wn][wav].append(10*np.log10(lossdict[wn][bar][k]["ratiomean"][0]))


#%%

import matplotlib.patches as mpatches

fig, ax = plt.subplots()
bars = ["D_1", "C_4", "B_2", "A_2"]
bars = ["D_1"]
for wn in lossdict.keys():
    fig, ax = plt.subplots()
    ax.set_title(wn)
    ax.set_xlabel("Wavelength [nm]", fontweight = "bold")
    ax.set_ylabel("MMI Inbalance [dB]", fontweight = "bold")
    ax.set_ylim(bottom = -2, top = 4)
    for bb,bar in enumerate(bars):
        bar_color = plt.cm.viridis((bb+.2)/3)
        try:
            for idd in lossdict[wn][bar].keys():
                ax.scatter(lossdict[wn][bar][idd]["wl"], 10*np.log10(lossdict[wn][bar][idd]["meanratio"][0]), marker = "o", color = bar_color)
                ax.scatter(lossdict[wn][bar][idd]["wl"], 10*np.log10(lossdict[wn][bar][idd]["ratiomean"][0]), marker = "x", color = bar_color, s = 200)
        except:
            continue
        
    patches = [mpatches.Patch(color = plt.cm.viridis((bars.index(bar)+0.2)/3), label = bar) for bar in bars]
    ax.legend(handles = patches)
            
#%%
# wg1700 = [m for m in measlist_wgt if "E1700" in m.meas_attrs["Comments"] 
#           and ("2mm" in m.meas_attrs["Comments"] or "4mm" in
#                 m.meas_attrs["Comments"] or "9mm" in m.meas_attrs["Comments"])]
wg1700 = [m for m in measlist_wgt if "E1700" in m.meas_attrs["Comments"] 
          and "9mm" in m.meas_attrs["Comments"]]
coldict = {"MPW26#120":plt.cm.viridis(0.2), "MPW26#121":plt.cm.viridis(0.8)}
coldict = {k:plt.cm.viridis(wafers.index(k)/len(wafers)) for k in wafers}
fig, ax= plt.subplots()
ax.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    bottom=False,      # ticks along the bottom edge are off
    top=False,         # ticks along the top edge are off
    labelbottom=False)
ax.set_ylabel("E1700 Loss [dB/cm]", fontweight = "bold")
ax.set_title(f"MPW26#120,#121 WG Loss, MMI Bal. corrected")
losslist = []
for i, m in enumerate(wg1700):
    pdout, pdin = dfb_from_wgt(m.device, pi121, m.meas_attrs["WaferName"])
    # loss = pdout.datasets[0][1]/pdin.datasets[0][1]
    # print(m.datasets[0][1].mean(), loss.mean())
    indx = np.where(pdout.datasets[0][1]>1e-4)
    if len(indx[0])<50:
        continue
    start_ind = min(indx[0])
    end_ind = max(indx[0])
    wl = str(int(m.meas_attrs["wavelength"]*1e9))
    length = float(m.meas_attrs["Comments"].split("mm")[0][-1])/10
    loss = -10*np.log10(m.datasets[0][1][start_ind:end_ind].mean())
    print(wl, m.meas_attrs["WaferName"])
    try:
        balance = max(np.array(balancedict[m.meas_attrs["WaferName"]][wl]))
    except KeyError:
        try:
            balance = max(np.array(balancedict[m.meas_attrs["WaferName"]]["1530"]))
        except KeyError:
            continue
    print(loss, balance)
    loss_per_cm =(loss + balance)/length
    losslist.append(loss_per_cm)
    print(loss_per_cm)
    ax.scatter(i,loss_per_cm, color = coldict[m.meas_attrs["WaferName"]])
    
patches = [mpatches.Patch(label = k, color = coldict[k]) for k in coldict.keys()]
ax.legend(handles=patches, prop = {"size":6})
# ax.scatter(range(len(losslist)), losslist)
#%%bj loss
bjdict = {"MPW26#120":{"losslist":[], "lengthlist":[]}, "MPW26#121":{"losslist":[], "lengthlist":[]}}
bjdict = {k:{"losslist":[], "lengthlist":[]} for k in wafers}
length_list = []
loss_list = []
for m in measlist_iso:
    pdout, pdin = dfb_from_iso(m.device, pi121, m.meas_attrs["WaferName"])
    indx = np.where(pdout.datasets[0][1]>1.5e-4)
    if len(indx[0])<50:
        print(len(indx))
        continue
    ind_start = min(indx[0])
    ind_end = max(indx[0])
    wn = m.meas_attrs["WaferName"]
    # bar = m.device["Bar"]
    # if bar not in lossdict[wn].keys():
    #     lossdict[wn][bar] = {}
    bjdict[wn][k] = {}
    bjdict[wn][k]["l"] = m.device["L_I"]
    bjdict[wn][k]["meanratio"] = mean_of_ratio(m,start_ind = ind_start, end_ind = ind_end)
    bjdict[wn][k]["ratiomean"] = ratio_of_mean(*dfb_from_iso(m.device, pi121, wn), ind_start, ind_end)
    try:
        loss_db = -10*np.log10(bjdict[wn][k]["ratiomean"][0])+ max(balancedict[m.meas_attrs["WaferName"]]["1540"])
    except KeyError:
        loss_db = -10*np.log10(bjdict[wn][k]["ratiomean"][0])+ max(balancedict[m.meas_attrs["WaferName"]]["1530"])
    if loss_db<0:
        continue
    if loss_db>5:
        continue
    bjdict[wn]["lengthlist"].append(m.device["L_I"])
    bjdict[wn]["losslist"].append(loss_db)
    
#%%
for wn in bjdict.keys():
    length_list = bjdict[wn]["lengthlist"]
    loss_list = bjdict[wn]["losslist"]
    fig, ax= plt.subplots()
    ax.scatter(np.array(length_list)*1e6, loss_list)
    coefs = np.polyfit(np.array(length_list)*1e6, loss_list, 1)
    pl1d = np.poly1d(coefs)
    length_set = np.array(list(set(length_list+[0])))*1e6
    length_set.sort()
    ax.plot(length_set, pl1d(length_set), linestyle = "dashed", color = "r", linewidth = 1)
    ax.set_ylim(0,6)
    ax.set_ylabel("Loss [dB]", fontweight = "bold")
    ax.set_title(f"{wn} BJ+ISO Loss, MMI Bal. corrected")
    ax.set_xlabel("ISO Length [µm]", fontweight = "bold")
    ax.annotate(f"y = {np.around(coefs[0],6)} * x + {np.around(coefs[1],2)}", xy = (.25,.25), color = "r", xycoords="figure fraction")
