# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 17:50:53 2021

@author: hogan
"""
import os
import datetime, time
import numpy as np
import pandas as pd

from foubase import common, devices, measurements, evaluations, chips

struct_attributes = ["IDStruct", "StructName", "StructType"]
mover_attributes = ["StageName", "Z_on_chip", "Offset_Angle", "Motor_DB_Rotation", "Reflection_Angle"]

channel_attrs = ["Channel_Type", "Source_Number", "Address", "Pad_Type", "Needle_Number"]
channel_types = ["None", "GND", "V", "I"]
pad_types = ["None", "GND", "PDREF", "PDREFL", "PDIN", "PDOUT", "DFB", "HEAT", "SOA",
             "PDOUT_N", "PDOUT_P", "MOD_N", "BIAS_T", "BIAS_P", "PDREF_P"]

waveguide_names = 12*["E1700"] + 1*["E600"] + 1*["E200"]

SOA_gain_currents = [0.5e-3, 20e-3, 40e-3, 70e-3, 100e-3, 130e-3] # mA per 200um active region Length


meas_attrs_basic = measurements.Measurement_Attributes("vi")
meas_attrs_basic["MeasurementType"] = common.unsetAttribute
meas_attrs_basic["Station"] = "PIC-Lab1"
meas_attrs_basic["Temp"] = 20
meas_attrs_basic["Operator"] = "schoenau"
meas_attrs_basic['Pulsewidth'] = 1
meas_attrs_basic['Pulseperiod'] = 1
meas_attrs_basic['PulseCW'] = 0

class MeasurementStructure(dict):
    """
    dict-like class to represent measurement structures. 
    autmatically generated from DFB
    includes data about source channels, such as PIConnect source number, needles and pads
    """

    _keys = struct_attributes

    def __init__(self, connection, DFB, ChipUT = None, meas_attrs_basic = meas_attrs_basic, path_to_csv = os.path.realpath(__file__).replace("pympw.py", "") + 'WVel_MPW24.csv' ):
        """


        """
        
        super().__init__()
        for key in MeasurementStructure._keys:
            self[key] = common.unsetAttribute
        
        
        self.connection = connection
        self.DFB = DFB    
        self.ChipUT = ChipUT
        
        if type(self.ChipUT) != chips.Chip:
            MasksetName = self.DFB["MasksetName"]
    
            Chips = chips.get_chips_fromMaskset(MasksetName, self.connection)
            Chip_UT = [chip for chip in Chips if chip['ChipName'] == self.DFB['ChipName'] and chip['ChipNumber'] == self.DFB['ChipNumber']][0]  

            self.ChipUT = Chip_UT
        
        if self.DFB["MasksetName"] in ["MPW19", "MPW20", "MPW21", "MPW22", "DONNY2", "DONNY3", "PICA2", "LUCA"]:
            
            self.find_DUT_and_StructType_from_DFB()
        
        else:
            self.get_DUT_and_StructType_from_CSV(path_to_csv)
            
        self.get_channels_from_StructType()
        
        self.meas_attrs_basic = meas_attrs_basic
        self.meas_attrs_basic["Date"] = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'%Y-%m-%d %H:%M:%S')
        
        self.SOA_gain_currents = SOA_gain_currents
    
        self.measurements = []
    # force to use the pre-defined keys:

    def __setitem__(self, key, val):
        if key not in MeasurementStructure._keys:
            raise KeyError
        dict.__setitem__(self, key, val)

    def __eq__(self, struct):
        for key in MeasurementStructure._keys:
            if self[key] != struct[key]:
                return False
        return True

    def update(self,  *args, **kwargs):
        if len(args) > 1:
            raise TypeError(f'update expected at most 1 arguments, got {len(args)}')
        other = dict(*args, **kwargs)
        for key in other:
            if key not in MeasurementStructure._keys:
                raise KeyError
        dict.update(self, other)
    def __hash__(self):
        return hash(tuple(sorted(self.items())))
    
    def find_DUT_and_StructType_from_DFB(self, DevTypes_to_ignore = ["HHI_WGT"]):
    
    
        x_DFB, y_DFB = self.DFB["xPos"] + self.DFB["Length"]/2, self.DFB["yPos"] + self.DFB["Width"]/2    
        
        if self.DFB["angle"] == 180:
            x_DFB, y_DFB = self.DFB["xPos"] - self.DFB["Length"]/2, self.DFB["yPos"] + self.DFB["Width"]/2    
        
        #get devices to the right of DFB:
        DUT_candidates = [dev for dev in self.ChipUT.devices if x_DFB + 305 <=dev["xPos"]<=x_DFB + 4000 and dev["yPos"]<=y_DFB<=dev["yPos"] + dev["Width"] and dev["DeviceType"] not in DevTypes_to_ignore]
    
        #sort by distance to DFB:
        DUT_candidates = sorted(DUT_candidates, key = lambda dev: dev["xPos"])
        
        DUT_candidate_list = [dev["DeviceType"] for dev in DUT_candidates]
        print(DUT_candidate_list)
        if "HHI_DFB" in DUT_candidate_list:
            DUT_candidate_list = DUT_candidate_list[:DUT_candidate_list.index("HHI_DFB")]
                
        if "HHI_MMI2x2" not in DUT_candidate_list:
            
            #see if the the first device within 1200um directly above the DFB is a WGT, if so then it must be a bend
            WGT_candidates = [dev for dev in self.ChipUT.devices if x_DFB-300<=dev["xPos"]<=x_DFB + 300 and y_DFB +224 <= dev["yPos"] <= y_DFB +1200 and dev["DeviceType"] == "HHI_WGT"]
            WGT_candidates = sorted(WGT_candidates, key = lambda dev: dev["yPos"])
            
            
            if len(DUT_candidate_list) >0 and DUT_candidate_list[0] == "HHI_PDDC" and 500 < DUT_candidates[0]["xPos"] - x_DFB < 700 :
                self.DUT = None # the DFB itself is being measured
                self["StructType"] = "DFB_LIV_balance"
                self["StructName"] = "DFB"
            
            
            
            elif len(WGT_candidates) > 0 and '55' in str(self.DFB["WL_L"]):
                
                self.DUT = WGT_candidates[0] # it's a bend
                
                bend_radius = int((self.DUT["yPos"] + self.DUT["Width"]/2  - self.DFB["yPos"] - self.DFB["Width"]/2)/2)
                
                self["StructType"] = "Bend_loss"
                self["StructName"] = "Bend" + str(bend_radius)
            
        
        elif DUT_candidates[0]["DeviceNumber"] <=14 : # it's a WG
            self.DUT = select_next_dev(self.DFB, self.ChipUT, 1800, -70)
            self["StructType"] = "WG_loss"
            self["StructName"] = waveguide_names[int(DUT_candidates[0]["DeviceNumber"])-1]
            
        elif len(DUT_candidate_list) == 1:
            self.DUT = DUT_candidates[0] # it's the MMI
            self["StructType"] = "MMI_balance"
            self["StructName"] = "MMI"
        
        elif DUT_candidate_list[1] == "HHI_SOA": #it's a SOA
            self.DUT = DUT_candidates[1]
            self["StructType"] = "SOA_gain"
            self["StructName"] = "SOA"
            
        elif DUT_candidate_list[2] == "HHI_ISO": #it's a BJ
            self.DUT = DUT_candidates[2]
            self["StructType"] = "BJ_loss"
            self["StructName"] = "BJ"
        
        else: print("couldnt find measurement structure")
        
    def get_DUT_and_StructType_from_CSV(self, path_to_csv = os.path.realpath(__file__).replace("pympw.py", "") + 'WVel_MPW24.csv'):
        
        LT = pd.read_csv(path_to_csv, sep = ';', nrows = 85) #load lookuptable
        
        #find DFB from position with respect to chip
        xmin = np.round(self.DFB["xPos"] - self.ChipUT["xPos"], 0)
        # xmax = self.DFB["xPos"] - self.ChipUT["xPos"] + self.DFB["Width"]
        ymin = np.round(self.DFB["yPos"] - self.ChipUT["yPos"], 0)
        # ymax = self.DFB["yPos"] - self.ChipUT["yPos"] + self.DFB["Height"]
        
        # row = LT.loc[(LT["xPos"] >= xmin) & (LT["xPos"] <= xmax) & (LT["yPos"] >= ymin) & (LT["yPos"] <= ymax)]
        
        self.row = LT.loc[(np.round(LT["xPos"], 0) == xmin) & (np.round(LT["yPos"], 0) == ymin)]
        
        self.DUT = None
        if not self.row["DeviceType"].isnull().values.any():
            xdistance = self.row.Xdistance_from_DFB.values[0]
            ydistance = self.row.Ydistance_from_DFB.values[0]
            self.DUT = select_next_dev(self.DFB, self.ChipUT, 
                                       delta_x = xdistance, delta_y = ydistance, tol = 100,
                                       DeviceType = self.row["DeviceType"].values[0])
            
        self["StructType"] = self.row.StructType.values[0]
        self["StructName"] = self.row.StructName.values[0]
        
               
          
    def get_channels_from_StructType(self):
        self.channels = dict()
        for cc, chan_def in enumerate(channel_definitions[self["StructType"]]):
            if chan_def[0] not in channel_types:
                raise TypeError("expects a list in the following format:  [['None', 20, 'None'], ['None', 22, 'None'], ['V', 24, 'PDIN'], ['I',  '4', 'DFB'], ['GND',  '3', 'GND'], ...] ")
            if chan_def[3] not in pad_types:
                raise TypeError("expects a list in the following format:  [['None', 20, 'None'], ['None', 22, 'None'], ['V', 24, 'PDIN'], ['I',  '4', 'DFB'], ['GND',  '3', 'GND'], ...] ")
            
            chan_def = chan_def +  [cc+1]
            chan = dict()
            for aa, attr in enumerate(channel_attrs):   
                chan[attr] = chan_def[aa]
            
            if chan["Pad_Type"] != "None":
                self.channels[chan["Pad_Type"]] = chan    
    
    def setup_measurements(self):
        ''' generates measurement objects according to the measurement structure'''
        
        self.measurements = []
        self.measurements.append(measurements.Measurement(self.connection, "vi"))
        
        if "HEAT" in self.channels.keys():
            meas_heat = measurements.Measurement(self.connection, "vi")
            meas_heat.meas_attrs["Comments"] = 'HEATER MEASUREMENT!'
            self.measurements.append(meas_heat)
            
            if self["StructType"] in ["WG_loss", "BJ_loss"]:
                if self.DFB["MasksetName"] not in ["MPW19", "MPW20", "MPW21", "MPW22", "DONNY2", "DONNY3", "PICA2", "LUCA"]:
                    self.measurements.pop(-1) #the layout changed
                
            

        
        for chan in [self.channels[chan_key] for chan_key in self.channels if "PD" in self.channels[chan_key]["Pad_Type"]]:
            
            meas_dfb_pi = measurements.Measurement(self.connection, "pi")
            meas_dfb_pi.meas_attrs["Comments"] = "pd_" + chan["Pad_Type"][2:].lower()
            self.measurements.append(meas_dfb_pi)
        
        for meas in self.measurements:
            meas.device = self.DFB
    
            
        if self.DUT != None:
            
            if self.DUT["DeviceType"] == "HHI_SOA":
                # meas_soa_vi = measurements.Measurement(self.connection, "vi")
                # meas_soa_vi.device = self.DUT
                # self.measurements.append(meas_soa_vi)
                
                for SOA_current in SOA_gain_currents:
                    if not self.DUT["L_S"]*1e6* SOA_current/(200) > 0.2:
                        
                        meas_soa_ai = measurements.Measurement(self.connection, "ai")
                        meas_soa_ai.meas_attrs["Comments"] = 'SOA_current = ' + str(self.DUT["L_S"]*1e6* SOA_current/(200))
                        meas_soa_ai.meas_attrs["wavelength"] = self.DFB['WL_L']
                        meas_soa_ai.device = self.DUT
                        
                        self.measurements.append(meas_soa_ai)
            
            else:
                meas_dut_ai = measurements.Measurement(self.connection, "ai")
                meas_dut_ai.meas_attrs["Comments"] = self["StructName"]
                meas_dut_ai.meas_attrs["wavelength"] = self.DFB['WL_L']
                meas_dut_ai.device = self.DUT
                
                self.measurements.append(meas_dut_ai)
                
        for meas in self.measurements:
            for key in self.meas_attrs_basic.keys(): 
                if self.meas_attrs_basic[key] != common.unsetAttribute:
                    meas.meas_attrs[key] = self.meas_attrs_basic[key]
                    
    def plot_on_chip(self, IDs = None):
        if not IDs:
            IDs = [dev["IDDevice"] for dev in [self.DFB, self.DUT] if dev]
        self.ChipUT.plot(IDs)

                      
                      
#%%       mover class
            
       
class Mover(dict):
    """
    dict-like class for positional handling with respect to chip. 
    stores data relevant for coordinate system transformation, and tracks motor movement with respect to DB coordinate system.
    """

    _keys = mover_attributes

    def __init__(self, connection, DFB_init, motor, XY_home_MO = (0,0), offset_angle = 0, motor_to_DB_rotation = 0, reflection_angle = -45):
        """
        newp: PIClabinstruments motor object

        """
        
        super().__init__()
        for key in Mover._keys:
            self[key] = common.unsetAttribute
            
        self.motor = motor

        
        self.connection = connection
        self.DFB_init = DFB_init
        self.DEV_curr = DFB_init
        
        self.ChipUT = DFB_init.get_chip()  
        
        self.align_MOtoDB(XY_home_MO)

        self["Z_on_chip"] = np.round(self.motor.mid.position('z'),1)[0]
        
        
        self["Offset_Angle"] = offset_angle
        self["Motor_DB_Rotation"] = motor_to_DB_rotation
        self.get_rotation_matrix()
        
        self["Reflection_Angle"] = reflection_angle
        self.get_reflection_matrix()
        

    # force to use the pre-defined keys:

    def __setitem__(self, key, val):
        if key not in Mover._keys:
            raise KeyError
        dict.__setitem__(self, key, val)

    def __eq__(self, struct):
        for key in Mover._keys:
            if self[key] != struct[key]:
                return False
        return True

    def update(self,  *args, **kwargs):
        if len(args) > 1:
            raise TypeError(f'update expected at most 1 arguments, got {len(args)}')
        other = dict(*args, **kwargs)
        for key in other:
            if key not in Mover._keys:
                raise KeyError
        dict.update(self, other)
    def __hash__(self):
        return hash(tuple(sorted(self.items()))) 

    def on_chip(self):
        
        if self["Z_on_chip"] == np.round(self.motor.mid.position('z'),1)[0]:
            return True
        
        elif self["Z_on_chip"] - 300 >=  np.round(self.motor.mid.position('z'),1)[0]:
            return False
        
        else:
            print("Z position possibly no longer aligned to Probe")
            raise ValueError
    
    def get_rotation_matrix(self):
        
        theta = np.deg2rad(self["Motor_DB_Rotation"] + self["Offset_Angle"])
        
        self.Rot_Matrix = np.array([[np.cos(theta) , 
                                     -np.sin(theta)],
                                    [np.sin(theta),
                                     np.cos(theta)]])
    def get_reflection_matrix(self):
        
        phi = np.deg2rad(self["Reflection_Angle"])
        self.Refl_Matrix = np.array([[np.cos(2*phi) , 
                                     np.sin(2*phi)],
                                    [np.sin(2*phi),
                                     -np.cos(2*phi)]])
        
        
    
    def align_MOtoDB(self, XY_home_MO = (0,0)):
        
        self.XY_home_DB = np.array([self.DFB_init["xPos"] , self.DFB_init["yPos"]])
        self.XY_setpoint_DB = self.XY_home_DB
        
        self.XY_home_MO = np.array(XY_home_MO)
        if all(self.XY_home_MO == np.array((0,0))):
            #the motor's y axis is the x axis in the DB and vice versa:
            self.XY_home_MO = np.array([self.motor.mid.position('x')[0], self.motor.mid.position('y')[0]])            
        
        
        self.XY_setpoint_MO = self.XY_home_MO
            
    def pos_is_consistent(self, message = True):
        """
        TODO
        """
        return True
   
        
    def transform_DBtoMO(self, XY_DB):
        
        DeltaXY_dev_home_DB = XY_DB - self.XY_home_DB       
        DeltaXY_dev_home_MO = np.dot(self.Refl_Matrix, np.dot(self.Rot_Matrix, DeltaXY_dev_home_DB)) 
        XY_MO = self.XY_home_MO + DeltaXY_dev_home_MO
        
        return XY_MO
    
    def transform_MOtoDB(self, XY_MO):
        
        DeltaXY_dev_home_MO = XY_MO - self.XY_home_MO  
        DeltaXY_dev_home_DB = np.dot(self.Refl_Matrix, np.dot(self.Rot_Matrix, DeltaXY_dev_home_MO))    
        XY_DB = self.XY_home_DB + DeltaXY_dev_home_DB
        
        return XY_DB

    def move_to_dev(self, dev, find_exact_coords = False, contact_offset = 200):
        """
        move to a certain device and place needles at given offset.
        under assumption of perfect knowledge of rotation matrix between chip and mid stage motor axes.
    
        Parameters
        ----------
    
        """
        XY_dev_DB = np.array([dev["xPos"] , dev["yPos"]])
        XY_dev_MO = self.transform_DBtoMO(XY_dev_DB)
        
        if find_exact_coords: #overwrite to center of chip
            XY_dev_DB = np.array([dev["xPos"] + (dev["Length"] - 2*contact_offset)/2 , dev["yPos"]])
            XY_dev_MO = self.transform_DBtoMO(XY_dev_DB)
        

        
        if self.on_chip():
            self.motor.mid.move(-300, 'z')                    # go down
        
        self.motor.device.move_group("M_XYZ", m_x = XY_dev_MO[0]*1e-3, m_y = XY_dev_MO[1]*1e-3 )
        
        # self.motor.mid.move('M_XYZ.M_Y', XY_dev_MO[1]*1e-3)
        # self.motor.mid.move('M_XYZ.M_X', XY_dev_MO[0]*1e-3)           # go to next
        self.XY_setpoint_MO = XY_dev_MO
        self.XY_setpoint_DB = XY_dev_DB
        
        time.sleep(1)
        self.motor.mid.move(self["Z_on_chip"], 'z', relative = False)                      # go up again
        
        self.DEV_curr = dev
    
    def move_absolute_MO(self, XY_MO):
        
        XY_DB = self.transform_MOtoDB(XY_MO)
        
        
        if self.on_chip():
            self.motor.mid.move(-300, 'z')                # go down
        
        self.motor.device.move_group("M_XYZ", m_x = XY_MO[0]*1e-3, m_y = XY_MO[1]*1e-3 )
        # self.motor.mid.move('M_XYZ.M_Y', XY_MO[1]*1e-3)
        # self.motor.mid.move('M_XYZ.M_X', XY_MO[0]*1e-3)           # go to next      
        self.XY_setpoint_MO = XY_MO
        self.XY_setpoint_DB = XY_DB
        
        time.sleep(1)
        
    def move_absolute_DB(self, XY_DB):

        XY_MO = self.transform_DBtoMO(XY_DB)
        
        if self.on_chip():
            self.motor.mid.move(-300, 'z')                # go down
        
        self.motor.device.move_group("M_XYZ", m_x = XY_MO[0]*1e-3, m_y = XY_MO[1]*1e-3)
        
        # self.motor.mid.move('M_XYZ.M_Y', XY_MO[1]*1e-3)
        # self.motor.mid.move('M_XYZ.M_X', XY_MO[0]*1e-3)           # go to next
        self.XY_setpoint_MO = XY_MO
        self.XY_setpoint_DB = XY_DB
        
        time.sleep(1)
        

    def move_relative(self, XY_delta_DB, contact_if_DeviceType = "HHI_DFB", override_sanitycheck = False):
        """
        move relative in both coordinate systems.
        under assumption of perfect knowledge of rotation matrix between chip and mid stage motor axes.
        

        Parameters
        ----------
        XY_delta : Tuple
            xy distance in DB coordinates.
        contact_if_DeviceType: specify devices you would like to contact
        override_sanitycheck : if new position is above specified device, will move back up to
                            establish contact without asking you

        """
        XY_DB = self.XY_setpoint_DB + np.array(XY_delta_DB)
        XY_MO = self.transform_DBtoMO(XY_DB)
        
        if self.on_chip():
            self.motor.mid.move(-300, 'z')                # go down
        
        self.motor.mid.move('y', XY_MO[1], relative = True)
        self.motor.mid.move('x', XY_MO[0], relative = True)           # go to next
        self.XY_setpoint_MO = XY_MO
        self.XY_setpoint_DB = XY_DB
        
        time.sleep(1)
        
        #check if there's a device here
        DEV = [dev for dev in self.ChipUT.devices if dev["xPos"]<=XY_DB[0]<=dev["xPos"] + dev["Length"] and dev["yPos"]<=XY_DB[1]<=dev["yPos"] + dev["Width"] and contact_if_DeviceType in dev["DeviceType"]]
        
        self.DEV_curr = "Nothing contacted"
        
        if len(DEV) == 1:
            DEV = DEV[0]
            establish_contact = True
            if not override_sanitycheck:
                if '' != input(f"Found {DEV['DeviceName']} #{DEV['DeviceNumber']} in this position, establish contact? yes = ENTER: "):
                    establish_contact = False
            if establish_contact:
                self.motor.mid.move(self["Z_on_chip"], 'z', relative = False)          # go up again
                self.DEV_curr = DEV

#%%


def select_next_dev(old_dev, ChipUT, delta_x = 0, delta_y = 400, tol = 100, DeviceType = None):
    
    x_old, y_old = old_dev["xPos"] + old_dev["Length"]/2, old_dev["yPos"] + old_dev["Width"]/2
    
    if old_dev["angle"] == 180:
        x_old, y_old = old_dev["xPos"] - old_dev["Length"]/2, old_dev["yPos"] + old_dev["Width"]/2
        
        
    
    x_new, y_new = x_old + delta_x , y_old + delta_y
    

    try:    
        new_dev = [dev for dev in ChipUT.devices if dev["xPos"] - tol <=x_new<=dev["xPos"] + dev["Length"] + tol  and dev["yPos"] - tol <=y_new<=dev["yPos"] + dev["Width"] + tol ]
        if DeviceType:
            dump =[dev for dev in new_dev if dev["DeviceType"] == DeviceType][0]
    except:
        #new device device has rotation
        x_old, y_old = x_old + old_dev["Length"]/2, y_old - old_dev["Width"]/2
        x_new, y_new = x_old + delta_x , y_old + delta_y
        
        new_dev = [dev for dev in ChipUT.devices if dev["xPos"] - tol <=x_new<=dev["xPos"] + dev["Length"] + tol  and dev["yPos"] - tol <=y_new<=dev["yPos"] + dev["Width"] + tol ]
    
    if DeviceType:
        new_dev =[dev for dev in new_dev if dev["DeviceType"] == DeviceType][0]
    else:
        new_dev = new_dev[0]
        
        
    return new_dev



# DUTtype_structtype_dict = dict() 

# DUTtype_structtype_dict["HHI_WGT"] = "WG_loss"
# DUTtype_structtype_dict["HHI_ISO"] = "BJ_loss"
# DUTtype_structtype_dict["HHI_MMI2x2"] = "MMI_balance"
# DUTtype_structtype_dict["HHI_DFB"] = "DFB_LIV_balance"
# DUTtype_structtype_dict["HHI_SOA"] = "SOA_gain"



channel_definitions = dict()

channel_definitions["WG_loss"] = [['V',  '1', 20, 'PDOUT'], 
                                  ['V',  '2', 22, 'PDREFL'], 
                                  ['V',  '3', 24, 'PDIN'], 
                                  ['I',  '1', 4,  'DFB'], 
                                  ['GND','0', 3,  'GND'], 
                                  ['I',  '2', 6,  'HEAT'], 
                                  ['V',  '4', 26, 'PDREF']] 
channel_definitions["BJ_loss"] = [['V',  '1', 20, 'PDOUT'], 
                                  ['V',  '2', 22, 'PDREFL'], 
                                  ['V',  '3', 24, 'PDIN'], 
                                  ['I',  '1', 4,  'DFB'], 
                                  ['GND','0', 3,  'GND'], 
                                  ['I',  '2', 6, 'HEAT'], 
                                  ['V',  '4', 26, 'PDREF']] 
channel_definitions["MMI_balance"] = [['V',  '1', 20, 'PDOUT'], 
                                      ['V',  '2', 22, 'PDREFL'], 
                                      ['V',  '3', 24, 'PDIN'], 
                                      ['I',  '1',  4, 'DFB'], 
                                      ['GND', '0', 3, 'GND'], 
                                      ['I',  '2', 6, 'HEAT'], 
                                      ['V',  '4', 26, 'PDREF']] 
channel_definitions["DFB_LIV_balance"] = [['None',  '1', 20, 'None'], 
                                          ['None',  '2', 22, 'None'], 
                                          ['V',  '3', 24, 'PDIN'], 
                                          ['I',  '1',  4, 'DFB'], 
                                          ['GND', '0', 3, 'GND'], 
                                          ['I',  '2', 6, 'HEAT'], 
                                          ['V',  '4', 26, 'PDREF']] 
channel_definitions["Bend_loss"] = [['None',  '1', 20, 'None'], 
                                    ['None',  '2', 22, 'None'], 
                                    ['V',  '3', 24, 'PDIN'], 
                                    ['I',  '1',  '4', 'DFB'], 
                                    ['GND', '0', 3, 'GND'], 
                                    ['None',  '2', 6, 'None'], 
                                    ['V',  '4', 26, 'PDREF']] 
channel_definitions["SOA_gain"] = [['V',  '1', 20, 'PDOUT'], 
                                   ['V',  '2', 22, 'PDREFL'], 
                                   ['V',  '3', 24, 'PDIN'], 
                                   ['I',  '1',  4, 'DFB'], 
                                   ['GND', '0', 3, 'GND'], 
                                   ['I',  '2', 6, 'SOA'], 
                                   ['V',  '4', 26, 'PDREF']] 















