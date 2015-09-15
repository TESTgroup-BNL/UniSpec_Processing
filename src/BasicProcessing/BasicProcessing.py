'''
Created on Aug 4, 2015

@author: amcmahon
'''

import os.path
import configparser
import sys

import numpy as np
from scipy import interpolate
from math import floor, ceil, log10

import matplotlib.pyplot as plt



sys.path.append('C:\Python34')
sys.path.append('C:\Python34\Lib')
sys.path.append('C:\Python34\DLLs')
sys.path.append('C:\Python34\Lib\site-packages')

class consts:
    header = 0
    data = 1
    CH_B_WL = 0
    CH_B = 1
    CH_A_WL = 2
    CH_A = 3 
    WL_Lims = 2
    CH_B_WL_Start = 0
    CH_B_WL_End = 1
    CH_A_WL_Start = 2
    CH_A_WL_End = 3

class UnispecProcessing:
    SourcePath = ""
    WP_identifier = ""
    HeaderLines = ""
    WPs = [""] # * 3
    Stops = [""] # * 200
    WP_count = 0
    stop_count = 0
    
  
    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        
        InputParams = ""        
        InputParams = config['Input']
        self.SourcePath = InputParams['SourcePath']
        self.WP_identifier = InputParams['WP_Identifier']
        self.HeaderLines = int(InputParams['HeaderLines'])

    def GetFileLists(self):
        for file in os.listdir(self.SourcePath):
            if file.endswith(".spu"):
                if file.endswith(self.WP_identifier + ".spu"):
                    self.WPs[-1] = file
                    self.WPs.append("") 
                else:
                    self.Stops[-1] = file                    
                    self.Stops.append("")                

        self.WP_count = len(self.WPs) - 1
        self.stop_count = len(self.Stops) - 1
        print("Found " + str(self.WP_count) + " white plates and " + str(self.stop_count) + " stops in dir " + self.SourcePath + ".\n")
        return self.WP_count, self.stop_count
            

    def ReadFiles(self, flist, headerlen):

        outdata = [[[None],[None]] for item in range(0, len(flist)-1)]
        
        for i in range(0, len(flist)-1):
#            Open File
            sf = open(self.SourcePath + "\\" + flist[i], "Ur")
            data = sf.readlines()
            
#            Read Header
            outdata[i][0] = data[0:headerlen - 1]
            
