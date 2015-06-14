# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 22:12:56 2013

@author: xujy2013
"""

import numpy as np
import pylab as pl
import sys
from pylab import *

def calc_CDF_data(array_data):
    pb = []
    for i in range(len(array_data)):
        if not math.isnan(array_data[i]):
            pb.append(array_data[i])
    
    pb_sorted = sorted(pb)
    
    sorted_arr = []
    pb_len = len(pb_sorted)
    for j in range(len(pb_sorted)):
        sorted_arr.append((pb_sorted[j], float(j)/float(pb_len)*100))
        
    return np.array(sorted_arr, dtype=[('x', '<f4'), ('y', '<f4')])
    
def get_intkey_valued_data(array_data, key, value, key2):
    key2_value = []
    for i in range(len(array_data)):
        if array_data[key][i] == value:
            key2_value.append(array_data[key2][i])
    
    return key2_value
    
def get_strkey_valued_data(array_data, key, value, key2, if_contain, nets):
    key2_value = []
    print len(nets)
    for i in range(len(array_data)):
        if if_contain and array_data[key][i]==value:
            key2_value.append(array_data[key2][i])
        if not if_contain and array_data[key][i] not in nets:
            key2_value.append(array_data[key2][i])
    
    return key2_value
    
def get_strkey_valued_all_data(array_data, key, value):
    rst_arr=[]
    for i in range(len(array_data)):
        if array_data[key][i] == value:
            rst_arr.append(array_data[i])    
    
    return np.array(rst_arr, array_data.dtype)
    
    
def get_particle_value(sorted_ar, particle):
    length=len(sorted_ar)
    if length == 0:
        return 0
    index=int(particle*length/100)
    return sorted_ar[index]

def get_xticklabels(time_str, counts):
    ticks_count=30
    tick_str=[]
    if counts==1:
        ticks_count=1
        tick_str.append(str(time_str)[4:8])
    elif counts<=30:
        ticks_count=counts
        for i in range(counts):
            tick_str.append(str(time_str[i])[4:8])
    else:
        step=counts/30.0
        for i in range(30):
            str_idx=int(i*step+step)
            tick_str.append(str(time_str[str_idx-1])[4:8])

    return ticks_count, tick_str    
