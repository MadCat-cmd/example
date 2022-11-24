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
#username = 'chen'
username = 'hogan'
host = "172.16.29.181"
name_db='foubase'
connex = connection.Mysql_Connection(username=username, host=host, name_db=name_db) # OR jones gets his own DB account
connex.connect("1234")# enter pw here
#connex.connect("1q2w3e4r")

#%%define meas params
 
"""Define measurement:"""""""""""""""""""""
# wafernames = ["MPW20#1", "MPW20#2", "MPW20#3", "MPW20#4", "MPW20#5", "MPW20#6"] 
# wafernames = ["MPW21#9", "MPW21#10"]
# wafernames = ["MPW22#50", "MPW22#51", "MPW22#52"]
# wafernames = ["MPW22#53", "MPW22#54", "MPW22#55"]
# wafernames = ["DONNY3#26", "DONNY3#27"]
wafernames = ["DONNY3#113", "DONNY3#114"]
# wafernames = ["LUCA#40", "LUCA#41"]
# wafernames = ["MPW23#81", "MPW23#84", "MPW23#85"]
# wafernames = ["MPW24#90", "MPW24#93", "MPW24#94"]
wafernames = ["MPW26#120"]

bar = "D_1"#"D_1" # DONNY3 "A_1" #'A_3' #23 #LUCA:"B_9"#22:"A_1" #"D_5" #21: D_4
# date = '21-07-15' #'21-03-30' # 21-03-26
date = ''


#%% get data DB
device_template = devices.Device(connex)
device_template["MasksetName"] = wafernames[0].split('#')[0]
device_template["Bar"] = bar


devices_found = devices.get_devices_fromTemplate(device_template, connex)

#devices_evaluated = devices.load_evaluations_deviceList_al(connex, devices_found)

devices_measured = devices.load_measurements_deviceList(connex, devices_found)




meas_list = []

AIs = []
PIs = []
VIs = []
heater_VIs = []

for dev in devices_measured:
    for meas in dev.measurements:
        if meas.meas_attrs["WaferName"] not in wafernames:
            continue
        
        meas_list.append(meas)
        
        if meas.meas_attrs["MeasurementType"] == "vi":
            if "HEATER" in meas.meas_attrs["Comments"] or max(meas.datasets[0][0]) < 0.055:
                heater_VIs.append(meas)
            else:
                VIs.append(meas)
        
        elif meas.meas_attrs["MeasurementType"] == "pi":
            PIs.append(meas)
            
        elif meas.meas_attrs["MeasurementType"] == "ai":
            AIs.append(meas)
        

#%% get data local
# path_to_files = f"C:/Users/fou/Documents/Labdata/Autoalign/{wafername}/{bar}/{date}/backup"
path_to_files = f"//9YM84W2/Users/fou/Documents/Labdata/Autoalign/{wafernames[0]}/{bar}/{date}"
# path_to_files = f"//hhi.de/abteilung/PC/PC-FOU/Messungen/Users/hogan/MPW19_WVel/{wafername}/{bar}/{date}"

filenames = [f for f in os.listdir(path_to_files) if os.path.isfile(os.path.join(path_to_files, f))]

meas_list = []

AIs = []
PIs = []
VIs = []
heater_VIs = []


for filename in filenames:
    meas = measurements.read_file(connex, path_to_files+'/'+filename)
    meas.meas_attrs["Station"] = "PIC_Lab1"
    meas.device["ChipName"] = bytes(meas.device["ChipName"], "ascii")
    meas_list.append(meas)
    
    if meas.meas_attrs["MeasurementType"] == "vi":
        if "WV" in meas.meas_attrs["Comments"]:
            VIs.append(meas)
        else:
            heater_VIs.append(meas)
    
    elif meas.meas_attrs["MeasurementType"] == "pi":
        PIs.append(meas)
        
    else:
        AIs.append(meas)
    


#%%plot VIs

# wafers = ["MPW22#52"]
# wafers = ["LUCA#40", "LUCA#41"]

# wafers= ["MPW23#81", "MPW23#84", "MPW23#85"]
# wafers = ["MPW24#90", "MPW24#93", "MPW24#94"]
wafers = ["DONNY3#113", "DONNY3#114"]

# wafers= ["DONNY3#26", "DONNY3#27"]

wafers = ["MPW26#120"]

fig = plt.figure()
ax = fig.add_subplot(111)
# ax_twin = ax.twinx()


ax.set_xlabel(u"Current [mA]")  
ax.set_ylabel(u"Voltage [V]", color = cm.viridis(0.3))
ax.set_title(f"VI WVel {wafers} {bar}") #" Modejumps: " + str(eva.eval_attrs["Modejumps"]))
# ax_twin.set_ylabel(u"Diff. Resistance [Ω]", color = cm.magma(0.3))

Rs = []

