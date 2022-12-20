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

#WHITEPOINT @ NORMAL(0)
cx_0 = {'r':0.68, 'g':0.265, 'b':0.135}
cy_0 = {'r':0.32, 'g':0.69, 'b':0.054}
L0   = {'r':0.24,'g':0.69, 'b':0.07}
#calc cx,cy of RGB Mix:
x0_mix = ( cx_0['r']/cy_0['r']*L0['r'] \
        + cx_0['g']/cy_0['g']*L0['g'] \
        + cx_0['b']/cy_0['b']*L0['b'] ) \
        / ( L0['r']/cy_0['r'] + L0['g']/cy_0['g'] + L0['b']/cy_0['b'] )
y0_mix = ( L0['r'] + L0['g']  + L0['b'] ) \
          / ( L0['r']/cy_0['r'] + L0['g']/cy_0['g'] + L0['b']/cy_0['b'] )

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
Pow_Red = np.load(file_path_X)
Pow_Grn = np.load(file_path_Y)
Pow_Blu = np.load(file_path_Z)

#check that array sizes are same
if (Pow_Red.shape[0] != Pow_Grn.shape[0]) or (Pow_Red.shape[0] != Pow_Blu.shape[0]) or (Pow_Red.shape[1] != Pow_Grn.shape[1]) or (Pow_Red.shape[1] != Pow_Blu.shape[1]):
    print("input matrices do not have same dimensions (sizes)")
else:
    print("All Good")

#generate XY Angle Space that matches input size
POL_x = np.linspace(-90, 90, Pow_Red.shape[1])
POL_y = np.linspace(-90, 90, Pow_Red.shape[0])
POL_XX, POL_YY = np.meshgrid(POL_x, POL_y)
POL_RR = (POL_XX**2 + POL_YY**2)**0.5

#Center of Optical Power Matrix
Pow0_Red = Pow_Red[int(Pow_Red.shape[0]/2)][int(Pow_Red.shape[1]/2)]
Pow0_Grn = Pow_Grn[int(Pow_Grn.shape[0]/2)][int(Pow_Grn.shape[1]/2)]
Pow0_Blu = Pow_Blu[int(Pow_Blu.shape[0]/2)][int(Pow_Blu.shape[1]/2)]

#Compute Color-Mix At each Angle
L_red = Pow_Red * L0['r']/Pow0_Red
L_grn = Pow_Grn * L0['g']/Pow0_Grn
L_blu = Pow_Blu * L0['b']/Pow0_Blu
x_mix = ( cx_0['r']/cy_0['r']*L_red  \
        + cx_0['g']/cy_0['g']*L_grn  \
        + cx_0['b']/cy_0['b']*L_blu ) \
        / ( L_red/cy_0['r'] + L_grn/cy_0['g'] + L_blu/cy_0['b'] )
y_mix = ( L_red + L_grn + L_blu ) \
          / ( L_red/cy_0['r'] + L_grn/cy_0['g'] + L_blu/cy_0['b'] )
r_colordeviation_A = ((x_mix-x0_mix)**2+(y_mix-y0_mix)**2)**0.5  #definition of DEVIATION
r_colordeviation_A[ POL_RR > 88] = 0   #set points outside circle to zero

# ********  Alternative Method.... ****************
#Compute TriStimulusValues at each View Angle
X_red = L_red * (cx_0['r'] / cy_0['r'])
X_grn = L_grn * (cx_0['g'] / cy_0['g'])
X_blu = L_blu * (cx_0['b'] / cy_0['b'])
Z_red = (L_red / cy_0['r']) * (1 - cx_0['r'] - cy_0['r'])
Z_grn = (L_grn / cy_0['g']) * (1 - cx_0['g'] - cy_0['g'])
Z_blu = (L_blu / cy_0['b']) * (1 - cx_0['b'] - cy_0['b'])
X_tot = X_red + X_grn + X_blu
Y_tot = L_red + L_grn + L_blu
Z_tot = Z_red + Z_grn + Z_blu
XYZ_tot = np.stack((X_tot,Y_tot,Z_tot),2)
XYZ_tot / XYZ_tot.max()
#chromaticity values
x = X_tot / (X_tot+Y_tot+Z_tot)
y = Y_tot / (X_tot+Y_tot+Z_tot)


#Plot Tristimulus Colors
fig0 = plt.figure
plt.imshow(XYZ_tot,extent=(-90,90,-90,90))
plt.xlabel('Left-Right Angle [deg]')
plt.ylabel('Up-Down Angle [deg]')
plt.title('XYZ Tristimulus Colors  v. ViewAngle\n' + 'file:    '+ file_path_X.split("/")[-1][:-4])
outfilename = file_path_X.split("/")[-1][:-4] + "_TriStimColor_New1.png"
plt.savefig(wkspFldr + "/" + outfilename)


#Compute Deviation Relative to Center
x0 = x[int(x.shape[0]/2)][int(x.shape[1]/2)] #center
y0 = y[int(y.shape[0]/2)][int(y.shape[1]/2)] #center
r_colordeviation_B = ((x-x0)**2+(y-y0)**2)**0.5  #definition of DEVIATION
r_colordeviation_B[ POL_RR > 88] = 0   #set points outside circle to zero

# ********** END of ALTERNATIVE METHOD *********




#Plot Color Deviation
r_colordeviation = r_colordeviation_A
#r_colordeviation = r_colordeviation_B
fig1 = plt.figure()
plt.pcolor(POL_XX, POL_YY, r_colordeviation)
plt.xlabel('Left-Right Angle [deg]')
plt.ylabel('Up-Down Angle [deg]')
plt.colorbar()
plt.clim(0,0.4)
plt.title("Deviation of CIE1931(x,y) ColorBalance v. ViewAngle")
outfilename = file_path_X.split("/")[-1][:-4] + "_ColorDeviation_New1.png"
plt.savefig(wkspFldr + "/" + outfilename)

#Save Text
outfilename = file_path_X.split("/")[-1][:-4] + "_ColorDeviation_New1.txt"
np.savetxt(wkspFldr+"/"+outfilename, r_colordeviation)