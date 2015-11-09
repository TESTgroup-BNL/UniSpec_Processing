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


# Hard-coded paths - TO BE REMOVED
sys.path.append('C:\Python34')
sys.path.append('C:\Python34\Lib')
sys.path.append('C:\Python34\DLLs')
sys.path.append('C:\Python34\Lib\site-packages')

class consts:
    """Class of constants to make understanding various lists/arrays simpler."""
    
    header = 0
    data = 1
    
    CH_B_WL = 0
    CH_B = 1
    CH_A_WL = 2
    CH_A = 3 
    
    WL_Lims = 2
    datetime = 1
    
    CH_B_WL_Start = 0
    CH_B_WL_End = 1
    CH_A_WL_Start = 2
    CH_A_WL_End = 3
    
    date = 0
    time = 1
    
    int_WL = 0
    int_CH_B = 1
    int_CH_A = 2
    

class UnispecProcessing:
    """Class for Unispec data processing"""
    
    SourcePath = ""
    OutputPath = ""
    OutputPrefix = ""
    WP_identifier = ""
    HeaderLines = ""
    #: Array of white plate files indexed as *[Run #][WP #]* 
    WPs = [[]] # * 3
    #: Array of stop files indexed as *[Run #][Stop #]* 
    Stops = [[]] # * 200 
    WP_count = 0
    stop_count = 0
    run_count = 0
    
  
    def __init__(self, config_file):
        """Initializes the class.  Reads input/output parameters from configuration file.
        
        :param config_file: Text file containing input/output configuration
        :type config_file: String
        
        """
        
        config = configparser.ConfigParser()
        config.read(config_file)
        
        InputParams = ""        
        InputParams = config['Input']
        self.SourcePath = InputParams['SourcePath']
        self.WP_identifier = InputParams['WP_Identifier']
        self.HeaderLines = int(InputParams['HeaderLines'])
        OutputParams = ""
        OutputParams = config['Output']
        self.OutputPath = OutputParams['OutputPath'] 
        self.OutputPrefix = OutputParams['OutputPrefix']


    def GetFileLists(self):
        """Reads input directory specified in config file and populates class arrays :data:`~BasicProcessing.UnispecProcessing.WPs` and :data:`~BasicProcessing.UnispecProcessing.Stops` with file paths/names that are to be processed.
        
        File sets are split based on where white plates are identified date/time (assuming they are included in the filename) and .
        
        :return: # of runs, # of white plates, # of stops
        :rtype: Integer, Integer, Integer

        """
         
        WP_break = False
        run = 0
        flist = os.listdir(self.SourcePath)
        flist.sort()
        for file in flist:
            if file.endswith(".spu"):
                if file.endswith(self.WP_identifier + ".spu"):
                    if WP_break:
                        run += 1
                        self.WPs.append([])
                        self.Stops.append([])
                        WP_break = False
                    self.WPs[run].append(file)
                else:
                    WP_break = True                        
                    self.Stops[run].append(file)                    

        self.WP_count = [len(self.WPs[i]) - 1 for i in range(0, run+1)]
        self.stop_count = [len(self.Stops[i]) - 1 for i in range(0, run+1)]
        print("Found " + str(run) + " runs in " + self.SourcePath + ".\n\tWPs\tStops\n")
        for r in range(0, run+1):
            print(str(r) + ":\t" + str(self.WP_count[r]) + "\t"+ str(self.stop_count[r]))
        self.run_count = run +1
        return self.run_count, self.WP_count, self.stop_count
            

    def ReadFiles(self, flist, headerlen):
        """Reads Unispec output files into a list, separating header and spectrum data for each file.
        
        :param flist: List of files to read (as returned from :func:`~BasicProcessing.UnispecProcessing.GetFileLists`)
        :type flist: Nested list of Strings
        :param headerlen: Constant defining how many lines the header consists of
        :type headerlen: Integer
        :returns: List of data indexed as [file index][:const:`~BasicProcessing.consts.header` / :const:`~BasicProcessing.consts.data`][row index][:const:`~BasicProcessing.consts.CH_B_WL` / :const:`~BasicProcessing.consts.CH_B` / :const:`~BasicProcessing.consts.CH_A_WL` / :const:`~BasicProcessing.consts.CH_A`]
        :rtype: Nested list of Strings
        
        """

        outdata = [[[None],[None]] for item in range(0, len(flist)-1)]
        
        for i in range(0, len(flist)-1):
#            Open File
#           *Edited by SPS on 11/06/2015
#           sf = open(self.SourcePath + "\\" + flist[i], "Ur")
            sf = open(os.path.join(self.SourcePath,flist[i]), "Ur")
            data = sf.readlines()
            
