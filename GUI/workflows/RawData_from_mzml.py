import os, re, traceback
import numpy as np
import pyteomics.mzml as mzml
import pandas as pd
from PyQt6.QtWidgets import QApplication

def extract_RawData(mzml_directory, parent_mz, output_csv_file):
    '''Extracts the mass spectra from mzml files and averages them across all scans. Interpolation on a common mz grid for all mzml files provided is used. Usage is:
    directory containing mzml files, m/z of the parent ion (needed for interpolation), and the name of .csv file to output results to.
    '''
   
    #Set up interpolation grid - different from before because we don't want to print the mass spectrum in 0.01 Da increments. 
    min_mz = 0.
    max_mz = parent_mz + 50.  #adding 50 mass units to the parent ion

    #Get a list of mzML files in the given directory
    mzml_files = [f for f in os.listdir(mzml_directory) if f.lower().endswith('.mzml')]

    #dict to store data
    raw_data = {}
    
    #define common mz grid for interpolation and add to dict
    common_mz_grid = np.round(np.linspace(min_mz, max_mz, int((max_mz - min_mz) / 0.05 + 1)),2) #0.05 Da incremenets for mz grid
    raw_data['m/z'] = common_mz_grid

    for mzml_file in mzml_files:
        
        #get wavelength from mzml file name
        try:
            wavelength = re.findall(r'\d+', mzml_file.split('Laser')[-1])[-1]
            wl_title = f'{wavelength}nm' #title to be written to raw data file

        except ValueError as ve:
            print(f'Could not extract the wavelength from the .mzml file name. This is what the code has found: {wavelength}.\nDoes the filename contain the text: "Laser"?\nAnalysis will be stopped.')
            QApplication.processEvents()
            return

        #Initialize dictionary w/ zeroes for each scan
        average_intensity = np.zeros_like(common_mz_grid)
        scan_counter = 0

        with mzml.read(os.path.join(mzml_directory, mzml_file)) as spectra:  
            
            for spectrum in spectra:

                #according to stack exchange, these are pre-defined lists from pyteomics              
                try:
                    mz = spectrum['m/z array']
                    intensity = spectrum['intensity array']
                    
                except Exception as e:
                    print(f'Error encounter when extract m/z and intensity arrays from spectrum number {i+1} in {mzml_file}: {e}.\nTraceback: {traceback.format_exc()}\n')
                    QApplication.processEvents()
                    return
                
                #Check for inconsistent data
                if len(mz) != len(intensity):
                    print(f'Inconsistent lengths of m/z and intensity arrays in {os.path.basename(mzml_file)}. Analysis will be stopped.')
                    QApplication.processEvents()     
                    return

                #Interpolate intensity onto the common m/z grid and append to list
                interp_intensity = np.interp(common_mz_grid, mz, intensity, left = 0, right = 0)
            
                average_intensity += interp_intensity
                scan_counter += 1

        if scan_counter > 0:
            average_intensity /= scan_counter

        else:
            print(f'No mass spectra were found in {mzml_file}! Aborting raw data processing.')
            QApplication.processEvents()  
            return
        
        #append averaged mass spectra for each wavelength to the dictionary
        raw_data[wl_title] = average_intensity

    try: 
        df = pd.DataFrame(raw_data)
        df.to_csv(output_csv_file, index=False)
        print(f'Data succesfully written to {output_csv_file}\n\n')
        QApplication.processEvents()  
        return
    
    except PermissionError:
        'Close the .csv file with the same name as the one where the raw data is being written and then rerun the code.'
        QApplication.processEvents()  
        return       

