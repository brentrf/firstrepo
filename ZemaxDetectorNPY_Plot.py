import tkinter as tk
from tkinter import filedialog
import numpy as np
import struct
import matplotlib.pyplot as plt
from scipy.interpolate import griddata


#get files
root = tk.Tk()
root.withdraw()
file_paths = filedialog.askopenfilenames(filetypes=[("Zemax Detector Data Files","*.NPY")])


#for count,filename in enumerate(file_paths):
filename = file_paths[0]
a = np.load(filename)

thetas = np.linspace(0,90,91)
azphis = np.linspace(0,360,92)



#plt.pcolor(thetas, azphis, a)

pvals,px,py = [],[],[]
for kt in range(0,np.size(thetas)):
    for kp in range(0,np.size(azphis)):
        pvals.append(a[kp][kt])
        R = thetas[kt]
        px.append( R*np.cos(np.deg2rad(azphis[kp])) )
        py.append( R*np.sin(np.deg2rad(azphis[kp])) )

fig, ax = plt.subplots(nrows=1, ncols=1)
ax.scatter(px, py, c='k', alpha=0.2, marker='.')


POL_x = np.linspace(-90,90,181)
POL_y =  np.linspace(-90,90,181)
POL_XX, POL_YY = np.meshgrid(POL_x,POL_y)
Ti = griddata((px, py), pvals, (POL_XX, POL_YY), method='nearest')