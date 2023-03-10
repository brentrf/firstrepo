#Functions in this File
# 1. Convert_OptPower_v_SPHERICALAngles_to_XYAngles_FullHemisphere
# 2. read_zemax_DDR
#  2b. get_integer()
#  2c. get_float()

import numpy as np
import scipy as sp
import struct
from scipy.interpolate import griddata



#from: https://stackoverflow.com/questions/43086557/convolve2d-just-by-using-numpy
def np_conv2d(a, f):
    s = f.shape + tuple(np.subtract(a.shape, f.shape) + 1)
    strd = np.lib.stride_tricks.as_strided
    subM = strd(a, shape = s, strides = a.strides * 2)
    return np.einsum('ij,ijkl->kl', f, subM)
def sp_conv2d(a, sigma_y,sigma_x):
    sigma = [sigma_y, sigma_x]
    y = sp.ndimage.filters.gaussian_filter(a, sigma, mode='constant')
    return y

def sp_conv2d_byfft(a,f):
    in1 = a
    ntopbot = ( a.shape[0]-f.shape[0] ) / 2
    if ntopbot == np.floor(ntopbot):
        ntop = int(ntopbot)
        nbot = int(ntopbot)
    else:
        ntop = int(np.ceil(ntopbot))
        nbot = int(np.floor(ntopbot))
    nleftright = ( a.shape[1]-f.shape[1] ) / 2
    if nleftright == np.floor(nleftright):
        nleft  = int(nleftright)
        nright = int(nleftright)
    else:
        nleft  = int(np.ceil(nleftright))
        nright = int(np.floor(nleftright))
    in2 = np.pad(f, ((ntop,nbot),(nleft, nright)), 'constant', constant_values=((0,0),(0,0)) )
    aconv = sp.signal.fftconvolve(in1, in2, mode='same', axes=None)
    #aconv_full = sp.signal.fftconvolve(in1, in2, mode='full', axes=None)
    #aconv_valid = sp.signal.fftconvolve(in1, in2, mode='valid', axes=None)
    return aconv


def np_conv2d_byfft(a,f):   #NOT WORKING YET
    ntopbot = ( a.shape[0]-f.shape[0] ) / 2
    if ntopbot == np.floor(ntopbot):
        ntop = int(ntopbot)
        nbot = int(ntopbot)
    else:
        ntop = int(np.ceil(ntopbot))
        nbot = int(np.floor(ntopbot))
    nleftright = ( a.shape[1]-f.shape[1] ) / 2
    if nleftright == np.floor(nleftright):
        nleft  = int(nleftright)
        nright = int(nleftright)
    else:
        nleft  = int(np.ceil(nleftright))
        nright = int(np.floor(nleftright))
    fp = np.pad(f, ((ntop,nbot),(nleft, nright)), 'constant', constant_values=((0,0),(0,0)) )

    fft_a = np.fft.fft2(a)
    s = a.shape
    fft_fp = np.fft.fft2(f,s)
    fft_aconv = fft_a*fft_fp
    aconv = np.fft.ifft2(fft_aconv)
    return aconv



