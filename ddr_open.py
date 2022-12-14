# imports
# matplotlib

import tkinter as tk
from tkinter import filedialog
import numpy as np
import struct
import matplotlib.pyplot as plt

def get_integer(file):
    return struct.unpack('I', file.read(4))[0]


def get_float(file):
    return struct.unpack('d', file.read(8))[0]


def convert_DDR_to_TXT(filename="/Users/brentfisher/Documents/Zemax/MODELS_XDC/LTM/detectdata_8_det1.DDR"):
    #dirpath = "/Users/brentfisher/Documents/Zemax/MODELS_XDC/LTM/"
    #filename = dirpath + "detectdata_8_det1.DDR"

    with open(filename, "rb") as file:  #open the file.... (within this indentation)
        # unpack little endian integers

        #header data....
        version = get_integer(file)
        type_det = get_integer(file)
        lens_units = get_integer(file)
        source_units = get_integer(file)
        source_multiplier = get_integer(file)
        #print(f'{version=}')
        #print(f'{type_det=}')

        match type_det:
            case 1:
                fmt_d_data = 'ddddd'  # 5 values (doubles) per pixel
                inc_int_pos, inc_int_ang, coh_real, coh_imag, coh_amp = [], [], [], [], []
            case 3:
                fmt_d_data = 'dddddddd'  # 8 values (doubles) per pixel
                ang_P, ang_Xtri, ang_Ytri, ang_Ztri = [], [], [], []

        struct_len = struct.calcsize(fmt_d_data)
        struct_unpack = struct.Struct(fmt_d_data).unpack_from

        # more header data (ints)....
        i_data_len = 50
        i_data = []
        for _ in range(i_data_len):
            i_data.append(get_integer(file))

        x_pixels = i_data[0]
        y_pixels = i_data[1]
        n_rays_spatial_detector = i_data[2]
        n_rays_angular_detector = i_data[3]
        #print(f'{x_pixels=}')
        #print(f'{y_pixels=}')
        #print(f'{n_rays_spatial_detector=}')
        #print(f'{n_rays_angular_detector=}')
        #print(f'{i_data=}')

        #  there is a gap of 4 bytes that appears between
        # the last int member (i_data) and the first double member (d_data)

        #gap = get_integer(file)   #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # more HEADER data (doubles)...........................
        d_data = []
        for _ in range(i_data_len):
            d_data.append(get_float(file))
        #print(f'{d_data=}')

        ray_trace_method = struct.unpack('I', file.read(4))[0]
        #print(f'{ray_trace_method=}')
        #print(f'{struct_len=}')


        # START READING DETECTOR DATA ...........................
        #data = file.read(struct_len)
        record_count = 0
        while True:
            data = file.read(struct_len)
            if not data: break
            if len(data)==struct_len:
                s = struct_unpack(data)
                match type_det:
                    case 1:
                        inc_int_pos.append(s[0])
                        inc_int_ang.append(s[1])
                        coh_real.append(s[2])
                        coh_imag.append(s[3])
                        coh_amp.append(s[4])
                    case 3:
                        ang_P.append(s[4])
                        ang_Xtri.append(s[5])
                        ang_Ytri.append(s[6])
                        ang_Ztri.append(s[7])
                record_count=record_count+1
    Nrecords = record_count


    #reshape data to 2D matrix
    match type_det:
        case 1:
            data_to_export = inc_int_pos
        case 3:
            data_to_export = ang_P
    tmp2D = np.zeros([i_data[1],i_data[0]])
    for count,value in enumerate(data_to_export):
        kc = np.mod(count,i_data[0])
        kr = int((count - kc+1)/i_data[1])
        tmp2D[kr][kc]=value
        #print(kc,kr) # this line for for debugging

#    #output to text file ...
#    lenfile = len(filename)
#    output_filename = filename[0:len(filename)-4]+".txt"
#    np.savetxt(output_filename,tmp2D)

    #record dictionary output
    ddrdat=dict()
    ddrdat['version'] = version
    ddrdat['type_det'] = type_det
    ddrdat['struct_len'] = struct_len
    ddrdat['x_pixels'] = x_pixels
    ddrdat['y_pixels'] = y_pixels
    ddrdat['ray_trace_method'] = ray_trace_method
    ddrdat['n_rays_spatial_detector'] = n_rays_spatial_detector
    ddrdat['n_rays_angular_detector'] = n_rays_angular_detector
    ddrdat['i_data'] = i_data
    ddrdat['d_data'] = d_data
    ddrdat['2DData'] = tmp2D

    return ddrdat


    # Pixel Ordering
    # For Detector Rectangle and Color objects,
    # pixel  # 1 is in the (-x, -y) lower left corner and the subsequent pixels move first across the columns
    # in the +x direction, then up through the rows.
    # For Detector Polar
    #objects, pixel  # 1 starts at a polar angle of zero, and subsequent pixels go along the radial arm at zero
    # degrees to the +x axis to the maximum polar angle. The next pixel starts again at polar angle of zero
    # and continues along the radial arm at the first azimuthal angle increment. The pattern repeats for
    # each angular arm along the azimuthal direction.
    #For Detector Volume
    # objects, pixel  # 1 is in the (-x, -y) lower left corner of the first plane on the -Z side of the detector, and subsequent pixels move first across the columns in the +x direction, then up through the rows to (+x, +y) of the first plane. The next pixel as at the (-x, -y) corner of the next Z plane, and the pattern continues through all the Z planes.

######### MAIN  #####

#get the files you want to convert
root = tk.Tk()
root.withdraw()
file_paths = filedialog.askopenfilenames(filetypes=[("Zemax Detector Data Files","*.DDR")])

for count,name in enumerate(file_paths):
    ddrdat = convert_DDR_to_TXT(name)
    tmp2D = ddrdat['2DData']

    #output to text file ...
    lenfile = len(name)
    output_filename = name[0:len(name)-4]+".txt"
    np.savetxt(output_filename,tmp2D)
    print(name," has been converted...")