#            Read Header
            outdata[i][0] = data[0:headerlen - 1]
            
#            Read Spectra
            outdata[i][1] = [[float(l) for l in line.split("\t")] for line in data[headerlen + 1:]]
                      
            sf.close()
        return outdata

        """            
        def ReadHeader(self, sff):
        header = [None] * self.HeaderLines
        for i in range(0,self.HeaderLines - 1):
            header[i] = sff.readline()
        return header
        """
    
    
    def CheckSaturation_WL(self, data):
        """
        Returns a list of wavelengths with saturated values.
        
        :param data: List of full run data (as returned from :func:`~BasicProcessing.UnispecProcessing.ReadFiles`)
        :type data: Nested list of Strings
        :returns: List wavelengths indexed as *[file index][Ch B(0) / Ch A(1)]*
        :rtype: Nested list of Floats
        
        """
        
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
 
 
    def CheckSaturation(self, data):
        """
        Returns a list with a count of saturated values per channel for each file.
        
        :param data: List of full run data (as returned from :func:`~BasicProcessing.UnispecProcessing.ReadFiles`)
        :type data: Nested list of Strings
        :returns: List of Arrays *[file index, Ch B, Ch A]*
        :rtype: [Integer, Integer, Integer]
        
        """
        
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
        """
        Removes data from files indexed in **sat_data** from **orig_data**.
        
        :param orig_data: List of full run data (as returned from :func:`~BasicProcessing.UnispecProcessing.ReadFiles`)
        :type orig_data: Nested list of Strings
        :param sat_data: List of Arrays *[file index, Ch B, Ch A]*
        :returns: List of reduced run data (maintains list format)
        :rtype: Nested list of Strings
        
        """   
        for idx, item in enumerate(reversed(sat_data)):
            del(orig_data[item[0]])

    """   
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
    """    
    
    def Interp(self,data):
        """
        Interpolates data to 1 nm.
        
        Only includes wavelengths where data is present for both channels.
        
        :param data: List of run data (as returned from :func:`~BasicProcessing.UnispecProcessing.ReadFiles`)
        :type data: Nested list of Strings
        :returns: Array of interpolated data indexed as [file #, :data:`~BasicProcessing.consts.int_WL` / :data:`~BasicProcessing.consts.int_CH_B` / :data:`~BasicProcessing.consts.int_CH_A`]
        :rtype: [file, WL/Ch B/Ch A] Array of Floats
        
        """
        
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
    
    
    def GetDateTime(self, file):
        """
        Gets the time and date from a specified file.
        
        :param file: List of data from file (from full run data with file index specified)
        :type file: Nested list of data
        :returns: Array containing date and time indexed as [:const:`~BasicProcessing.consts.date` / :const:`~BasicProcessing.consts.time`]
        :rtype: [Date/Time] String
        
        """
        
        dt = file[consts.header][consts.datetime].replace('"Time:    ','').replace('"\n','').split('  ')
        return dt
    
    
    def AvgWPs(self,data):
        """
        Averages values for each channel and file in **data**.
        
        :param data: Array of interpolated data (as returned from :func:`~BasicProcessing.UnispecProcessing.Interp`)
        :type file: Array of Floats indexed as [File, :data:`~BasicProcessing.consts.int_WL` / :data:`~BasicProcessing.consts.int_CH_B` / :data:`~BasicProcessing.consts.int_CH_A`]
        :returns: Array of averaged values for each file
        :rtype: Array of Floats indexed as [:data:`~BasicProcessing.consts.int_WL` / :data:`~BasicProcessing.consts.int_CH_B` / :data:`~BasicProcessing.consts.int_CH_A`]
        
        """
        newdata = np.array(np.zeros_like(data[0]))
        newdata[self.consts.int_WL] = data[0,0]
        newdata[self.consts.int_CH_B] = np.average(data[:,1,:], axis=0)
        newdata[self.consts.int_CH_A] = np.average(data[:,2,:], axis=0)
        return newdata
    
    
    def plot_Averaging(self,orig_data,avg_data):
        """
        Creates a plot comparing a collection of data with its average.
        
        Useful for checking white plate averaging.
        
        :param orig_data: Array of interpolated data (as returned from :func:`~BasicProcessing.UnispecProcessing.Interp`)
        :type orig_data: Array of Floats indexed as [File, :data:`~BasicProcessing.consts.int_WL` / :data:`~BasicProcessing.consts.int_CH_B` / :data:`~BasicProcessing.consts.int_CH_A`]
        :param avg_data: Array of averaged values for each file
        :type avg_data: Array of Floats indexed as [:data:`~BasicProcessing.consts.int_WL` / :data:`~BasicProcessing.consts.int_CH_B` / :data:`~BasicProcessing.consts.int_CH_A`]
        :returns: 0
        :rtype: Integer
        
        """
        for chan_idx, chan in enumerate(['Chan B', 'Chan A']):
            axs = plt.subplot(1, 2, chan_idx + 1)  
            plt.title(chan) 
            for f_idx, f in enumerate(orig_data):
                axs.plot(f[0], f[chan_idx + 1], '-', label='WP ' + str(f_idx))           
            axs.plot(avg_data[0], avg_data[chan_idx + 1], '-', label='Average')   
        plt.show()
        return 0
    
    
    def Refl(self,Stop_data, WP_data):
        """
        Calculates reflectance for an array of data.
        
        :param Stop_data: Stop data to be used 
        :type Stop_data: Array of Floats indexed as [File, :data:`~BasicProcessing.consts.int_WL` / :data:`~BasicProcessing.consts.int_CH_B` / :data:`~BasicProcessing.consts.int_CH_A`]
        :param WP_data: White plate data to be used (as returned from :func:`~BasicProcessing.UnispecProcessing.AvgWPs`)
        :type WP_data: Array of Floats indexed as [:data:`~BasicProcessing.consts.int_WL` / :data:`~BasicProcessing.consts.int_CH_B` / :data:`~BasicProcessing.consts.int_CH_A`]
        :returns: Array of reflectance values for each file
        :rtype: [File, WL] Float
        
        """
        
        refl = np.array(np.zeros((len(Stop_data),2,len(Stop_data[0, 0]))))

        for s_idx, stop in enumerate(Stop_data):
            refl[s_idx, 0] = stop[self.consts.int_WL]
            #Reflec = (I_up / I_WP) * (I_trg / I_up)
            refl[s_idx, 1] = (stop[self.consts.int_CH_A] / WP_data[self.consts.int_CH_B]) * (stop[self.consts.int_CH_B] / stop[self.consts.int_CH_A])
        
        return refl
    
    
    def plot_R(self,R_data,idx):
        """
        Creates a plot from reflectance data.
        
        :param R_data: Array of reflectance data (as returned from :func:`~BasicProcessing.UnispecProcessing.Refl`)
        :type R_data: Array of Floats indexed as [File, :data:`~BasicProcessing.consts.int_WL` / :data:`~BasicProcessing.consts.int_CH_B` / :data:`~BasicProcessing.consts.int_CH_A`]
        :param idx: Array of averaged values for each file
        :type idx: Array of Floats indexed as [:data:`~BasicProcessing.consts.int_WL` / :data:`~BasicProcessing.consts.int_CH_B` / :data:`~BasicProcessing.consts.int_CH_A`]
        :returns: 0
        :rtype: Integer
        
        """
        plt.title('Reflectance') 
        plt.plot(R_data[idx, 0], R_data[idx, 1], '-')           
        plt.show()
        return 0
    
    def WriteOutput(self,data,path,filename):
        """
        Creates a CSV file of the reflectance data in *data*.
        
        A file should be generated for each set of stops.  Each row then represents a stop and each column corresponds with a wavelength.
        
        :param data: Array of reflectance data (as returned from :func:`~BasicProcessing.UnispecProcessing.Refl`)
        :type data: Array of Floats indexed as [File, :data:`~BasicProcessing.consts.int_WL` / :data:`~BasicProcessing.consts.int_CH_B` / :data:`~BasicProcessing.consts.int_CH_A`]
        :param path: Directory to save the generated file in
        :type path: String
        :param filename: Filename to use for the generated file
        :type filename: String
        :returns: 0
        :rtype: Integer
        
        """
        
        # Added by SPS 11/06/2015 to create output directory on-the-fly
        if not os.path.exists(os.path.dirname(os.path.join(path,filename))):
            os.makedirs(os.path.dirname(os.path.join(path,filename)))
        
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
        
        # *Edited by SPS 11/06/2015
        #fh = open(path + r'\\' + filename, "a")
        fh = open(os.path.join(path,filename), "a")

        #Write header
        fh.write("Stop," + ",".join(['%f' % num for num in data[0,0]])) #str(data[0,0])[2:-2].replace("  ", ",").replace(" ","").replace("\n",""))
       
        for s_idx, stop in enumerate(data):
            fh.write("\n" + str(s_idx) + "," + ",".join(['%f' % num for num in stop[1]])) #str(stop[1])[2:-2].replace("  ", ",").replace(" ","").replace("\n",""))
        
        fh.flush()
        fh.close()
        
        print("Wrote " + str(len(data)) + " row(s).\nFile closed.") 
        
        return 0