def PE_calc(W_nm, P, dP, Par, dPar, Frag, dFrag):
    '''Calculates photofragmentation efficiency with normlaization to laser power. Useage is:
    Wavelength, Power, Power stdev, base peak integration, base peak integration stdev, fragment peak integration, fragment peak integration stdev
    '''

    #Check for division by zero
    if P == 0 or Par == 0:
        print(f'WARNING!!!!!\nDivision by zero error for wavelenth {W}nm. Power (P) is {P}, Parent integration is {Par} and Fragment integration is {Frag}.\n The sum of base peak integration (Par) and fragment peak integration (Frag) must be non-zero.\nWriting zeros for PE and PE_stdev')
        QApplication.processEvents()   
        return [0, 0]   
   
    #convert wavelength (nm) to eV because we want lower numbers as we increase nm, not the other way around
    def nm_to_eV(wavelength):
        
        h = 6.62607015E-34 #J*s
        c = 299792458 #m/s
        E = 1.60217663E-19
        
        W_eV = ((h * c) / (wavelength * 1.E-9)) / E #wavelength(nm) to eV
        return W_eV

    #incident wavelength to eV
    W = nm_to_eV(W_nm)

    #Note that the bandwidth of the OPO is about +/- 2nm, which is essentially the FWHM of the energy distribution (which should be Gaussian). So we need to convert this to a sigma to get the stdev
    # FWHM = 2*sqrt(2*ln(2))*sigma, where FWHM = 4 (+/-2)
    
    def fwhm_to_sigma(fwhm):
        sigma = fwhm / (2 * np.sqrt(2 * np.log(2)))
        return sigma
    
    #stdev of incident wavelength
    #bandwidth of OPO - assuming that it is +/- 2 nm
    W_high = nm_to_eV(W_nm + 2.) 
    W_low = nm_to_eV(W_nm - 2.) 
   
    dW = fwhm_to_sigma(np.abs(W_low - W_high)) #stdev

    #calculate photofragmentation efficiency
    PE = -(W / P) * np.log(Par / (Frag + Par))

    #calculate standard deviatian in photofragmentation efficiency
    try:
        term1 = np.square((np.log(Par / (Par + Frag)) / -P) * dW)
        term2 = np.square(((W * np.log(Par / (Par + Frag))) / np.square(P)) * dP)
        term3 = np.square(-1 * ((1 / (Par + Frag) / P / Par * W * Frag)) * dPar)
        term4 = np.square((W * 1 / (Par + Frag) / P) * dFrag)

        PE_stdev = np.sqrt(term1+term2+term3+term4)

        return [PE, PE_stdev]    
    
    except Exception as e:
        print(f'Error encountered during calculation of photogfragmentaion efficiency at wavelength {W}nm: {e}.\nWriting zeros for PE and PE_stdev')
        QApplication.processEvents()      
        return [0, 0] 

def PE_calc_noNorm(W, P, dP, Par, dPar, Frag, dFrag): 
    '''Calculates photofragmentation efficiency without normlaization to laser power. Useage is:
    Wavelength, Power, Power stdev, base peak integration, base peak integration stdev, fragment peak integration, fragment peak integration stdev
    Note that W, P, and dP are dummy variables - kept it like this for functionality within main function.
    '''
    
    #Check for division by zero
    if Par == 0:
        print(f'WARNING!!!!!\nDivision by zero error for wavelenth {W}nm. Power (P) is {P}, Parent integration is {Par} and Fragment integration is {Frag}.\n The sum of base peak integration (Par) and fragment peak integration (Frag) must be non-zero.\nWriting zeros for PE and PE_stdev')
        QApplication.processEvents()   
        return [0, 0]   

    #calculate photofragmentation efficiency
    efficiency = -1 * np.log(Par / (Frag + Par))

    #calculate standard deviatian in photofragmentation efficiency
    try:
        term1 = np.square(-1 * (Frag / (Par + Frag) / Par) * dPar)
        term2 = np.square((1 / (Par + Frag)) * dFrag)

        PE_stdev = np.sqrt(term1+term2)
        
        return [efficiency, PE_stdev]

    except Exception as e:
        print(f'Error encountered during calculation of photogfragmentaion efficiency at wavelength {W}nm: {e}.\nWriting zeros for PE and PE_stdev')
        QApplication.processEvents()      
        return [0, 0] 
