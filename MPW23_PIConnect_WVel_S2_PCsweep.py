# -*- coding: utf-8 -*-
"""
Created on Thu Sep 19 10:15:37 2019


@author: fou
"""
"""
Measurement description:
    Recording LIV of DFB with two PDs. Loss between MMI and second PD is inferred
    ->   VI, PI_in, PI_out, AI(Attenuation) = PI_out/PI_in
"""

import os, errno, datetime, re, copy, sys, keyring, time
# import visa

from pyMPW import pympw
# import pympw
# from PIC_Lab_instruments.instruments.sourcemeter import HHI_PIConnect



# from pyautoalign_S2.functions import *
def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
from foubase import connection, devices, measurements, evaluations, chips, common, masksets
from tqdm import tqdm

import numpy as np
import matplotlib.pyplot as plt



#%%access

username = 'heibach'
host = "172.16.29.181"
name_db='foubase'
connex = connection.Mysql_Connection(username=username, host=host, name_db=name_db) # OR jones gets his own DB account
# connex.connect()
connex.connect("hh123")# enter pw here
#%%
path_to_gds = "//hhi.de/abteilung/PC/PC-FOU/Messungen/CAD/MPW26_v7.gds"
maskset_obj = masksets.Maskset(connex)
maskset_obj.read_from_gds(path_to_gds)

#%%define meas params
 
"""Define measurement:"""""""""""""""""""""

# Mask = masksets.read_from_sql("MPW22", connex)

# ChipUT = [Chip for Chip in Mask.chips if Chip["IDChip"] == 5108 ][0] #MPW21: 4798
wafername = "MPW26#120"

operator = "heibach"
station = "PIC_Lab1"
temp = 20 


laser_currents = np.arange(0.5,150.1,0.5)*1e-3 #A
heater_currents = np.arange(0.5,50.1,0.5)*1e-3 #A
pd_vi_voltages = np.arange(-3,2.001, 0.02)
sweep_params = {"las_start":laser_currents[0]*1e6, 
                "las_num":len(laser_currents), 
                "las_step" :(laser_currents[1]-laser_currents[0])*1e6,
                "heat_start":heater_currents[0]*1e6,
                "heat_num":len(heater_currents),
                "heat_step":(heater_currents[1]-heater_currents[0])*1e6,
                "pd_start":pd_vi_voltages[0]*1e3,
                "pd_num": len(pd_vi_voltages),
                "pd_step":(pd_vi_voltages[1]-pd_vi_voltages[0])*1e3}

PDDC_voltage = -2 #V
PD_responsivity = 0.8 #A/W assumed

#get devices from DB:
########
bar = 'C_4'
Mask = masksets.read_from_sql_al(wafername.split("#")[0], connex)
DFB_init = [dev for dev in Mask.devices if (dev["DeviceType"] == "HHI_DFB" and dev["Bar"] == bar)][0]
# DFB_init = devices.get_device_fromIDs([373161], connex)[0]
ChipUT = DFB_init.get_chip_al()
# DFB_init, ChipUT = run_device_finder_gui()
# DFBs, ChipUT = run_device_finder_gui_multi()
# DFB_init = DFBs[0] # select the first DFB manually (could also be obtained from Chip, if specified)
#%%
""""""""""""""""""""""""""""""""""""""""""
'''this may help:'''
StructType_to_measure = ["WG_loss", "BJ_loss", "MMI_balance",  "Bend_loss", "DFB_LIV_balance"]#, "SOA_gain"]#, "DFB_LIV_balance", "Bend_loss"]#"

DFBs=[]
for dev in [dev for dev in ChipUT.devices if dev["DeviceType"] == "HHI_DFB"]:
    dev.connection = connex
    try:
        MS = pympw.MeasurementStructure(connex, dev, ChipUT, maskset_object = maskset_obj)
        if MS["StructType"] in StructType_to_measure:
            DFBs.append(dev)
            # print(MS, MS.DUT["DeviceType"])
            # print(all([MS["StructType"] not in ["WG_loss", "BJ_loss"], MS.DFB["MasksetName"] not in ["MPW19", "MPW20", "MPW21", "MPW22", "DONNY2", "DONNY3", "PICA2", "LUCA"]]))
    except Exception as e:
        print(e)
        continue
DFBs = sorted(DFBs, key =  lambda DFB : DFB["yPos"])    
# DFB_init = DFBs[0]

# DFBs.pop(-2) #check DFBs!!!!
# DFBs.pop(-2)    # remove the ones you dont want to measure

