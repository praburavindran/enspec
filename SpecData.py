# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 17:38:35 2015

@author: pravindran
"""

from __future__ import print_function
import numpy as np
import os.path
import struct

class SpecData:
    
    def __init__(self, filename = None):
        self._wavelengths = None
        self._reference = None
        self._measured = None


    def _locate_kwd(self, lines, kwd):
        """
        Find the line on which the keyword, @kwd, occurs.
        This is used to find the file line on which
        a data table starts.
    
        input:
        lines: the data file lines
        kwd: the keyword to locate
        return:
        kwdline: the line number on which data starts.
        """
        kwdline = 0
        for l in lines:
            kwdline = kwdline + 1
            if kwd in l:
                break
        return kwdline
        
        
    def _extract_wvl_ref_rad(self, lines, startline, wvli, refi, radi):
        """
        Reads the @lines from @startline and extracts
        the columns @wvli, @refi and @radi. Puts these
        numbers in numpy array member attricbutes.
        
        input: 
        lines: the data file lines
        startline: the line number for data table start
        wvli: column index which contains the wavelength
        refi: column index which contains the reference
        radi: column index which contains the measured
        effect:
        sets up some local members as numpy arrays
        """
        #read the wavelength, reference and radiance into lists
        wavelengths = []
        reference = []
        measured = []
        for l in lines[startline:]:
            tkns = l.strip().split()
            wavelengths.append(float(tkns[wvli]))
            reference.append(float(tkns[refi]))
            measured.append(float(tkns[radi]))
        #store as numpy arrays
        if wavelengths and reference and measured:
            self._wavelengths = np.array(wavelengths)
            self._reference = np.array(reference)
            self._measured = np.array(measured)

        
    def load_from_sig(self, filename):
        """
        Reads spectral data from a .sig file

        inputs:
        filename: name of file to read from
        """
        #read the lines from the file
        lines = []
        with open(filename) as f:
            lines = f.readlines()
        self._extract_wvl_ref_rad(lines, 
                                  self._locate_kwd(lines, "data="), 
                                  0, 1, 2)
    
    def load_from_sed(self, filename):
        """
        Reads spectral data from a .sed file

        inputs:
        filename: name of file to read from
        """        
        #read the lines from the file
        lines = []
        with open(filename) as f:
            lines = f.readlines()
        #extract data from the lines and put into numpy array
        self._extract_wvl_ref_rad(lines, 
                                  self._locate_kwd(lines, "Chan.#"), 
                                  1, 2, 3)

    
                
    def load_from_asd(self, filename):
        """
        Reads spectral data from a .sed file

        inputs:
        filename: name of file to read from
        """
        #read the contents of the binary file
        binconts = None
        with open(filename, 'rb') as f:
            binconts = f.read()
        #read wavelength data and number of channels from header
        (wavestart, wavestep) = struct.unpack("ff", binconts[191:191+8])
        numchannels = struct.unpack("i", binconts[204:204+4])[0]
        waveend = wavestart + numchannels*wavestep - 1
        #read the measured and reference
        fmt = "d"*numchannels
        size = numchannels*8
        measured = list(struct.unpack(fmt, binconts[484:(484 + size)]))
        reference = list(struct.unpack(fmt, binconts[17712:(17712 + size)]))
        #put data in numpy array
        if measured and reference:
            self._wavelengths = np.linspace(wavestart, waveend, numchannels)
            self._measured = np.array(measured)
            self._reference = np.array(reference)
    
    
    
    def print(self, numlines):
        print(self._wavelengths[0:numlines])
        print(self._reference[0:numlines])
        print(self._measured[0:numlines])
        
        
        
if __name__ == "__main__":
    
    datadir = "/home/pravindran/data/enspec/from_clayton"
    
    #loading a sample .sig file
    sigf = os.path.join(datadir, 
                        "sig", 
                        "20141217_dut11_c_165_svc02040_213_001.sig")
    ssig = SpecData()
    ssig.load_from_sig(sigf)
    print("Head for data read from .sig file")
    ssig.print(10)
    
    #loading a sample .sed file
    sedf = os.path.join(datadir, 
                        "sed", 
                        "20141217_DWI3_C_110_SE_LC_2S_00005.sed")
    ssed = SpecData()
    ssed.load_from_sed(sedf)
    print("Head for data read from .sed file")
    ssed.print(10)
    
    #loading a sample .asd file
    asdf = os.path.join(datadir,
                        "asd",
                        "20141217_DWI3_C_110_ASD00001.asd")
    sasd = SpecData()
    sasd.load_from_asd(asdf)
    print("Head for data read from .asd file")
    sasd.print(20)
    
    
    
    