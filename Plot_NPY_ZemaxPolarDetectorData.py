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


# # function:  convert to DetectorMatrixData = f(theta,azim) to f(ViewingAngle_XY)
# def Convert_OptPower_v_SPHERICALAngles_to_XYAngles_FullHemisphere(Power_v_thetaAz):
#     Npts_azim = np.size(Power_v_thetaAz, 0)
#     azphis = np.linspace(0, 360, Npts_azim)
#     Npts_theta = np.size(Power_v_thetaAz, 1)
#     thetas = np.linspace(0, 90, Npts_theta)
#     thetas[0] = 1
#
#     RadIntens_v_thetaAz = Power_v_thetaAz / np.sin(np.deg2rad(thetas))
#     RadIntens_v_thetaAz = np.divide(Power_v_thetaAz, np.sin(np.deg2rad(thetas)))  # should be the same
#
#     # generate vector of Radiant Intensity Values at each VIEW ANGLE XY
#     a = RadIntens_v_thetaAz
#     pvals, px, py = [], [], []
#     for kt in range(0, np.size(thetas)):
#         for kp in range(0, np.size(azphis)):
#             pvals.append(a[kp][kt])
#             R = thetas[kt]
#             px.append(R * np.cos(np.deg2rad(azphis[kp])))
#             py.append(R * np.sin(np.deg2rad(azphis[kp])))
#     # fig0, ax = plt.subplots(nrows=1, ncols=1)
#     # ax.scatter(px, py, c='k', alpha=0.2, marker='.')
#
#     # generate value-matrix of colors using GRIDDATA to  INTERPOLATE
#     POL_x = np.linspace(-90, 90, 181)
#     POL_y = np.linspace(-90, 90, 181)
#     POL_XX, POL_YY = np.meshgrid(POL_x, POL_y)
#     RadIntens_v_ViewAngleXY = griddata((px, py), pvals, (POL_XX, POL_YY), method='nearest')
#     return (RadIntens_v_ViewAngleXY,POL_XX,POL_YY,RadIntens_v_thetaAz,thetas,azphis)

####################   MAIN   #############################
#User: SELECT NPY files
root = tk.Tk()
root.withdraw()
print("SELECT NPY FILES CONTAINING *POLAR* DETECTOR DATA")
file_paths = filedialog.askopenfilenames(filetypes=[("Zemax Detector Data Files","*.NPY")])


for count,filename in enumerate(file_paths):
    #filename = file_paths[0]
    wkspFldr = os.path.dirname(filename)  #return folder path where data gotten from
    Power_v_thetaAz = np.load(filename)

    (RadIntens_v_ViewAngleXY,POL_XX,POL_YY,RadIntens_v_thetaAz,thetas,azphis)\
        = zf.Convert_OptPower_v_SPHERICALAngles_to_XYAngles_FullHemisphere(Power_v_thetaAz)

    # Npts_azim = np.size(Power_v_thetaAz,0)
    # azphis = np.linspace(0,360,Npts_azim)
    # Npts_theta = np.size(Power_v_thetaAz,1)
    # thetas = np.linspace(0,90,Npts_theta)
    # thetas[0] = 1
    #
    # RadIntens_v_thetaAz = Power_v_thetaAz/np.sin(np.deg2rad(thetas))
    # RadIntens_v_thetaAz = np.divide(Power_v_thetaAz, np.sin(np.deg2rad(thetas)))  #should be the same
    #
    # #generate vector of Radiant Intensity Values at each VIEW ANGLE XY
    # a = RadIntens_v_thetaAz
    # pvals,px,py = [],[],[]
    # for kt in range(0,np.size(thetas)):
    #     for kp in range(0,np.size(azphis)):
    #         pvals.append(a[kp][kt])
    #         R = thetas[kt]
    #         px.append( R*np.cos(np.deg2rad(azphis[kp])) )
    #         py.append( R*np.sin(np.deg2rad(azphis[kp])) )
    # #fig0, ax = plt.subplots(nrows=1, ncols=1)
    # #ax.scatter(px, py, c='k', alpha=0.2, marker='.')
    #
    # # generate value-matrix of colors using GRIDDATA to  INTERPOLATE
    # POL_x = np.linspace(-90,90,181)
    # POL_y =  np.linspace(-90,90,181)
    # POL_XX, POL_YY = np.meshgrid(POL_x,POL_y)
    # RadIntens_v_ViewAngleXY = griddata((px, py), pvals, (POL_XX, POL_YY), method='nearest')


    # PLOT 1: Power v. Theta,Azim (Square Matrix Input)
    #fig0, ax = plt.subplots(nrows=1, ncols=1)
    fig0 = plt.figure()
    plt.pcolor(thetas, azphis, Power_v_thetaAz)
    plt.xlabel('Polar(Zenith) Angle [deg]')
    plt.ylabel('Azimuth Angle [deg]')
    plt.colorbar()
    plt.title(filename.split("/")[-1]+'\n'+'Input Data:  Rel. Power [W] v theta,azim')

    # PLOT 2: Power v. Theta,Azim (Square Matrix Input)
    #fig1, ax = plt.subplots(nrows=1, ncols=1)
    fig1 = plt.figure()
    plt.pcolor(thetas, azphis, RadIntens_v_thetaAz)
    plt.xlabel('Polar(Zenith) Angle [deg]')
    plt.ylabel('Azimuth Angle [deg]')
    plt.colorbar()
    plt.title(filename.split("/")[-1]+'\n'+'Radiant Intensity [W/sr] v theta,azim')


    # PLOT 3: Radiant Intensity v. View Angle
    #fig2, ax = plt.subplots(nrows=1, ncols=1)
    fig1 = plt.figure()
    plt.pcolor(POL_XX,POL_YY,(RadIntens_v_ViewAngleXY))
    plt.xlabel('Left-Right Angle [deg]')
    plt.ylabel('Up-Down Angle [deg]')
    plt.colorbar()
    plt.title(filename.split("/")[-1]+'\n'+'Rel. Radiant Intensity [W/sr] v. Viewing Angle')
    outfilename = filename.split("/")[-1][:-4]+".png"
    plt.savefig(wkspFldr+"/"+outfilename)
    print("Done with: "+filename.split("/")[-1])


print("... Finished with "+str(count+1)+" files processed...")