for mm, meas in enumerate(VIs):
    
    # if any([data < 0.55 for data in meas.datasets[0][1]]):
    #     continue
    
    if meas.meas_attrs["WaferName"] not in wafers:
        continue
    
    ax.plot(meas.datasets[0][0]*1e3,meas.datasets[0][1],
            color=cm.turbo((round(meas.device['WL_L']*1e9)-1520)/100), 
            label =  f"{round(meas.device['WL_L']*1e9)} nm",
            linewidth = 1) #, label =  f"{int(meas.device['WL_L']*1e6)} nm")
    
    # for vv, data in enumerate(meas.datasets[0][1]):
    #     if vv == len(meas.datasets[0][1]) and abs(data - meas.datasets[0][1][vv-1]) > 0.2:
    #             meas.datasets[0][1][vv] = (meas.datasets[0][1][vv-1] + meas.datasets[0][1][vv-2])/2
        
    #     elif vv == 0:
    #         pass
              
    #     elif abs(data - meas.datasets[0][1][vv-1]) > 0.2 and abs(data - meas.datasets[0][1][vv+1]) > 0.2:
    #         ax.scatter(meas.datasets[0][0][vv]*1e3,meas.datasets[0][1][vv],color="r", linewidth = 5, marker = "o")
    #         print(f"MEAS {meas.meas_attrs['IDMeasurement']}: invalid data point at {np.round(meas.datasets[0][0][vv]*1e3,1)} mA, will interpolate between previous and following value")
    #         meas.datasets[0][1][vv] = (meas.datasets[0][1][vv-1] + meas.datasets[0][1][vv+1])/2
    
    eva = evaluations.Evaluation(connex, 
                                 meas.meas_attrs["MeasurementType"])
    eva.measurement = meas
    # eva.check_sane()
    eva.compute()
    print(eva.eval_attrs['Rs'][0])
    Rs.append(eva.eval_attrs['Rs'][0])

plt.show()
    
    # ax_twin.plot(eva.datasets[0][0]*1e3,eva.datasets[0][1],
    #              color=cm.magma((mm)/len(VIs)), linewidth = 2, 
    #              label = f"{np.round(eva.eval_attrs['Rs'][0], 2)} Ω") #label =  f"{int(meas.device['WL_L']*1e6)} nm")

print("mean:")
print(np.mean(Rs))
      
    
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(sorted(zip(labels, handles), key = lambda t: t[0]))
ax.legend(by_label.values(), by_label.keys())

# ax_twin.legend()
ax.grid(0)
# ax_twin.set_ylim([0,100])
fig.set_size_inches(16*scale_factor, 10*scale_factor)

'''save to DB TODO: #3 '''

# for mm, meas in enumerate(VIs):
#     if any([data < 0.55 for data in meas.datasets[0][1]]):
#         continue
#     meas.write_sql()
#     eva = evaluations.Evaluation(connex, meas.meas_attrs["MeasurementType"])
#     eva.measurement = meas
#     eva.compute()
#     eva.check_sane()
#     eva.write_sql()

#%%plot heater_VIs

heat_IDs = []
# wafers = ["MPW22#50"]
# wafers = ["LUCA#40", "LUCA#41"]
wafers= ["MPW23#81"]#, "MPW23#84", "MPW23#85"]
wafers = ["MPW24#90", "MPW24#93", "MPW24#94"]
wafers= ["DONNY3#26", "DONNY3#27"]
wafers = ["MPW22#54", "MPW22#55"]


fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlabel(u"Current [mA]")  
ax.set_ylabel(u"Voltage [V]")
ax.set_title(f"DFB Heaters WVel {wafers} {bar}") #" Modejumps: " + str(eva.eval_attrs["Modejumps"]))

for mm, meas in enumerate(heater_VIs):
    
    if not "HEATER" in meas.meas_attrs["Comments"]:
        continue
    #if not 0.5 < meas.datasets[0][1][-1] < 3:
    #    continue
    if meas.meas_attrs["WaferName"] not in wafers:
        continue 
    
    if meas.datasets[0][1][-1] > 5:
        continue
    

    ax.plot(meas.datasets[0][0]*1e3,meas.datasets[0][1],
            color=cm.turbo((meas.device["WL_L"]*1e9-1500)/100), 
            linewidth = 2, label =  f"{int(meas.device['WL_L']*1e9)} nm")
    
    heat_IDs.append(meas.meas_attrs["IDMeasurement"])
    if meas.datasets[0][1][-1] > 3:
        continue
    # for vv, data in enumerate(meas.datasets[0][1]):
    #     if abs(data - meas.datasets[0][1][vv-1]) > 0.5 and abs(data - meas.datasets[0][1][vv+1]) > 0.5:
    #         ax.scatter(meas.datasets[0][0][vv]*1e3,meas.datasets[0][1][vv],color="r", linewidth = 5, marker = "o")
    #         print(f"invalid data point at {np.round(meas.datasets[0][0][vv]*1e3,1)} mA, will interpolate between previous and following value")
    #         meas.datasets[0][1][vv] = (meas.datasets[0][1][vv-1] + meas.datasets[0][1][vv+1])/2

plt.show()
    
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(sorted(zip(labels, handles), key = lambda t: t[0]))
ax.legend(by_label.values(), by_label.keys())
ax.grid(0)
fig.set_size_inches(16*scale_factor, 10*scale_factor)

'''save to DB TODO #3'''

# for mm, meas in enumerate(heater_VIs):

#     if not 0.5 < meas.datasets[0][1][-1] < 3:
#         continue
    # meas.write_sql()
    # eva = evaluations.Evaluation(connex, meas.meas_attrs["MeasurementType"])
    # eva.measurement = meas
    # eva.compute()
    # eva.check_sane()
    # eva.write_sql()

     
