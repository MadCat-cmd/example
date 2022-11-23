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
import visa

#from pyMPW import pympw
from PIC_Lab_instruments.instruments.sourcemeter import HHI_PIConnect



from foubase import connection, devices, measurements, evaluations, chips, common, masksets
from tqdm import tqdm

import numpy as np
import matplotlib.pyplot as plt

#%% foubase access

username = 'chen'
host = "172.16.29.181"
#name_db='foubase'
name_db="fouwaste"
connex = connection.Mysql_Connection(username=username, host=host, name_db=name_db) # OR jones gets his own DB account
# connex.connect()
connex.connect("1q2w3e4r")# enter pw here

#%%
#chip plot

#Hole alle DFB aus MPW22 aus db

wafername = "MPW22"
bar = "A_1"

Mask = masksets.read_from_sql(wafername.split('#')[0], connex)

DFB_init = [dev for dev in Mask.devices if dev["DeviceType"] == "HHI_DFB" and dev["Bar"] == bar]


ChipUT = DFB_init[0].get_chip()

ChipUT.plot([DFB["IDDevice"] for DFB in DFB_init])

plt.show()




for dev in ChipUT.devices:
    #print(dev["DeviceType"])
    pass

for DFB in DFB_init:
    print(DFB.get_chip())