ChipUT.plot([DFB["IDDevice"] for DFB in DFBs])
#%%init coord system
'''
PLEASE CONTACT THE FIRST DEVICE (DFB_init) BEFORE EXECUTING THIS BLOCK

note that x axis in motor corresponds to y axis in DB/GDS system! 
Also, motors use mm units, whereas DB/GDS uses um.
All positional variables in this script refer to DB/GDS system.
I.e. the entire positioning will be done in DB/GDS coordinates.
Since offset between GND Pad and DFB is assumed constant, there is no need to correct for this.
'''
'''MOTOR POSITIONING REFERENCE TO DB/GDS COORDINATE SYSTEM:'''

offset_angle = 0.0
# we will create a rotation matrix with unitvector_Motor = Rot_Matrix * unitvector_DB 
#-> correct for rotational mismatch, if needed (ie 23° on optical WV)
mover = pympw.Mover(connex, DFB_init, xps, offset_angle = offset_angle)

#%%initialize PIConnect:

# ip_PIConnect =      '172.16.32.233'
# ip_PIConnect =     '172.16.32.129'
ip_PIConnect =     '172.16.32.218'

pcx = HHI_PIConnect(ip_PIConnect)
pcx.output(0)

#%% funcs


def check_contact(DFB, test_curr = 0.05, test_volt = 1.2): #mA, V
    
    ms = pympw.MeasurementStructure(connex, DFB, ChipUT, maskset_object = maskset_obj)
    print(ms["StructName"])
    
    time.sleep(0.5)
    pcx.output(1)
    time.sleep(0.5)

    pcx.setlevel("vs" + '1', 1)    

    for PD in [chan_key for chan_key in ms.channels if "PD" in chan_key]:
        pcx.setlevel("vs" + str(ms.channels[PD]['Source_Number']), test_volt)
        time.sleep(0.1)
    
    pcx.setlevel("cs" + str(ms.channels["DFB"]['Source_Number']), test_curr)
    time.sleep(0.5)

   

    defect = False
    
    volt = pcx.measure('cs' + str(ms.channels["DFB"]['Source_Number']), 'v')
    print(" DFB: V = " + str(volt) + " V at I = "  + str(test_curr*1e3) + " mA")

    if not 0.1 < volt < 4.8:
        print("issue with DFB")
        defect = True
    
    
    for PD in [chan_key for chan_key in ms.channels if "PD" in chan_key]:
        
        PDcurr = pcx.measure('vs' + str(ms.channels[PD]['Source_Number']), 'i')
        print(PD + ": I = "  + str(PDcurr*1e3) + " mA at V = " + str(test_volt) + " V")
        if not 0.05 < PDcurr*1e3 < 10:
            print("issue with " + PD + ": I = "  + str(PDcurr*1e3) + " mA at V = " + str(test_volt) + " V")
            defect = True  
    
    pcx.output(0)
    
    if defect:
        # if first_try:
        #     pcx.device.resetOCSF()
        #     check_contact(DFB, test_curr = test_curr, test_volt = test_volt, first_try = False)
        # else:
        return False
    
    print("established contact: I_las = " + str(test_curr*1e3) + " mA, V_las = " + str(np.round(volt,3)) + " V")
    
    return True

def test_procedure(DFBs):
    passed = 0
    for dd, DFB in enumerate(DFBs):
        
        mover.move_to_dev(DFB)
        print("testing device " + str(dd+1))
        
        if not check_contact(DFB):
            print("device " + str(dd+1) + " FAILED")
            continue
        
        print("device " + str(dd+1) + " PASSED")
        passed += 1
    
    if passed == len(DFBs):
        print("ALL devices PASSED!")
        

    
    
#%%search the devices you want to measure

MasksetName = wafername.split("#")[0]

#ChipUT = mover.ChipUT
MeasIDs = []
MeasStrucs = []

DFB_IDs = []
DUTs = []
DUT_IDs = []

for DFB in DFBs:
    
    try:
        MS = pympw.MeasurementStructure(connex, DFB, ChipUT, maskset_object = maskset_obj)
    except:
        continue
    MS.meas_attrs_basic["WaferName"] = wafername
    MS.meas_attrs_basic["Operator"] = operator
    MS.meas_attrs_basic["Temp"] = temp

    
    DFB_ID = DFB['IDDevice']
    DFB_IDs.append(DFB_ID)
    
    if MS.DUT != None:
        DUTs.append(MS.DUT)
        DUT_IDs.append(MS.DUT['IDDevice'])
    
    MS.setup_measurements()
    MeasStrucs.append(MS)
    
    