#%%plot PIs

wafers = ["MPW22#52"]
wafers = ["LUCA#40"]
wafers = ["MPW23#81", "MPW23#84", "MPW23#85"]
wafers = ["MPW24#90", "MPW24#93", "MPW24#94"]
wafers = ["DONNY3#26", "DONNY3#27"]
wafers = ["MPW22#55"]
wafers = ["DONNY3#113", "DONNY3#114"]



cond = ["pd_ref, WV"]

fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlabel(u"Current [mA]")  
ax.set_ylabel(u"Power [mW]")
ax.set_title(f"PI@{cond} WVel {wafers} {bar}") #" Modejumps: " + str(eva.eval_attrs["Modejumps"]))
# ax.set_title(f"PI@pd_ref vs @{cond[1]} (dashed) WVel {wafers} {bar}") 

for mm, meas in enumerate(PIs):
    
    if meas.meas_attrs["Comments"] not in cond:# or meas.meas_attrs["Comments"] != '':
        continue
    
    if meas.meas_attrs["WaferName"] not in wafers or meas.meas_attrs["PulseCW"] != '0':
        continue
    
    # if not meas.device["IDDevice"] in [320334, 320307, 320202]: #[319964, 319974, 319984]
    #     continue
    
    # if not meas.device["IDDevice"] in  [dev["IDDevice"] for dev in devices_measured if dev["DeviceType"] == "HHI_DFB"][:10] + [dev["IDDevice"] for dev in devices_measured if dev["DeviceType"] == "HHI_DFB"][12:13]:
    #     continue
    # if any([data < 0.00011 for data in meas.datasets[0][1][230:]]):
    #     continue 
    line = '-'
    if meas.meas_attrs["Comments"] in ["pd_in", "pd_out"]:
        line = '--'
    
    ax.plot(meas.datasets[0][0]*1e3,meas.datasets[0][1]*1e3,
            color=cm.gist_ncar(np.round(round(meas.device['WL_L']*1e9)-1520)/85, 2), 
            linewidth = 1.5, label =  f"{round(meas.device['WL_L']*1e9)} nm",
            linestyle = line)
    
    # for vv, data in enumerate(meas.datasets[0][1]):
    #     if vv == len(meas.datasets[0][1])-1 and abs(data - meas.datasets[0][1][vv-1]) > 0.1*1e-3:
    #             meas.datasets[0][1][vv] = (meas.datasets[0][1][vv-1] + meas.datasets[0][1][vv-2])/2
        
    #     elif vv == 0:
    #         pass
              
    #     else:
    #         if abs(data - meas.datasets[0][1][vv-1]) > 0.1*1e-3 and abs(data - meas.datasets[0][1][vv+1]) > 0.1*1e-3:
    #             ax.scatter(meas.datasets[0][0][vv]*1e3,meas.datasets[0][1][vv]*1e3,color="r", linewidth = 5, marker = "o")
    #             print(f"invalid data point at {np.round(meas.datasets[0][0][vv]*1e3,1)} mA, will interpolate between previous and following value")
                                
    #             meas.datasets[0][1][vv] = (meas.datasets[0][1][vv-1] + meas.datasets[0][1][vv+1])/2
         
    eva = evaluations.Evaluation(connex, meas.meas_attrs["MeasurementType"])
    eva.measurement = meas
    # eva.check_sane()
    eva.compute()
    
    # ax.scatter(eva.eval_attrs["Ith"][0]*1e3, 1 ,s = 1e7, color=cm.gist_ncar(np.round(int(meas.device['WL_L']*1e6)-1520)/85, 2), linewidth = 2, marker = "|") #label =  f"{int(meas.device['WL_L']*1e6)} nm")
      
    
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(sorted(zip(labels, handles), key = lambda t: t[0]))
ax.legend(by_label.values(), by_label.keys())
# ax.legend()
ax.grid(0)
ax.set_ylim(top = 1.1)
fig.set_size_inches(16*scale_factor, 10*scale_factor)
        

'''save to DB TODO:  #3 , and discuss whether pd_in, out, refl needed in DB...'''

# for mm, meas in enumerate(PIs):
#     if meas.meas_attrs["Comments"] != cond:        
#         continue
#     if any([data < 0.00011 for data in meas.datasets[0][1][230:]]):
#         continue 
    
#     meas.write_sql()
#     eva = evaluations.Evaluation(connex, meas.meas_attrs["MeasurementType"])
#     eva.measurement = meas
#     eva.compute()
#     eva.check_sane()
#     eva.write_sql()

#%%plot PIs compare wafers

cond = "pd_ref, WV"

fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlabel(u"Current [mA]")  
ax.set_ylabel(u"Power [mW]")
ax.set_title(f"PI@{cond} WVel {wafernames} {bar}") #" Modejumps: " + str(eva.eval_attrs["Modejumps"]))


