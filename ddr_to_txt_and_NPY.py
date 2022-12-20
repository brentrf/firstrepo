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
    tmp3D = ddrdat['3DData']

    #output to text file ...
    lenfile = len(name)
    match ddrdat['type_det']:
        case 1:
            output_filename0 = name[0:len(name) - 4] + "_int_pos.txt"
            output_filename1 = name[0:len(name) - 4] + "_int_ang.txt"
            output_filename2 = name[0:len(name) - 4] + "_coh_real.txt"
            output_filename3 = name[0:len(name) - 4] + "_coh_imag.txt"
        case 3:
            output_filename0 = name[0:len(name) - 4] + "_ang_P.txt"
            output_filename1 = name[0:len(name) - 4] + "_ang_Xtri.txt"
            output_filename2 = name[0:len(name) - 4] + "_ang_Ytri.txt"
            output_filename3 = name[0:len(name) - 4] + "_ang_Ztri.txt"
    np.savetxt(output_filename0,tmp3D[:,:,0])
    np.savetxt(output_filename1,tmp3D[:,:,1])
    np.savetxt(output_filename2,tmp3D[:,:,2])
    np.savetxt(output_filename3,tmp3D[:,:,3])
    print(name," has been converted to TXT...")

    #output to NPY
    output_filename = name[0:len(name)-4]+"_tmp3D.npy"
    np.save(output_filename,tmp3D)
    print(name," has been converted to NPY...")