def Convert_OptPower_v_SPHERICALAngles_to_XYAngles_FullHemisphere(Power_v_thetaAz,flag_sincorr=1):
    # This function receives a 2D array of values that represent optical power
    # at different points on a hemisphere (theta=0..90,  azim=0...360)
    # The POWER values are converted to Radiant intensity by dividing by solid angle ~ sin(theta)
    # and then resampled and returned as 2D array v. XY-angles
    #
    # flag_sincorr = a flag that is either 1 or 0 depending on whether the sine correction  should be applied

    Npts_azim = np.size(Power_v_thetaAz, 0)
    azphis = np.linspace(0, 360, Npts_azim)
    Npts_theta = np.size(Power_v_thetaAz, 1)
    thetas = np.linspace(0, 90, Npts_theta)
    thetas[0] = 1

    #sine() correction
    if flag_sincorr==1:
        RadIntens_v_thetaAz = Power_v_thetaAz / np.sin(np.deg2rad(thetas))
        RadIntens_v_thetaAz = np.divide(Power_v_thetaAz, np.sin(np.deg2rad(thetas)))  # should be the same
    else:
        RadIntens_v_thetaAz = Power_v_thetaAz

    #apply smoothing if desired
    smooth_width_AZ_deg = 0
    smooth_width_THETA_deg = 0
    if (smooth_width_AZ_deg>1)&(smooth_width_THETA_deg>1):
        kernel_size_AZ = int(np.round((Npts_azim/360)*smooth_width_AZ_deg,0))
        kernel_size_THETA = int(np.round((Npts_theta/90)*smooth_width_THETA_deg,0))
        sigma_y = kernel_size_THETA
        sigma_x = kernel_size_AZ
        tmp = sp_conv2d(RadIntens_v_thetaAz, sigma_y, sigma_x)
        print(np.size(RadIntens_v_thetaAz))
        print(np.size(tmp))

        kernel = np.ones([kernel_size_AZ,kernel_size_THETA]) / (kernel_size_AZ*kernel_size_THETA)
        print(kernel_size_AZ)
        print(kernel_size_THETA)
        print(kernel)
        print(np.size(RadIntens_v_thetaAz))
        tmp2 = np_conv2d(RadIntens_v_thetaAz, kernel)
        RadIntens_v_thetaAz = tmp2
        print(np.size(RadIntens_v_thetaAz))

        RadIntens_v_thetaAz = tmp

    # generate vector of Radiant Intensity Values at each VIEW ANGLE XY
    a = RadIntens_v_thetaAz
    pvals, px, py = [], [], []
    for kt in range(0, np.size(thetas)):
        for kp in range(0, np.size(azphis)):
            pvals.append(a[kp][kt])
            R = thetas[kt]
            px.append(R * np.cos(np.deg2rad(azphis[kp])))
            py.append(R * np.sin(np.deg2rad(azphis[kp])))
    # fig0, ax = plt.subplots(nrows=1, ncols=1)
    # ax.scatter(px, py, c='k', alpha=0.2, marker='.')

    # generate value-matrix of colors using GRIDDATA to  INTERPOLATE
    POL_x = np.linspace(-90, 90, 181)
    POL_y = np.linspace(-90, 90, 181)
    POL_XX, POL_YY = np.meshgrid(POL_x, POL_y)
    RadIntens_v_ViewAngleXY = griddata((px, py), pvals, (POL_XX, POL_YY), method='nearest')
    # method = 'nearest'  method = 'linear' method = 'cubic'

    return (RadIntens_v_ViewAngleXY,POL_XX,POL_YY,RadIntens_v_thetaAz,thetas,azphis)


def get_integer(file):
    return struct.unpack('I', file.read(4))[0]
def get_float(file):
    return struct.unpack('d', file.read(8))[0]
    #these are used by read_zemax_DDR (below)

def read_zemax_DDR(filename="/Users/brentfisher/Documents/Zemax/MODELS_XDC/LTM/detectdata_8_det1.DDR"):
    # This function receives a filename path that points to a
    # file that is assumed to be a ZEMAX DDR detector file (binary)
    # The file is then opened according to file format specifications in zemax documentation
    #
    # The contents are then returned as a dictionary called  "ddrdat"


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
        #this^^ line appeared in original code that I got, but leaving it in results in wacky data (e.g. 1e+163)...
        #probably because it shifts all the bits by 4 resulting in incorrect data

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
    data_to_export = []
    match type_det:
        case 1:
            data_to_export.append(inc_int_pos)
            data_to_export.append(inc_int_ang)
            data_to_export.append(coh_real)
            data_to_export.append(coh_imag)
        case 3:
            data_to_export.append(ang_P)
            data_to_export.append(ang_Xtri)
            data_to_export.append(ang_Ytri)
            data_to_export.append(ang_Ztri)

    tmp3D = np.zeros([i_data[1],i_data[0],4])
    for ii in range(0,4):
        for count,value in enumerate(data_to_export[ii]):
            kc = np.mod(count,i_data[0])
            kr = int((count - kc+1)/i_data[1])
            tmp3D[kr,kc,ii]=value
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
    ddrdat['3DData'] = tmp3D

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