for mm, meas in enumerate(PIs):
    
    if meas.meas_attrs["Comments"] != cond:
        continue
    
    # if any([data < 0.00011 for data in meas.datasets[0][1][230:]]):
    #     continue 
    
    ax.plot(meas.datasets[0][0]*1e3,meas.datasets[0][1]*1e3,
            color=cm.turbo((int(meas.meas_attrs['WaferName'].split('#')[-1]) - 53)/3), 
            linewidth = 2, 
            label =  meas.meas_attrs['WaferName'])
    
    for vv, data in enumerate(meas.datasets[0][1]):
        if vv == len(meas.datasets[0][1])-1 and abs(data - meas.datasets[0][1][vv-1]) > 0.1*1e-3:
                meas.datasets[0][1][vv] = (meas.datasets[0][1][vv-1] + meas.datasets[0][1][vv-2])/2
        
        elif vv == 0:
            pass
              
        else:
            if abs(data - meas.datasets[0][1][vv-1]) > 0.1*1e-3 and abs(data - meas.datasets[0][1][vv+1]) > 0.1*1e-3:
                # ax.scatter(meas.datasets[0][0][vv]*1e3,meas.datasets[0][1][vv]*1e3,color="r", linewidth = 5, marker = "o")
                # print(f"invalid data point at {np.round(meas.datasets[0][0][vv]*1e3,1)} mA, will interpolate between previous and following value")
                                
                meas.datasets[0][1][vv] = (meas.datasets[0][1][vv-1] + meas.datasets[0][1][vv+1])/2
         
    eva = evaluations.Evaluation(connex, meas.meas_attrs["MeasurementType"])
    eva.measurement = meas
    # eva.check_sane()
    eva.compute()
    
    # ax.scatter(eva.eval_attrs["Ith"][0]*1e3, 1 ,s = 1e7, color=cm.gist_ncar(np.round(int(meas.device['WL_L']*1e6)-1520)/85, 2), linewidth = 2, marker = "|") #label =  f"{int(meas.device['WL_L']*1e6)} nm")
      
    
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(sorted(zip(labels, handles), key = lambda t: t[0]))
ax.legend(by_label.values(), by_label.keys())
# ax.legend()
ax.grid(0)
ax.set_ylim(bottom = -0.1)
fig.set_size_inches(16*scale_factor, 10*scale_factor)
        

'''save to DB TODO:  #3 , and discuss whether pd_in, out, refl needed in DB...'''

# for mm, meas in enumerate(PIs):
#     if meas.meas_attrs["Comments"] != cond:        
#         continue
#     if any([data < 0.00011 for data in meas.datasets[0][1][230:]]):
#         continue 
    
#     meas.write_sql()
#     eva = evaluations.Evaluation(connex, meas.meas_attrs["MeasurementType"])
#     eva.measurement = meas
#     eva.compute()
#     eva.check_sane()
#     eva.write_sql()
#%%plot MMI AIs ######################## DO THIS FIRST!!!!!!

cond = "MMI"

wafers = ["MPW23#81"]
wafers = ["MPW24#90", "MPW24#93", "MPW24#94"]
wafers = ["DONNY3#26", "DONNY3#27"]
wafers = ["MPW22#54"]
wafers = ["DONNY3#113", "DONNY3#114"]




fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlabel(u"Current [mA]")  
ax.set_ylabel(u"Balance (arb) [Top/Bottom]")
ax.set_title(f"MMI balance WVel {wafers} {bar}") #" Modejumps: " + str(eva.eval_attrs["Modejumps"]))


for mm, meas in enumerate(AIs):
    
    if cond not in meas.meas_attrs["Comments"]:
        continue
    
    if meas.meas_attrs["WaferName"] not in wafers:
        continue
    print(mm)
    
    if mm in [ 35, 42]:
        continue
    
    meas_MMI_balance = meas 
    
    '''get balance:'''
    
    balance_index_start = 100 #data between these indeces is used for balance evaluation, adapt manually!!!!! possibly wiser to just use minimum
    balance_index_stop = 200
    
    
    balance = np.mean(meas.datasets[0][1][balance_index_start:balance_index_stop])
    print(balance, meas.meas_attrs["wavelength"])
    balance_in = np.round(100/(balance +1),2)
    balance_out = np.round(100-balance_in,2)
    
    ax.plot(meas.datasets[0][0]*1e3,meas.datasets[0][1],
            color=cm.rainbow(int(meas.meas_attrs["wavelength"]*1e9 - 1500)/80), 
            linewidth = 2,
            label =  f'@{int(meas.meas_attrs["wavelength"]*1e9)}nm T(L){round(balance_out,1)}/B(R){round(balance_in,1)} on {meas.meas_attrs["WaferName"][-3:]}')
    



    for vv, data in enumerate(meas.datasets[0][1]):
        if abs(data - meas.datasets[0][1][vv-1]) > 1 and abs(data - meas.datasets[0][1][vv+1]) > 1:
            ax.scatter(meas.datasets[0][0][vv]*1e3,meas.datasets[0][1][vv],color="r", linewidth = 5, marker = "o")
            print(f"invalid data point at {np.round(meas.datasets[0][0][vv]*1e3,1)} mA, will interpolate between previous and following value")
            meas.datasets[0][1][vv] = (meas.datasets[0][1][vv-1] + meas.datasets[0][1][vv+1])/2
            
    ax.scatter(meas.datasets[0][0][balance_index_start]*1e3,
                meas.datasets[0][1][balance_index_start],
                color="r", 
                linewidth = 3, 
                marker = "|", 
                s = 1e5,
                linestyle = "-.")
    ax.scatter(meas.datasets[0][0][balance_index_stop]*1e3,
                meas.datasets[0][1][balance_index_stop],
                color="r", 
                linewidth = 3, 
                marker = "|",
                s = 1e5,
                linestyle = "-.")    

handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(sorted(zip(labels, handles), key = lambda t: t[0]))
ax.legend(by_label.values(), by_label.keys())


ax.grid(0)
ax.set_ylim([0.5,1.5])
fig.set_size_inches(16*scale_factor, 10*scale_factor)

###### meas_MMI_balance.write_sql() ##### DONE!
        
        
        
#%%plot WG AIs

cond = ["E200", "E600", "E1700"]
wafers = ["MPW22#51"]
wafers = ["LUCA#40"]
wafers = ["MPW23#81"]
wafers = ["MPW24#90", "MPW24#93", "MPW24#94"]
wafers = ["DONNY3#26", "DONNY3#27"]
wafers = ["MPW22#54", "MPW22#55"]
wafers = ["DONNY3#113", "DONNY3#114"]


wls = [1530, 1540, 1550, 1560]

fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlabel(u"Current [mA]")  
ax.set_ylabel(u"Transmission (arb) [Out/In]")
ax.set_title(f"WG loss WVel {wafers} {bar}") #" Modejumps: " + str(eva.eval_attrs["Modejumps"]))


for mm, meas in enumerate(AIs):
    
    if not any( con in meas.meas_attrs["Comments"] for con in cond):
        continue
    
    # if mm in [71,72]:
    #     continue
    
    if meas.meas_attrs["WaferName"] not in wafers:
        continue 
    
    # if int(meas.device["yPos"]) == 3255:
    #     meas.meas_attrs["Comments"] = "E1700"
    
    # correct for MMI Balance, do this only once!:
    # meas.datasets[0][1] = meas.datasets[0][1]*1/balance
        
    WL = int(meas.meas_attrs["wavelength"]*1e9)
    if WL not in wls:
        continue
    
    print(mm)
    eva = evaluations.Evaluation(connex, meas.meas_attrs["MeasurementType"])
    eva.measurement = meas
    # eva.check_sane()
    try:
        eva.compute()
        label = f"{meas.meas_attrs['Comments']} @{WL}nm"#{np.round(eva.eval_attrs['loss'][0],1) } db"
    except:
        label = f"{meas.meas_attrs['Comments']} nan db"
        
    ax.plot(meas.datasets[0][0]*1e3,meas.datasets[0][1],color=cm.rainbow((mm)/15), linewidth = 2, label =  label)

    # for vv, data in enumerate(meas.datasets[0][1]):
    #     if abs(data - meas.datasets[0][1][vv-1]) > 1 and abs(data - meas.datasets[0][1][vv+1]) > 1:
    #         ax.scatter(meas.datasets[0][0][vv]*1e3,meas.datasets[0][1][vv],color="r", linewidth = 5, marker = "o")
    #         print(f"invalid data point at {np.round(meas.datasets[0][0][vv]*1e3,1)} mA, will interpolate between previous and following value")
    #         meas.datasets[0][1][vv] = (meas.datasets[0][1][vv-1] + meas.datasets[0][1][vv+1])/2
    
    
   
    
    
    
# ax.set_ylim([0.2,1.31])    

handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(sorted(zip(labels, handles), key = lambda t: t[0]))
ax.legend(by_label.values(), by_label.keys())

# ax.legend(loc = "upper left")
ax.grid(0)
fig.set_size_inches(20*scale_factor, 13*scale_factor)


'''save to DB TODO:  #1'''

# for mm, meas in enumerate(AIs):
    
#     if cond not in meas.meas_attrs["Comments"]:
#         continue
    
#     if 0 < np.mean(meas.datasets[0][1][150:]) < 1:
#         # meas.write_sql()
#         print(mm)
        
#         try:
#             eva = evaluations.Evaluation(connex, meas.meas_attrs["MeasurementType"])
#             eva.measurement = meas
#             eva.compute()
#             # eva.check_sane()
#             eva.write_sql()
#         except:
#             print(f"failed to evaluate {meas.meas_attrs['Comments']}")
        


#%%plot BJ AIs

cond = "BJ"

# wafers = ["MPW22#52"]
wafers = ["LUCA#40"]
wafers = ["MPW23#81"]
wafers = ["MPW24#90", "MPW24#93", "MPW24#94"]
wafers = ["DONNY3#26", "DONNY3#27"]
wafers = ["MPW22#54", "MPW22#55"]
wafers = ["DONNY3#113", "DONNY3#114"]




fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlabel(u"Current [mA]")  
ax.set_ylabel(u"Transmission (arb) [Out/In]")
ax.set_title(f"BJ loss WVel {wafers} {bar}") #" Modejumps: " + str(eva.eval_attrs["Modejumps"]))


