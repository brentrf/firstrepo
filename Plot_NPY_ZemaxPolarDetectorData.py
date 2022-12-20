# This code opens a batch of NPY files (specified by user)
# which are assumed to contain a 2D array of values that represent optical power
# at different points on a hemisphere (theta=0..90,  azim=0...360)
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
import zmax_funs as zf
import matplotlib.image as mpimg

####################   MAIN   #############################
#User: SELECT NPY files
root = tk.Tk()
root.withdraw()
print("SELECT NPY FILES CONTAINING *POLAR* DETECTOR DATA")
file_paths = filedialog.askopenfilenames(filetypes=[("Zemax Detector Data Files","*.NPY")])

# dattype=0
# while dattype!=1 and dattype !=2:
#     type_str = input("What kind of data are input?  [1] *Power* v Angle(theta,az)  OR  [2] *Tri-Stimulus(XYZ)* v Angle(theta,az) ?")
#     dattype = int(type_str)
#     if dattype != 1 and dattype != 2:
#         print("your answer must be '1' or '2' !!! ")

for count,filename in enumerate(file_paths):
    filename = file_paths[0]
    wkspFldr = os.path.dirname(filename)  #return folder path where data gotten from
    IN = np.load(filename)

    Power_v_thetaAz = IN[:,:,0]
    XYZtri_v_thetaAz = IN[:,:,1:]

    # Convert Power_v_ThetaAz  to Radiant_Intensity_v_XYViewing (using function in zmax_funs)
    (RadIntens_v_ViewAngleXY, POL_XX, POL_YY, RadIntens_v_thetaAz, thetas, azphis) \
        = zf.Convert_OptPower_v_SPHERICALAngles_to_XYAngles_FullHemisphere(Power_v_thetaAz, 1)

    #create output Matrix (3D)
    OUT = np.zeros([POL_XX.shape[0],POL_XX.shape[1],IN.shape[2]])
    OUT[:,:,0] = RadIntens_v_ViewAngleXY

    # loop over X,Y,Z Tristimulus *if they are present in INPUT array*
    # Convert TRISTIM_v_ThetaAz  to TRISTIM_v_XYViewing (using function in zmax_funs)
    for kk in range(0,XYZtri_v_thetaAz.shape[2]):
        flag_sine_correction = 1
        (OUT[:, :, kk+1], POL_XX, POL_YY, RadIntens_v_thetaAz, thetas, azphis) \
            = zf.Convert_OptPower_v_SPHERICALAngles_to_XYAngles_FullHemisphere(XYZtri_v_thetaAz[:,:,kk],flag_sine_correction)
        print(kk)

    # Save NPY & Text: RadIntens_v_XYangle + XYZTristimulus values
    outfilename = filename.split("/")[-1][:-4] + "_v_XYangle.npy"
    np.save(wkspFldr + "/" + outfilename, OUT)

    # Save TXT Files
    outfilename = filename.split("/")[-1][:-4] + "_RadIntens_v_XYangle.txt"
    np.savetxt(wkspFldr + "/" + outfilename, RadIntens_v_ViewAngleXY)
    for kk in range(1,IN.shape[2]):
        outfilename = filename.split("/")[-1][:-4] + "_TriStim"+str(kk)+"_v_XYangle.txt"
        np.savetxt(wkspFldr + "/" + outfilename, OUT[:,:,kk])

    # Generate Plots

    # # PLOT 1: Power v. Theta,Azim (Square Matrix Input)
    # #fig0, ax = plt.subplots(nrows=1, ncols=1)
    # fig0 = plt.figure()
    # plt.pcolor(thetas, azphis, Power_v_thetaAz)
    # plt.xlabel('Polar(Zenith) Angle [deg]')
    # plt.ylabel('Azimuth Angle [deg]')
    # plt.colorbar()
    # plt.title(filename.split("/")[-1]+'\n'+'Input Data:  Rel. Power [W] v theta,azim')

    # # PLOT 2: Power v. Theta,Azim (Square Matrix Input)
    # #fig1, ax = plt.subplots(nrows=1, ncols=1)
    # fig1 = plt.figure()
    # plt.pcolor(thetas, azphis, RadIntens_v_thetaAz)
    # plt.xlabel('Polar(Zenith) Angle [deg]')
    # plt.ylabel('Azimuth Angle [deg]')
    # plt.colorbar()
    # plt.title(filename.split("/")[-1]+'\n'+'Radiant Intensity [W/sr] v theta,azim')

    # PLOT 3: Radiant Intensity v. View Angle
    # fig2, ax = plt.subplots(nrows=1, ncols=1)
    fig1 = plt.figure()
    plt.pcolor(POL_XX, POL_YY, (RadIntens_v_ViewAngleXY))
    plt.pcolor(POL_XX, POL_YY,  OUT[:,:,0])
    plt.xlabel('Left-Right Angle [deg]')
    plt.ylabel('Up-Down Angle [deg]')
    plt.colorbar()
    plt.title(filename.split("/")[-1] + '\n' + 'Rel. Radiant Intensity [W/sr] v. Viewing Angle')
    outfilename = filename.split("/")[-1][:-4] + ".png"
    plt.savefig(wkspFldr + "/" + outfilename)

    # PLOT 4: Tristim Values v. View Angle
    XYZtri_v_ViewAngle = OUT[:, :, 1:]

    fig11 = plt.figure()
    plt.pcolor(XYZtri_v_ViewAngle[:,:,2])




    print("Done with: "+filename.split("/")[-1])



print("... Finished with "+str(count+1)+" files processed...")