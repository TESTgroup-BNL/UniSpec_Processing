Introduction
============

The purpose of this package is to provide an automated system for generating useful, usable data from dual channel spectrometer data.  It has been developed for the Unispec-DC data format, though only the :func:`~BasicProcessing.UnispecProcessing.ReadFiles` would need to be modified to import data in an alternative format.

There are also project files here for Eclipse (with PyDev) which can be useful for debugging.

There are two main components to the package:

BasicProcessing.py
   Library with all data processing functions
      
Main.py
   Example script for processing data (described in detailed below)


Requirements
============

This has been tested on Python 3.4 and requires the following packages:

- `numpy <http://sourceforge.net/projects/numpy/files/NumPy/>`_
- `scipy <http://sourceforge.net/projects/scipy/files/scipy/>`_
- `matplotlib <http://matplotlib.org/downloads.html>`_ (only needed for plotting)


Main Function Use and Operation
===============================

---
Use
---

To process a set of data using Main.py, the configuration file "Config.txt" should be updated with the appropriate path and filename information and be saved in the same directory as BasicProcessing.py and Main.py.  Main.py can then be called directly with no arguments.  (From a command prompt "python main.py".)


---------
Operation
---------
The main function reads in the configuration options, sets up some lists to pass information between functions and iterates through each run as a group.

First, the object :obj:`Spec` is created from the :class:`~BasicProcessing.UnispecProcessing` class.  The Init function for the class also opens the config file specified and loads the values into class level variables.

.. code-block:: python

    >path = str(os.path.realpath('.'))
    >Spec = UnispecProcessing(path + r'\config.txt')

Then, file lists for runs, white plates and stops are generated.  These lists are also stored within the class.

.. code-block:: python

    >run_count, WP_count, stop_count = Spec.GetFileLists()

For each run (as determined by the poisitions of white plates between stops in chronological order), arrays are created for the "raw" imported data and saturation counts.

.. code-block:: python

    >for run in range(0,run_count):
    >    
	>	#There must be at least one white plate and one stop for a run to produce any useful data, otherwise skip it.
    >    if (WP_count[run] == 0) or (stop_count[run] == 0):
    >        continue
    >
    >    WP_data = [[[None], [None]] for item in range(0,WP_count[run])]
    >    Stop_data = [[[None], [None]] for item in range(0,stop_count[run])]
    >    sat = [[None], [None]]

These arrays are populated by :func:`~BasicProcessing.UnispecProcessing.ReadFiles` with the white plates and stops as two seperate groups.

.. code-block:: python

    >    WP_data = Spec.ReadFiles(Spec.WPs[run], Spec.HeaderLines)
    >    Stop_data = Spec.ReadFiles(Spec.Stops[run], Spec.HeaderLines)


Next, both data sets are checked for saturated values and a count of these are returned.  These counts could be used as a condition for whether or not to keep data from a specific stop/run.

.. code-block:: python

    >    sat_WP = Spec.CheckSaturation(WP_data)
    >    sat_stops = Spec.CheckSaturation(Stop_data)


The counts for each white plate/stop are also printed as a diagnostic.

.. code-block:: python

    >    print("Saturated Measurement Count\n\t\tCh_B\tCh_A")
    >    for idx, curfile in enumerate(sat_WP):
    >        print("WP " + str(idx) + ":\t\t" + str(curfile[1]) + "\t" + str(curfile[2])) 
    >    for idx, curfile in enumerate(sat_stops):
    >        print("Stop " + str(idx) + ":\t\t" + str(curfile[1]) + "\t" + str(curfile[2]))        
    >    print("\n" + str(len(sat_WP)) + " WPs and " + str(len(sat_stops)) + " stops saturated.")


Optionally, saturated stops are removed.

.. code-block:: python

    >    #Spec.RemoveSaturated(WP_data, sat_WP)
    >    #Spec.RemoveSaturated(Stop_data, sat_stops)


The "raw" data is then interpolated to 1 1nm.

.. code-block:: python

    >    intdata_WPs = Spec.Interp(WP_data)
    >    intdata_Stops = Spec.Interp(Stop_data)


All of the white plate values are averaged to a single data set.

.. code-block:: python

    >    avg_WP = Spec.AvgWPs(intdata_WPs)


Optionally, the white plate average can be plotted against all of the individual measurments as a diagnostic.

.. code-block:: python

    >    #Plot all WPs with average
    >    #Spec.plot_Averaging(intdata_WPs, avg_WP)


Next, the reflectance values are calculated.

.. code-block:: python

    >    R = Spec.Refl(intdata_Stops, avg_WP)


These can also be plotted for a particular stop as a diasgnostic.

.. code-block:: python

    >    #Spec.plot_R(R,20)


Finally, the CSV output is generated.  The date and tiem from the first white plate of a given run are used in the filename as a reference.

.. code-block:: python

    >    dt = Spec.GetDateTime(WP_data[0])       
    >    Spec.WriteOutput(R, "c:\\UniSpec\\Test", "test_R_" + dt[consts.date] + "__" + dt[consts.time].replace(':','_') + ".csv")



------------------
Configuration File
------------------

The configuration file is seperated into an Input and an Output section to help organize parameters, especially as future options are potentially added.

.. code-block:: text

	[Input]
	SourcePath = C:\Users\amcmahon\Documents\TEST\UnispecScripts\TestData\2015
	WP_Identifier = 000
	HeaderLines = 10

	[Output]
	OutputPath = C:\\UniSpec\\Test
