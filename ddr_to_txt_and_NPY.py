import tkinter as tk
from tkinter import filedialog
import numpy as np
import zmax_funs as zf
import struct

#########################  MAIN  ####################################

#get the files you want to convert
root = tk.Tk()
root.withdraw()
file_paths = filedialog.askopenfilenames(filetypes=[("Zemax Detector Data Files","*.DDR")])

for count,name in enumerate(file_paths):
    ddrdat = zf.read_zemax_DDR(name)
    tmp2D = ddrdat['2DData']

    #output to text file ...
    lenfile = len(name)
    output_filename = name[0:len(name)-4]+".txt"
    np.savetxt(output_filename,tmp2D)
    print(name," has been converted to TXT...")

    #output to NPY
    output_filename = name[0:len(name)-4]+".npy"
    np.save(output_filename,tmp2D)
    print(name," has been converted to NPY...")