for mm, meas in enumerate(AIs):
    
    
    if cond not in meas.meas_attrs["Comments"]:
        continue
    
    if meas.meas_attrs["WaferName"] not in wafers:
        continue
    # if not 0 < np.mean(meas.datasets[0][1][150:]) < 1 or np.round(np.mean(meas.datasets[0][1][:150]),1) == np.round(np.mean(meas.datasets[0][1][150:]),1):
    #     continue
    
    # correct for MMI Balance, do this only once!:
    # meas.datasets[0][1] = meas.datasets[0][1]*1/balance
    
    eva = evaluations.Evaluation(connex, meas.meas_attrs["MeasurementType"])
    eva.measurement = meas
    
    dev = meas.device
    length = dev["Length"]
    
    label = f"{meas.meas_attrs['Comments']} {int(length-2)}um "
    
    
    ''' do eval?
    try:
        eva.compute()
        label = f"{mm} {meas.meas_attrs['Comments']} {int(length-2)}um {np.round(eva.eval_attrs['loss'][0],1) } db"
    except:
        label = f"{mm} {meas.meas_attrs['Comments']} {int(length-2)}um nan db"
    '''    
    ax.plot(meas.datasets[0][0]*1e3,meas.datasets[0][1],
            color=cm.rainbow((length-100)/1500), 
            linewidth = 2, 
            label =  label)
    
    print(np.mean(meas.datasets[0][1][200:280]), mm)

    # for vv, data in enumerate(meas.datasets[0][1]):
    #     if abs(data - meas.datasets[0][1][vv-1]) > 1 and abs(data - meas.datasets[0][1][vv+1]) > 1:
    #         ax.scatter(meas.datasets[0][0][vv]*1e3,meas.datasets[0][1][vv],color="r", linewidth = 5, marker = "o")
    #         print(f"invalid data point at {np.round(meas.datasets[0][0][vv]*1e3,1)} mA, will interpolate between previous and following value")
    #         meas.datasets[0][1][vv] = (meas.datasets[0][1][vv-1] + meas.datasets[0][1][vv+1])/2
            
# ax.set_ylim([0.2,0.7])

handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(sorted(zip(labels, handles), key = lambda t: t[0][:2]))
# by_label = dict(sorted(zip(labels, handles), key = lambda t: t[0]))
ax.legend(by_label.values(), by_label.keys())
ax.grid(0)
fig.set_size_inches(16*scale_factor, 10*scale_factor)

# for mm, meas in enumerate(AIs): # TODO: all again!
    
#     if cond not in meas.meas_attrs["Comments"]:
#         continue
    
    
    
# #     if not 0 < np.mean(meas.datasets[0][1][150:]) < 1 or np.round(np.mean(meas.datasets[0][1][:150]),1) == np.round(np.mean(meas.datasets[0][1][150:]),1):
# #         continue
    
#     if 0 < np.mean(meas.datasets[0][1][150:]) < 1:
#         print(mm)
#         meas.write_sql()
        
#         try:
#             eva = evaluations.Evaluation(connex, meas.meas_attrs["MeasurementType"])
#             eva.measurement = meas
#             eva.compute()
#             eva.check_sane()
#             eva.write_sql()
#         except:
#             print(f"failed to evaluate {meas.meas_attrs['Comments']}")
        
        
#%%plot DFBs

wafers = ["MPW22#51"]
wafers = ["LUCA#40", "LUCA#41"]
wafers = ["MPW22#54", "MPW22#55"]
wafers = ["DONNY3#113", "DONNY3#114"]



dev = devices_found[0]
ChipUT = dev.get_chip()

PIs_DFB = [meas for meas in PIs if pympw.MeasurementStructure(connex, meas.device, ChipUT)["StructType"] == "DFB_LIV_balance"]

PIs_DFB_left = [meas for meas in PIs_DFB if meas.meas_attrs["Comments"] == "pd_ref, WV" ]

PIs_DFB_left = sorted(PIs_DFB_left , key = lambda meas: int(meas.device["WL_L"]*1e9))

PIs_DFB_right = [meas for meas in PIs_DFB if meas.meas_attrs["Comments"] == "pd_in" ]

fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlabel(u"Current [mA]")  
ax.set_ylabel(u"Balance (arb) [left/right]")
ax.set_title(f"DFB Balance WVel {wafers} {bar}") #" Modejumps: " + str(eva.eval_attrs["Modejumps"]))


for mm, meas in enumerate(PIs_DFB_left):
    
    if meas.meas_attrs["WaferName"] not in wafers:
        continue
    
    label = f"{int(meas.device['WL_L'] * 1e9)} nm "
    
    for meas_right in PIs_DFB_right:
        if meas_right.device == meas.device and meas.meas_attrs["WaferName"] == meas_right.meas_attrs["WaferName"]:
            balance = meas.datasets[0][1]/meas_right.datasets[0][1]
            if int(meas.device['WL_L'] * 1e9) == 1550:
                balance_1550 = balance
    
    ax.plot(meas.datasets[0][0]*1e3,balance,
            color=cm.rainbow((mm)/12), 
            linewidth = 2, label =  label)

    for vv, data in enumerate(meas.datasets[0][1]):
        if abs(data - meas.datasets[0][1][vv-1]) > 1 and abs(data - meas.datasets[0][1][vv+1]) > 1:
            ax.scatter(meas.datasets[0][0][vv]*1e3,meas.datasets[0][1][vv],color="r", linewidth = 5, marker = "o")
            print(f"invalid data point at {np.round(meas.datasets[0][0][vv]*1e3,1)} mA, will interpolate between previous and following value")
            meas.datasets[0][1][vv] = (meas.datasets[0][1][vv-1] + meas.datasets[0][1][vv+1])/2
            
    