ChipUT.plot(highlight_IDs = DFB_IDs + DUT_IDs)
    
    
#%% meas: #########################################################################################
'''measurement loop starts here'''
auto = True
time_start = time.time()
measlist = []
start_ind = 0
for dd, MS in enumerate(MeasStrucs[16:]):
    
    DFB = MS.DFB
    DFB_ID = DFB['IDDevice']
    
    

    if MS.DUT != None: 
        DUT = MS.DUT
        DUT_ID = MS.DUT['IDDevice']
    else:
        DUT = None
        DUT_ID = None
   
    
    DUTname = MS["StructName"] 
    wavelength = DFB['WL_L']
    
    pcx.output(0)
    time.sleep(0.4)
    mover.move_to_dev(DFB)
    
    time.sleep(0.5)

    time.sleep(0.1)
    
    print(f"measuring: {dd+1} {DUTname}, i.e. {int(100*dd/len(MeasStrucs))} % done") 
    
    ChipUT.plot(highlight_IDs = [DFB_ID, DUT_ID])
    
    plt.pause(2)
    
    # if not check_contact(DFB):
    #     warmup_DFB(min_burn_time = 5)
    if not check_contact(DFB) or not check_contact(DFB):
        print("device " + str(dd+1) + " FAILED")
        continue
    '''Init measurement objects:'''
    
   
    path_to_save = 'C:/Users/fou/Documents/Labdata/Autoalign/' + MS.measurements[0].meas_attrs["WaferName"]+ '/' + DFB["Bar"]+ '/' + time.strftime('%y') + "-" + time.strftime('%m') + "-" + time.strftime('%d') + '/'
    make_sure_path_exists(path_to_save)
    
    ##### GO #################################################################################
    
    #warmup_DFB(min_burn_time=150)
    ############################################################################################
    ####### measure ai/pi/vi_las ###############################################################
    
    print("ai/pi/vi...")

    # laser_voltages = np.zeros((len(laser_currents)))
   
    PDsUT = [chan_key for chan_key in MS.channels if "PD" in chan_key]
    
    pcx.output(1)
    time.sleep(0.5)

    PD_measure_channels = []
    for PD in PDsUT:
        pcx.setlevel("vs" + MS.channels[PD]['Source_Number'], PDDC_voltage)
        PD_measure_channels.append('vs' + MS.channels[PD]['Source_Number'])
        exec(PD + " = np.zeros((len(laser_currents)))")

    #measure:
    time.sleep(0.1)
    sweep_result = pcx.device.setgetSweep("cs" + MS.channels["DFB"]["Source_Number"],
                                          sweep_params["las_start"], sweep_params["las_step"], sweep_params["las_num"], 5,
                                          "cs" + MS.channels["DFB"]["Source_Number"], *PD_measure_channels)
    laser_voltages = np.array(sweep_result[0])*1e-3
    for ind, PD in enumerate(PDsUT):
        exec(PD + "=np.array(sweep_result[ind+1])*1e-6")
    
    # for (ii,laser_current) in enumerate(tqdm(laser_currents)):
        
    #     pcx.setlevel("cs" + MS.channels["DFB"]["Source_Number"], laser_current) # Set Laser current
        
    #     laser_voltages[ii] = pcx.measure('cs' + MS.channels["DFB"]['Source_Number'], 'v')
        
            
    #     for PD in PDsUT:
    #         exec(PD + "[ii] = - pcx.measure('vs' + MS.channels[PD]['Source_Number'], 'i')")
    #         meas_success = True
            
    pcx.output(0)

    if "PDOUT" in MS.channels:
        losses = PDOUT/PDIN
    else:
        losses = PDIN/PDREF
        
    MS.measurements[0].datasets.append([laser_currents, laser_voltages, ])
    
    for meas in MS.measurements:
        for PD in PDsUT:
            if meas.meas_attrs["Comments"] == "pd_" + PD[2:].lower():
                exec("meas.datasets.append([laser_currents, np.abs(" + PD + "/PD_responsivity) , ])")
        if meas.meas_attrs["MeasurementType"] == "ai" and MS["StructType"] != 'SOA_gain':
            meas.datasets.append([laser_currents, losses, ])
            if MS["StructType"] not in ['Bend_Loss', 'MMI_balance']:
                meas.meas_attrs["Comments"] += ", WV"
        if meas.meas_attrs["MeasurementType"] in ["vi", "pi"]:
            if "ref" in str(meas.meas_attrs["Comments"]) and "refl" not in str(meas.meas_attrs["Comments"]):
                meas.meas_attrs["Comments"] += ", WV"
        if meas.meas_attrs["MeasurementType"] in ["vi"] and "HEATER" not in str(meas.meas_attrs["Comments"]):
            meas.meas_attrs["Comments"] = "WV"
    ############################################################################################
    ######### Heater vi ##############################################################
        
    if any([("heater" in str(meas.meas_attrs["Comments"]).lower()) for meas in MS.measurements]):
        print("heater...")
        heater_voltages = np.zeros((len(heater_currents)))
        
        time.sleep(0.1)
        
        pcx.output(1)
        time.sleep(0.5)

        pcx.setlevel("cs" + MS.channels["DFB"]["Source_Number"], 0.5*1e-3)
        
        time.sleep(0.5)
        
        sweep_result = pcx.device.setgetSweep("cs" + MS.channels["HEAT"]["Source_Number"],
                                              sweep_params["heat_start"], sweep_params["heat_step"], sweep_params["heat_num"], 5,
                                              "cs" + MS.channels["HEAT"]["Source_Number"])
        
        heater_voltages = sweep_result[0]
        
        # for (ii,heater_current) in enumerate(heater_currents):
        #     pcx.setlevel("cs" + MS.channels["HEAT"]["Source_Number"], heater_current) # Set Laser current
        #     heater_voltages[ii] = pcx.measure('cs' + MS.channels["HEAT"]['Source_Number'], 'v')
    
        pcx.output(0)

        MS.measurements[1].datasets.append([heater_currents, heater_voltages, ])
    
        plt.plot(MS.measurements[1].datasets[0][0], MS.measurements[1].datasets[0][1])
    ############################################################################################
    ############ SOA ai ################################################################
        
    if MS["StructType"] == 'SOA_gain':
        
        print("SOA gain...")
        #set PD voltages:
        pcx.output(1)
        time.sleep(0.5)

        for PD in ["PDIN", "PDOUT"]:
            pcx.setlevel("vs" + MS.channels[PD]['Source_Number'], PDDC_voltage)  
            
        for meas in [meas for meas in MS.measurements if meas.meas_attrs["MeasurementType"] == "ai"]:
            
            
            PDIN_SOA = np.zeros((len(laser_currents)))
            PDOUT_SOA = np.zeros((len(laser_currents)))
            
            exec(meas.meas_attrs["Comments"]) #gets SOA current
            pcx.setlevel("cs" + MS.channels["SOA"]["Source_Number"], SOA_current)
            time.sleep(0.5)

            print("measuring SOA gain at " + str(SOA_current*1e3) + " mA SOA current")
            for (ii,laser_current) in enumerate(laser_currents):

                time.sleep(0.1)
                pcx.setlevel("cs" + MS.channels["DFB"]["Source_Number"], laser_current) # Set Laser current
                
                for PD in ["PDIN", "PDOUT"]:
                    exec(PD + "_SOA[ii] = - pcx.measure('vs' + MS.channels[PD]['Source_Number'], 'i') ")
            
        
            losses = PDIN_SOA/PDOUT_SOA
            meas.datasets.append([laser_currents, losses, ])
        
        pcx.output(0)

    ############################################################################################
    ############### plot ###################################################################
    fig = plt.figure()
    
    font = {'family' : 'normal',
            'weight' : 'bold',
            'size'   : 16}
    
    plt.rc('font', **font)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    for pp, PD in enumerate(PDsUT):
        
        exec("ax.plot(laser_currents*1e3," + PD + "*1e3, color=plt.cm.magma(pp/len(PDsUT)),label = PD)")
        
    ax_twin = ax.twinx()
    ax_twin.set_ylabel(u" Loss [dB]", fontweight='bold',color='g')
    ax_twin.plot(laser_currents*1e3,-10*np.log10(losses),color='g',label = "Loss")#
    ax_twin.plot(laser_currents*1e3,np.linspace(0,0,len(laser_currents)),color='grey',linestyle = ":")#
    
    
    ax.set_xlabel(u"current [mA]", fontweight='bold')  
    ax.set_ylabel(u"PD current [mA]", fontweight='bold')
    ax.set_title("DFB " + str(dd+start_ind+1) + ' ' + str(MS["StructName"]))
    ax.legend()
    ax.grid('on')
    legend = ax.legend(loc='best', shadow=False, fancybox=True, fontsize=12)    
    legend.get_frame().set_alpha(0.6)
    legend.set_visible(True)
    ax.grid(True)
    
    # ax_twin.set_ylim([-10,10])
    
    fig = plt.figure()
    
    font = {'family' : 'normal',
            'weight' : 'bold',
            'size'   : 16}
    
    plt.rc('font', **font)
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(laser_currents*1e3,laser_voltages,color='r')
    
    ax.set_xlabel(u"current [mA]", fontweight='bold')  
    ax.set_ylabel(u"voltage [V]", fontweight='bold')
    

    ax.grid('on')
    plt.pause(2)
    if not auto:
        check = input("check plots and decide whether to save (ENTER): ")
        
        autocheck = input("continue measurement on autopilot? (y/n): ")
        if autocheck == "y":
            auto = True
            check = ''
    else:
        check = ''
    # try: check = input_with_timeout("check plots and decide whether to save within 30s else will save (ENTER): ", 30)
    # except: check = ''
    # check = ''
    # fig.show()
    
    # print('doublecheck results and save to database manually''')
    # sys.exit()

    
    ############################################################################################
    ############### save ################################################################
    for meas in MS.measurements:
        
    #for meas in [meas_wgt_ai]:    
        filename = meas.device['DeviceName'] + '_' + str(meas.meas_attrs['Comments'])+ '_'
        meas.meas_attrs["Station"] = "PIC_Lab1"
        if check == '':
            meas.write_sql()
        measlist.append(meas.meas_attrs["IDMeasurement"])
        MeasIDs.append(meas.meas_attrs["IDMeasurement"])
        
        if "WV" in meas.meas_attrs["Comments"]:
            try:
                ev = evaluations.Evaluation(connex, eval_type = meas.meas_attrs["MeasurementType"])
                ev.measurement = meas
                ev.compute()
                ev.write_sql()
            except:
                print("Evaluation Error!")   
            
        meas.write_file(path_to_save, filename)
    
    # #%%DBcheck
    
    # DFB1 = devices.get_device_fromIDs([DFB_ID], connex)[0]
    # WGT = devices.get_device_fromIDs([WGT_ID], connex)[0]
    
    # DFB1.load_measurements()
    # WGT.load_measurements()
    
    # fig = plt.figure()
    
    # font = {'family' : 'normal',
    #         'weight' : 'bold',
    #         'size'   : 16}
    
    # plt.rc('font', **font)
    
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    
    # meas_to_plot_DFB = [meas for meas in DFB1.measurements if meas.meas_attrs["WaferName"] == meas_dfb_pi_in.meas_attrs["WaferName"] and meas.meas_attrs["MeasurementType"] == 'pi' and meas.meas_attrs["Comments"] == 'pd_in'][0]
    
    # meas_to_plot_WGT = [meas for meas in WGT.measurements if meas.meas_attrs["WaferName"] == meas_wgt_ai.meas_attrs["WaferName"]][0]
    
    
    # ax.plot(meas_to_plot_DFB.datasets[0][0]*1e3,meas_to_plot_DFB.datasets[0][1]*1e3,color='r',label = "PD_in")
    # ax.plot(meas_to_plot_WGT.datasets[0][0]*1e3,meas_to_plot_DFB.datasets[0][1]*meas_to_plot_WGT.datasets[0][1]*1e3,color='b',label = "PD_out")
    
    # for meas in DFB1.measurements:
    #     if meas.meas_attrs['MeasurementType'] == 'pi':
    #         ax.plot(meas.datasets[0][0]*1e3,meas.datasets[0][1]*1e3, linestyle = ':')
    
        
    
    # ax.set_xlabel(u"current [mA]", fontweight='bold')  
    # ax.set_ylabel(u"power [mW]", fontweight='bold')
    # ax.grid('on')
    # legend = ax.legend(loc='best', shadow=False, fancybox=True, fontsize=12)    
    # legend.get_frame().set_alpha(0.6)
    # legend.set_visible(True)
    
    
    # fig.show()
    # fig = plt.figure()
    
    # font = {'family' : 'normal',
    #         'weight' : 'bold',
    #         'size'   : 16}
    
    # plt.rc('font', **font)
    
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    
    # meas_to_plot_DFB_vi = [meas for meas in DFB1.measurements if meas.meas_attrs["WaferName"] == meas_dfb_pi_in.meas_attrs["WaferName"] and meas.meas_attrs["MeasurementType"] == 'vi'][0]
    
    # ax.plot(meas_to_plot_DFB_vi.datasets[0][0]*1e3,meas_to_plot_DFB_vi.datasets[0][1],color='r')
    # for meas in DFB1.measurements:
    #     if meas.meas_attrs['MeasurementType'] == 'vi':
    #         ax.plot(meas.datasets[0][0]*1e3,meas.datasets[0][1], linestyle = ':')
    
    
    # ax.set_xlabel(u"current [mA]", fontweight='bold')  
    # ax.set_ylabel(u"voltage [V]", fontweight='bold')
    # ax.grid('on')

#%%
xps.mid.move(-300, 'z')
time_end = time.time()
print(f"this measurement took {time_end-time_start} s")