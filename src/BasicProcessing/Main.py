'''
Created on Aug 4, 2015

@author: amcmahon
'''
from BasicProcessing import UnispecProcessing
from BasicProcessing import consts
import os.path
import sys


path = str(os.path.realpath('.'))
Spec = UnispecProcessing(path + r'\config.txt')

WP_count, stop_count = Spec.GetFileLists()

WP_data = [[[None], [None]] for item in range(0,WP_count)]
Stop_data = [[[None], [None]] for item in range(0,stop_count)]
sat = [[None], [None]]


#When getting data from these, they are formatted as:
#    var[file index][header/data][row index][CH_B_WL/CH_B/CH_A_WL/CH_A]
WP_data = Spec.ReadFiles(Spec.WPs, Spec.HeaderLines)
Stop_data = Spec.ReadFiles(Spec.Stops, Spec.HeaderLines)

#Formatted as:
#    var[file index][CH_B/CH_A][WL]
#    value of var is the WL saturation occurred at
sat_WP = Spec.CheckSaturation(WP_data)
sat_stops = Spec.CheckSaturation(Stop_data)

print("Saturated Measurement Count\n\tCh_B\tCh_A")
for idx, curfile in enumerate(sat_WP):
    print("WP " + str(idx) + ":\t" + str(curfile[1]) + "\t" + str(curfile[2])) 
for idx, curfile in enumerate(sat_stops):
    print("Stop " + str(idx) + ":\t" + str(curfile[1]) + "\t" + str(curfile[2]))        
print("\n" + str(len(sat_WP)) + " WPs and " + str(len(sat_stops)) + " stops saturated.")

Spec.RemoveSaturated(WP_data, sat_WP)
Spec.RemoveSaturated(Stop_data, sat_stops)

#Formatted as:
#    var[file, WL/CH_B/CH_A] = [1 dim array of values]
intdata_WPs = Spec.Interp(WP_data)
intdata_Stops = Spec.Interp(Stop_data)

avg_WP = Spec.AvgWPs(intdata_WPs)

#Plot all WPs with average
#Spec.plot_Averaging(intdata_WPs, avg_WP)

R, A = Spec.Refl_Abs(intdata_Stops)

#Plot reflectance and absorption for a particular stop
#    plot_R_A(Refl data, Abs data, Stop #)
Spec.plot_R_A(R,A,0)

Spec.WriteOutput(R, "c:\\UniSpec\\Test", "test_R.csv")