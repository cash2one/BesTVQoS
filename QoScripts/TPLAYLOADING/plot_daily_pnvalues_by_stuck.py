# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 15:45:52 2015

@author: xujy
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys

from tool_funs import *

reload(sys)
sys.setdefaultencoding("utf-8")

time=sys.argv[1]
ver1=sys.argv[2]
#input=sys.argv[2]
#output=sys.argv[3]
input1="./out/total/pnvalues_of_%s_vod_stuck" % ver1

data=np.loadtxt(input1, delimiter="|", usecols=(1, 3, 4, 5, 6, 7, 8), \
    dtype=[('date', 'i8'), ('p25', 'i8'), ('p50', 'i8'), 
    ('p75', 'i8'), ('p90', 'i8'), ('p95', 'i8'), ('count', 'i8')])
     
                         
data_len=len(np.atleast_1d(data))
ticks_count, time_str=get_xticklabels(data["date"], data_len)
fig=plt.figure(figsize=(10,6),dpi=120)
plt.plot(data['p25'], '*-r', label='p25')
plt.plot(data['p50'], '*-c', label='p50')
plt.plot(data['p75'], '*-m', label='p75')
plt.plot(data['p90'], '*-y', label='p90')
plt.plot(data['p95'], '*-k', label='p95')
plt.xlabel("date")
plt.ylabel("Second")
plt.legend(loc="upper left")
#plt.ylim(0, 20)
plt.ylim(0, max(data['p95']+1))

ax1=plt.gca()
ax1.set_xlim(0, data_len)
ax1.set_xticks(np.linspace(0, data_len, ticks_count+1, endpoint=True))
ax1.set_xticklabels(time_str, rotation=75)

ax2=ax1.twinx()
plt.plot(data['count'], '^--b', label='records')
ax2.set_ylabel("Records")

plt.legend(loc="upper right")
plt.grid()
plt.title("pnvalues of vod stuck of %s" % ver1)

plt.savefig("./png/daily_pn_plot_by_vod_stuck_of_%s_%s.png" % (ver1, time))
