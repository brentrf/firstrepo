# This code opens a batch of NPY files (specified by user)
# which are assumed to contain a 2D array of values that represent optical power
# at different points on RECTANGULAR DETECTOR
# The POWER values are converted to Radiant intensity by dividing by solid angle ~ sin(theta)
# and then resampled and plotted on a X-Y Viewing Angle Chart
# Final Plots are saved as JPG

import os
import tkinter as tk
from tkinter import filedialog
import numpy as np
import struct
import matplotlib.pyplot as plt
from scipy.interpolate import griddata


#User: SELECT NPY files
root = tk.Tk()
root.withdraw()
print("SELECT NPY FILES CONTAINING *RECT* DETECTOR DATA")
file_paths = filedialog.askopenfilenames(filetypes=[("Zemax Detector Data Files","*.NPY")])


for count,filename in enumerate(file_paths):
    #filename = file_paths[0]
    wkspFldr = os.path.dirname(filename)  #return folder path where data gotten from
    Power_v_XY = np.load(filename)

    Npts_Y = np.size(Power_v_XY,0)
    Npts_X = np.size(Power_v_XY,1)
    Ys = np.linspace(0,Npts_Y/Npts_X,Npts_Y)
    Xs = np.linspace(0,1,Npts_X)

    # PLOT 1: Power v. X,Y (Square Matrix Input)
    fig0 = plt.figure()   #fig1, ax = plt.subplots(nrows=1, ncols=1)
    plt.pcolor(Xs, Ys , Power_v_XY)
    plt.xlabel('X [rel to Detector Width]')
    plt.ylabel('Y [rel to Detector Width]')
    plt.colorbar()
    plt.title(filename.split("/")[-1]+'\n'+'Input Data:  Rel. Power [W] v X,Y')
    outfilename = filename.split("/")[-1][:-4]+".png"
    plt.savefig(wkspFldr+"/"+outfilename)
    print("Done with: "+filename.split("/")[-1])


print("... Finished with "+str(count+1)+" files processed...")