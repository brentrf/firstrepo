# This code opens a 3 NPY files (specified by user)
# which are assumed to contain a 2D array of values that represent optical power from a Zemax detector
# One File is for Red  --->  X
# One File is for Green -->  Y
# One File is for Blue, -->  Z

# The code computes (and stores, displays) a Matrix representing    **Deviation** from Color Balance at Center*
# where deviation of color balance is defined by deviation = ((x-x0)^2 + (y-y0)^2)^0.5
# and where x = X / (X+Y+Z)
# and where y = Y / (X+Y+Z)
# and where x0, y0 are the reference values at the center of detector
# and XYZ are the CIE tristimulus values:  X = integral_over_wavelengths( OpticalPowerRed * PhotopicResponse)
#                                          etc.


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
print("SELECT NPY FILES CONTAINING DETECTOR DATA for X (RED):")
file_path_X = filedialog.askopenfilename(filetypes=[("Zemax Detector Data Files","*.NPY")])
print("SELECT NPY FILES CONTAINING DETECTOR DATA for Y (GREEN):")
file_path_Y = filedialog.askopenfilename(filetypes=[("Zemax Detector Data Files","*.NPY")])
print("SELECT NPY FILES CONTAINING DETECTOR DATA for Z (BLUE):")
file_path_Z = filedialog.askopenfilename(filetypes=[("Zemax Detector Data Files","*.NPY")])

wkspFldr = os.path.dirname(file_path_X)  # return folder path where data gotten from

#Load 2D Array Data for X,Y,Z tristimulus values
colorX = np.load(file_path_X)
colorY = np.load(file_path_Y)
colorZ = np.load(file_path_Z)

#check that array sizes are same
if (colorX.shape[0] != colorY.shape[0]) or (colorX.shape[0] != colorZ.shape[0]) or (colorX.shape[1] != colorY.shape[1]) or (colorX.shape[1] != colorZ.shape[1]):
    print("input matrices do not have same dimensions (sizes)")
else:
    print("All Good")

#generate XY Angle Space that matches input size
POL_x = np.linspace(-90, 90, colorX.shape[1])
POL_y = np.linspace(-90, 90, colorX.shape[0])
POL_XX, POL_YY = np.meshgrid(POL_x, POL_y)
POL_RR = (POL_XX**2 + POL_YY**2)**0.5


#Compute ColorBalance & Deviation
x = colorX / (colorX + colorY + colorZ)
y = colorY / (colorX + colorY + colorZ)

#find center
x0 = x[int(x.shape[0]/2)][int(x.shape[1]/2)]
y0 = y[int(y.shape[0]/2)][int(y.shape[1]/2)]
r_colordeviation = ((x-x0)**2+(y-y0)**2)**0.5  #definition of DEVIATION
r_colordeviation[ POL_RR > 88] = 0   #set points outside circle to zero



#Plot Color Deviation
plt.figure()
plt.pcolor(POL_XX, POL_YY, r_colordeviation)
plt.xlabel('Left-Right Angle [deg]')
plt.ylabel('Up-Down Angle [deg]')
plt.colorbar()
plt.title("Deviation of CIE1931(x,y) ColorBalance v. ViewAngle")
outfilename = file_path_X.split("/")[-1][:-4] + "_ColorDeviation.png"
plt.savefig(wkspFldr + "/" + outfilename)

#Save Text
outfilename = file_path_X.split("/")[-1][:-4] + "_ColorDeviation.txt"
np.savetxt(wkspFldr+"/"+outfilename, r_colordeviation)