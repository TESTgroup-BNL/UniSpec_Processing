'''
Created on Aug 4, 2015

@author: amcmahon
'''
from BasicProcessing import UnispecProcessing
from BasicProcessing import consts
import os.path
import sys


def main():
    """
    Main function for generating CSV files from a directory of Unispec data.
    
    Input/Output paths, white plate identifier string and header size should be specified in "config.txt".
    
    Outputs one CSV file per tram run, where each row represets a stop and columns are wavelengths interpolated to 1nm.
    
    """

#    path = str(os.path.realpath('.'))
    # Edited by SPS on 11/06/2015
    #spec = UnispecProcessing(path + r'\config.txt')
#    spec = UnispecProcessing(os.path.join(path, "config.txt"))
    spec = UnispecProcessing(os.path.join("src", "config.txt"))
    
    run_count, WP_count, stop_count = spec.getFileLists()
    
    for run in range(0,run_count):
        
        if (WP_count[run] == 0) or (stop_count[run] == 0):
            continue
    
        WP_data = [[[None], [None]] for item in range(0,WP_count[run])]
        Stop_data = [[[None], [None]] for item in range(0,stop_count[run])]
        sat = [[None], [None]]
        
        
        #When getting data from these, they are formatted as:
        #    var[file index][header/data][row index][CH_B_WL/CH_B/CH_A_WL/CH_A]
        WP_data = spec.readFiles(spec.WPs[run], spec.HeaderLines)
        Stop_data = spec.readFiles(spec.Stops[run], spec.HeaderLines)
        
        #Formatted as:
        #    var[file index][CH_B/CH_A][WL]
        #    value is the WL saturation occurred at
        sat_WP = spec.checkSaturation(WP_data)
        sat_stops = spec.checkSaturation(Stop_data)
        
        print("Saturated Measurement Count\n\t\tCh_B\tCh_A")
        for idx, curfile in enumerate(sat_WP):
            print("WP " + str(idx) + ":\t\t" + str(curfile[1]) + "\t" + str(curfile[2])) 
        for idx, curfile in enumerate(sat_stops):
            print("Stop " + str(idx) + ":\t\t" + str(curfile[1]) + "\t" + str(curfile[2]))        
        print("\n" + str(len(sat_WP)) + " WPs and " + str(len(sat_stops)) + " stops saturated.")
        
        #spec.RemoveSaturated(WP_data, sat_WP)
        #spec.RemoveSaturated(Stop_data, sat_stops)
        
        #Subtract dark current values
        darkData = spec.readFiles([spec.darkSource], spec.darkHeaderLines)
        WP_data_darkCorrected = spec.subtractDarkCurrent(WP_data, darkData, spec.swapChannels)
        Stop_data_darkCorrected = spec.subtractDarkCurrent(Stop_data, darkData, spec.swapChannels)
        
        #Formatted as:
        #    var[file, WL/CH_B/CH_A] = [1 dim array of values]
        intdata_WPs = spec.interp(WP_data_darkCorrected)
        intdata_Stops = spec.interp(Stop_data_darkCorrected)
        
        avg_WP = spec.avgWPs(intdata_WPs)
        
        #Plot all WPs with average
        #spec.plot_Averaging(intdata_WPs, avg_WP)
        
        R = spec.refl(intdata_Stops, avg_WP)
        
        #Plot reflectance for a particular stop
        #    plot_R_A(Refl data, Stop #)
        #spec.plot_R(R,20)
        
        dt = spec.getDateTime(WP_data[0])
        
        spec.writeOutput(R, spec.OutputPath, spec.OutputPrefix + dt[consts.date] + "__" + dt[consts.time].replace(':','_') + ".csv")
        
        
if __name__ == "__main__":
    main()