# ax.set_xlim([70,150])
# ax.set_ylim([0,2.9])

ax.legend()
ax.grid(0)
fig.set_size_inches(16*scale_factor, 10*scale_factor)

#%%plot DFBs seperate PI

wafers = ["MPW22#51"]
wafers = ["LUCA#40", "LUCA#41"]
wafers = ["MPW22#55"]
wafers = ["DONNY3#113", "DONNY3#114"]



dev = devices_found[0]
ChipUT = dev.get_chip()

PIs_DFB = [meas for meas in PIs if pympw.MeasurementStructure(connex, meas.device, ChipUT)["StructType"] == "DFB_LIV_balance"]

PIs_DFB_left = [meas for meas in PIs_DFB if meas.meas_attrs["Comments"] == "pd_ref, WV" ]

PIs_DFB_left = sorted(PIs_DFB_left , key = lambda meas: int(meas.device["WL_L"]*1e9))

PIs_DFB_right = [meas for meas in PIs_DFB if meas.meas_attrs["Comments"] == "pd_in" ]

fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlabel(u"Current [mA]")  
ax.set_ylabel(u"Power [mW]")
ax.set_title(f"DFB L/R PI WVel {wafers} {bar}, solid - L, dashed - R") #" Modejumps: " + str(eva.eval_attrs["Modejumps"]))


for mm, meas in enumerate(PIs_DFB_left):
    
    if meas.meas_attrs["WaferName"] not in wafers:
        continue
    
    label = f"{int(meas.device['WL_L'] * 1e9)} nm "
    
    for meas_right in PIs_DFB_right:
        if meas_right.device == meas.device and meas.meas_attrs["WaferName"] == meas_right.meas_attrs["WaferName"]:
    
            ax.plot(meas.datasets[0][0]*1e3,meas.datasets[0][1]*1e3,
                    color=cm.rainbow((mm)/12), 
                    linewidth = 2, label =  label)
            
            ax.plot(meas.datasets[0][0]*1e3,meas_right.datasets[0][1]*1e3,
                    color=cm.rainbow((mm)/12), 
                    linewidth = 2,
                    linestyle = '--',
                    label =  label)

# ax.set_xlim([70,150])
# ax.set_ylim([0,2.9])

handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(sorted(zip(labels, handles), key = lambda t: t[0]))
ax.legend(by_label.values(), by_label.keys())
ax.grid(0)
fig.set_size_inches(16*scale_factor, 10*scale_factor)
        
#%%plot Bend AIs

cond = "Bend"

# wafers = ["MPW22#51"]
wafers = ["MPW23#81"]
wafers = ["MPW24#90", "MPW24#93", "MPW24#94"]
wafers = ["DONNY3#26", "DONNY3#27"]
wafers = ["MPW22#54", "MPW22#55"]
wafers = ["DONNY3#113", "DONNY3#114"]


fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlabel(u"Current [mA]")  
ax.set_ylabel(u"Transmission (arb) [Out/In]")
ax.set_title(f"Bend loss WVel {wafers} {bar}") #" Modejumps: " + str(eva.eval_attrs["Modejumps"]))

meas_bend_lst = []

for mm, meas in enumerate(AIs):
    
    
    if cond not in meas.meas_attrs["Comments"]:
        continue

    if meas.meas_attrs["WaferName"] not in wafers:
        continue
    
    eva = evaluations.Evaluation(connex, meas.meas_attrs["MeasurementType"])
    eva.measurement = meas
    
    meas_bend_lst.append(meas)
    
    bend_radius = int(meas.meas_attrs['Comments'].lstrip("Bend").rstrip(", WV"))

    label = f"R = {bend_radius}μm"
    
    
    corrected_data = meas.datasets[0][1]-balance_1550 #*1/balance #* np.mean(balance_1550[120:]) # correct for DFB L/R imbalance
    # corrected_data = meas.datasets[0][1]
    ax.plot(meas.datasets[0][0]*1e3,corrected_data,
            color=cm.rainbow((bend_radius-150)/200), 
            linewidth = 2, label =  label)

#     for vv, data in enumerate(meas.datasets[0][1]):
#         if abs(data - meas.datasets[0][1][vv-1]) > 1 and abs(data - meas.datasets[0][1][vv+1]) > 1:
#             ax.scatter(meas.datasets[0][0][vv]*1e3,meas.datasets[0][1][vv],color="r", linewidth = 5, marker = "o")
#             print(f"invalid data point at {np.round(meas.datasets[0][0][vv]*1e3,1)} mA, will interpolate between previous and following value")
#             meas.datasets[0][1][vv] = (meas.datasets[0][1][vv-1] + meas.datasets[0][1][vv+1])/2
            


handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(sorted(zip(labels, handles), key = lambda t: t[0]))
ax.legend(by_label.values(), by_label.keys())
ax.grid(0)

# +ax.set_xlim([80,150])
# ax.set_ylim([0.01,3])

fig.set_size_inches(16*scale_factor, 10*scale_factor)

### SAVE TO DB , TODO #1, #2 ###

# for meas in meas_bend_lst:
#     meas.write_sql()

#%%plot DFB balance
cond = 'bend'

wafers = ["MPW22#54", "MPW22#55"]
wafers = ["DONNY3#113", "DONNY3#114"]

fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlabel(u"Current [mA]")  
ax.set_ylabel(u"Transmission (arb) [Out/In]")
ax.set_title(f"Bend loss WVel {wafers} {bar}") #" Modejumps: " + str(eva.eval_attrs["Modejumps"]))

meas_bend_lst = []

for mm, meas in enumerate(PIs):
    
    
    if cond not in meas.meas_attrs["Comments"]:
        continue

    if meas.meas_attrs["WaferName"] not in wafers:
        continue
    
    eva = evaluations.Evaluation(connex, meas.meas_attrs["MeasurementType"])
    eva.measurement = meas
    
    meas_bend_lst.append(meas)
    
    bend_radius = int(meas.meas_attrs['Comments'].lstrip("Bend").rstrip(", WV"))

    label = f"R = {bend_radius}μm"
    
    
    corrected_data = meas.datasets[0][1]*1/balance #* np.mean(balance_1550[120:]) # correct for DFB L/R imbalance
    
    ax.plot(meas.datasets[0][0]*1e3,corrected_data,
            color=cm.rainbow((bend_radius-150)/350), 
            linewidth = 2, label =  label)

#     for vv, data in enumerate(meas.datasets[0][1]):
#         if abs(data - meas.datasets[0][1][vv-1]) > 1 and abs(data - meas.datasets[0][1][vv+1]) > 1:
#             ax.scatter(meas.datasets[0][0][vv]*1e3,meas.datasets[0][1][vv],color="r", linewidth = 5, marker = "o")
#             print(f"invalid data point at {np.round(meas.datasets[0][0][vv]*1e3,1)} mA, will interpolate between previous and following value")
#             meas.datasets[0][1][vv] = (meas.datasets[0][1][vv-1] + meas.datasets[0][1][vv+1])/2
            


ax.legend()
ax.grid(0)

# +ax.set_xlim([80,150])
ax.set_ylim([0.2,1])

fig.set_size_inches(16*scale_factor, 10*scale_factor)

### SAVE TO DB , TODO #1, #2 ###

# for meas in meas_bend_lst:
#     meas.write_sql()
        
      
#%%plot ALL AIs

fig = plt.figure()
ax = fig.add_subplot(111)

ax.set_xlabel(u"Current [mA]")  
ax.set_ylabel(u"Balance (arb) [Top/Bottom]")
ax.set_title(f"Losses WVel {wafernames} {bar}") #" Modejumps: " + str(eva.eval_attrs["Modejumps"]))


for mm, meas in enumerate(AIs):
    
    # if not 0 < np.mean(meas.datasets[0][1][150:]) < 1: # or np.round(np.mean(meas.datasets[0][1][:150]),1) == np.round(np.mean(meas.datasets[0][1][150:]),1):
    #     continue
    # if any([data<0 for data in meas.datasets[0][1]]): # or np.round(np.mean(meas.datasets[0][1][:150]),1) == np.round(np.mean(meas.datasets[0][1][150:]),1):
    #     continue
    
    if int(meas.device["yPos"]) == 3255:
        meas.meas_attrs["Comments"] = "E1700"
        
    eva = evaluations.Evaluation(connex, meas.meas_attrs["MeasurementType"])
    eva.measurement = meas
    try:
        eva.compute()
        label = f"{meas.meas_attrs['Comments']} {np.round(eva.eval_attrs['loss'][0],1) } db"
        ax.plot(meas.datasets[0][0]*1e3,meas.datasets[0][1],color=cm.rainbow((mm)/len(AIs)), linewidth = 2.5, label =  label)

    except:
        label = f"{meas.meas_attrs['Comments']} nan db"
        ax.plot(meas.datasets[0][0]*1e3,meas.datasets[0][1],color=cm.rainbow((mm)/len(AIs)), linewidth = 1.5, linestyle = ':',  label =  label)

        

    for vv, data in enumerate(meas.datasets[0][1]):
        if abs(data - meas.datasets[0][1][vv-1]) > 1 and abs(data - meas.datasets[0][1][vv+1]) > 1:
            ax.scatter(meas.datasets[0][0][vv]*1e3,meas.datasets[0][1][vv],color="r", linewidth = 5, marker = "o")
            print(f"invalid data point at {np.round(meas.datasets[0][0][vv]*1e3,1)} mA, will interpolate between previous and following value")
            meas.datasets[0][1][vv] = (meas.datasets[0][1][vv-1] + meas.datasets[0][1][vv+1])/2
            
    
    
ax.legend(loc = "upper left", prop={'size': 8})
ax.grid(0)
ax.set_ylim([0,3])
fig.set_size_inches(16*scale_factor, 10*scale_factor)
        

'''save to DB TODO:  #3...'''

        
# for mm, meas in enumerate(AIs):
    
#     if 0 < np.mean(meas.datasets[0][1][150:]) < 1:
#         meas.write_sql()
        
#         try:
#             eva = evaluations.Evaluation(connex, meas.meas_attrs["MeasurementType"])
#             eva.measurement = meas
#             eva.compute()
#             eva.check_sane()
#             eva.write_sql()
#         except:
#             print(f"failed to evaluate {meas.meas_attrs['Comments']}")
        
        
        
        
        
        
        
        
        
        