#            Read Spectra
            outdata[i][1] = [[float(l) for l in line.split("\t")] for line in data[headerlen + 1:]]
                      
            sf.close()
        return outdata

            
    def ReadHeader(self, sff):
        header = [None] * self.HeaderLines
        for i in range(0,self.HeaderLines - 1):
            header[i] = sff.readline()
        return header
    
    #Returns an array indexed as: [file #][CH_B/CH_A][WL]
    def CheckSaturation_WL(self, data):
        sat = [[[None], [None]] for item in range(0, len(data))]
        for i in range(0,len(data)):     
            for k, val in enumerate([row[consts.CH_B] for row in [d[consts.data] for d in data][i]]):
                if (val >= 65535):
                    sat[i][0].append(data[i][consts.data][k][consts.CH_B_WL])
            for k, val in enumerate([row[consts.CH_A] for row in [d[consts.data] for d in data][i]]):
                if (val >= 65535):
                    sat[i][1].append(data[i][consts.data][k][consts.CH_A_WL])
            del(sat[i][0][0]) 
            del(sat[i][1][0])
        return sat
 
     #Returns an array indexed as: [idx][file #/CH_B/CH_A]
    def CheckSaturation(self, data):
        sat = [None]
        for i in range(0,len(data)):  
            satcount_A = 0   
            satcount_B = 0
            for k, val in enumerate([d[consts.data] for d in data][i]):
                if (val[consts.CH_B] >= 65535):
                    satcount_B += 1
                if (val[consts.CH_A] >= 65535):
                    satcount_A += 1    
            if (satcount_A > 0 or satcount_B > 0):     
                sat.append([i, satcount_B, satcount_A])
        del(sat[0]) 
        return sat   
    
                
    def RemoveSaturated(self, orig_data, sat_data):
        for idx, item in enumerate(reversed(sat_data)):
            del(orig_data[item[0]])
   
    def flatten(self, l, ltypes=(list, tuple)):
        ltype = type(l)
        l = list(l)
        i = 0
        while i < len(l):
            while isinstance(l[i], ltypes):
                if not l[i]:
                    l.pop(i)
                    i -= 1
                    break
                else:
                    l[i:i + 1] = l[i]
            i += 1
        return ltype(l)             
    
    def Interp(self,data):
        newdata = np.array([])
        limlist = [0, 0, 0, 0]
        for f_idx, file in enumerate(data):   
           
            lims = file[consts.header][consts.WL_Lims]
            limlist[consts.CH_A_WL_Start], limlist[consts.CH_A_WL_End], limlist[consts.CH_B_WL_Start], limlist[consts.CH_B_WL_End] = [float(s.replace('"','')) for s in lims.split() if s[0].isdigit()]
            
            WL_min = ceil(max(limlist[0::2]))
            WL_max = floor(min(limlist[1::2]))
            
            xnew = np.arange(WL_min, WL_max, 1)
            newdata = np.resize(newdata, (len(data), 3, len(xnew)))
            newdata[f_idx, 0] = list(xnew)
           
            #newdata.append([])
            for chan_idx, chan in enumerate([consts.CH_B_WL, consts.CH_A_WL]):
                x = [row[chan] for row in [d[consts.data] for d in data][f_idx]]
                y = [row[chan + 1] for row in [d[consts.data] for d in data][f_idx]]
                f = interpolate.interp1d(x,y)
                ynew = f(xnew)
                
                newdata[f_idx, chan_idx  + 1] = list(ynew)
        
        #del(newdata[-1])
                #plt.plot(x, y, 'o', xnew, ynew, '-')
                #plt.show()
        
        return newdata
    
    def AvgWPs(self,data):
        newdata = np.array(np.zeros_like(data[0]))
        newdata[0] = data[0,0]
        newdata[1] = np.average(data[:,1,:], axis=0)
        newdata[2] = np.average(data[:,2,:], axis=0)
        return newdata
    
    def plot_Averaging(self,orig_data,avg_data):
        for chan_idx, chan in enumerate(['Chan B', 'Chan A']):
            axs = plt.subplot(1, 2, chan_idx + 1)  
            plt.title(chan) 
            for f_idx, f in enumerate(orig_data):
                axs.plot(f[0], f[chan_idx + 1], '-', label='WP ' + str(f_idx))           
            axs.plot(avg_data[0], avg_data[chan_idx + 1], '-', label='Average')   
        plt.show()
        return 0
    
    def Refl_Abs(self,data):
        refl = np.array(np.zeros((len(data),2,len(data[0, 0]))))
        absor = np.array(np.zeros((len(data),2,len(data[0, 0]))))
                            
        for s_idx, stop in enumerate(data):
            refl[s_idx, 0] = stop[0]
            refl[s_idx, 1] = stop[1] / stop[2]

            absor[s_idx, 0] = stop[0]
            absor[s_idx, 1] = [-log10(r) for r in refl[s_idx, 1]]
        
        return refl, absor
    
    def plot_R_A(self,R_data,A_data,idx):
        data = [R_data, A_data]
        for p_idx, param in enumerate(['Reflectance', 'Absorption']):
            axs = plt.subplot(2, 1, p_idx + 1)  
            plt.title(param) 
            axs.plot(data[p_idx][idx, 0], data[p_idx][idx, 1], '-')           
            axs.plot(data[p_idx][idx, 0], data[p_idx][idx, 1], '-')   
        plt.show()
        return 0
    
    def WriteOutput(self,data,path,filename):
        
        if (os.path.isfile(path + '/' + filename) == True) :
            n = 0
            exists = True
            while (exists) :
                n += 1
                if (n > 1):
                    filename = filename[:len(filename) - 6] + "_" + str(n) + filename[-4:]
                else:
                    filename = filename[:len(filename) - 4] + "_" + str(n) + filename[-4:]
                exists = os.path.isfile(path + '/' + filename)
    
        print("Writing file: " + filename)    
        
        fh = open(path + r'\\' + filename, "a")
        
        #Write header
        fh.write("Stop," + ",".join(['%f' % num for num in data[0,0]])) #str(data[0,0])[2:-2].replace("  ", ",").replace(" ","").replace("\n",""))
       
        for s_idx, stop in enumerate(data):
            fh.write("\n" + str(s_idx) + "," + ",".join(['%f' % num for num in stop[1]])) #str(stop[1])[2:-2].replace("  ", ",").replace(" ","").replace("\n",""))
        
        fh.flush()
        fh.close()
        
        print("Wrote " + str(len(data)) + " row(s).\nFile closed.") 
        
        return 0