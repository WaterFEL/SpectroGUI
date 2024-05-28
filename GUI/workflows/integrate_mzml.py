import os, re, traceback
import numpy as np
import pyteomics.mzml as mzml
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication

#Function to integrate mass spectra within specified bounds using NumPy
def integrate_spectra(directory, mzml_file, target_mz, search_window, parent_mz, background = 0.0, plot=False, height=2000, threshold=2000, prominence=100.0, width=10):
    '''
    Integrates the mass spectra from mzml files around peaks detected near a specified m/z using a common interpolated grid and SciPy's peak detection.
    Optional plotting to visualize peak detection and integration.
    
    Parameters:
        directory: Directory containing mzml files.
        mzml_file: Name of mzml file.
        target_mz: List of target m/z values to find and integrate the peaks.
        search_window: Window size around the target m/z to limit the search for the peak.
        parent_mz: m/z of the parent ion used to set the upper limit of the m/z range for the common grid.
        background: The amount of background fragmentation that you wish to be subtracted from the integration.
        plot: If True, plots the spectrum with peak detection and integration area highlighted.
        height, threshold, prominence, width: scipy peakfind parameters with defaults of 2000, 2000, 100, and 10, respectively.
    '''

    #Initialize variables
    integrations = []
    peaks_found = []
    min_mz = 0.
    max_mz = parent_mz + 50.  #adding 50 mass units to the parent ion
    
    #some counters to control print statements
    i = j = k = l = m = 0

    #define common mz grid for interpolation
    common_mz_grid = np.round(np.linspace(min_mz, max_mz, int((max_mz - min_mz) / 0.01 + 1)),2) #0.01 Da incremenets for mz grid

    with mzml.read(os.path.join(directory, mzml_file)) as spectra:  
        
        wavelength = float(re.findall(r'\d+',mzml_file.split('Laser')[-1])[-1]) #needed for print statements
        spec_counter = 0

        for spectrum in spectra:

            #according to stack exchange, these are pre-defined lists from pyteomics              
            try:
                mz = spectrum['m/z array']
                intensity = spectrum['intensity array']
                
            except Exception as e:
                print(f'Error encounter when extract m/z and intensity arrays from spectrum number {spec_counter+1} in {mzml_file}: {e}.\nTraceback: {traceback.format_exc()}')
                QApplication.processEvents()
                return False
            
            #Check for inconsistent data
            if len(mz) != len(intensity):
                print(f'Inconsistent lengths of m/z and intensity arrays in {os.path.basename(mzml_file)}. Analysis will be stopped.')
                QApplication.processEvents()     
                return False

            #Interpolate intensity onto the common m/z grid, adding zeros for any extrapolation
            interp_intensity = np.interp(common_mz_grid, mz, intensity, left = 0, right = 0)

            #scipy peak finder
            peaks, properties = find_peaks(interp_intensity, height=2000, threshold=2000, distance=None, prominence=100.0, width=10)
            peak_mz = common_mz_grid[peaks]

            #Filter peaks within the specified search window around the target m/z
            valid_peaks = [(index, peak_mz[index]) for index, peak in enumerate(peak_mz) if (target_mz - search_window) <= peak <= (target_mz + search_window)]

            if valid_peaks:
                if len(valid_peaks) > 1:
                    #Find the peak with the highest intensity among valid peaks
                    highest_intensity_peak = max(valid_peaks, key=lambda x: interp_intensity[peaks[x[0]]])
                    valid_peaks = [highest_intensity_peak]  #Update valid_peaks to only include the closest peak
                    
                    #only print once per fragment/mzml file combo
                    if i == 0:
                        #print(f'Multiple valid peaks found for {target_mz} in the UVPD spectrum at {wavelength}nm. Selecting peak at m/z = {highest_intensity_peak[1]}, which has the highest intensity.')
                        i +=1
                
                else:
                    if j == 0:
                        #print(f"Peak found at m/z = {valid_peaks[0][1]} for target m/z = {target_mz}")
                        j+=1

                idx, _ = valid_peaks[0]  #'idx' is the index within 'peaks', so it's valid for accessing 'properties'

                if 'left_bases' in properties and 'right_bases' in properties:
                    left_base = properties['left_bases'][idx]
                    right_base = properties['right_bases'][idx]
                    
                    #Integrate the peak using the trapezoidal rule
                    peak_mz_range = common_mz_grid[left_base:right_base + 1]
                    peak_intensity_range = interp_intensity[left_base:right_base + 1]
                    integration = np.trapz(peak_intensity_range, x=peak_mz_range) - background
                    if integration < 0:
                        if k == 0:
                            #print(f'Negative integration (value: {np.round(integration, 4)}) encountered for {target_mz} in the UVPD spectrum of {wavelength}nm.\nCheck your background data. Integratiions will continue for the mz, assigning values of zero for any negatives encountered.')
                            k += 1
                        integration = 0.0 #if total integration is not discernable from background and yields a negative number, assign an integration of zero.
                        
                    integrations.append(integration)

                    if plot and l == 0:
                        #Plotting the integration and peak detection only for 1 scan
                        plt.figure(figsize=(10, 5))
                        plt.plot(common_mz_grid, interp_intensity, label='Interpolated Intensity')
                        plt.plot(peak_mz_range, peak_intensity_range, 'r-', label='Integration Range')
                        plt.scatter(common_mz_grid[peaks], interp_intensity[peaks], color='orange', s=50, zorder=3, label='Detected Peaks')
                        plt.fill_between(peak_mz_range, peak_intensity_range, color='red', alpha=0.3)
                        plt.title(f'Peak Integration for Target m/z {target_mz} at {wavelength}nm')
                        plt.xlabel('m/z')
                        plt.ylabel('Intensity')
                        plt.legend()
                        #plt.show()

                        #Set x-axis limits to only show +/- 2.0 from target_mz
                        xlim_left = target_mz - 2.0
                        xlim_right = target_mz + 2.0
                        plt.xlim(xlim_left, xlim_right)
                        
                        #determine the maximum intensity within the x-axis range
                        xlims = (common_mz_grid >= xlim_left) & (common_mz_grid <= xlim_right)
                        max_intensity = np.max(interp_intensity[xlims])
                        plt.ylim(0, max_intensity)  #set y-axis to go from 0 to the max intensity found

                        #save plot to external file
                        plt.savefig(os.path.join(directory, 'integration_plots', f'mz{np.round(target_mz, 0)}_{wavelength}nm.png'))
                        plt.close()
                        l += 1

            #if no peak is found, append an integration of zero to the integration list.
            else:
                if m == 0:
                    #print(f'No valid peak found within {search_window} Da of target m/z = {target_mz} in the UVPD spectrum at {wavelength}nm.')
                    m += 1
                integrations.append(0.0)

            spec_counter += 1

    avg_integration = np.mean(integrations) if integrations else 0
    std_dev = np.std(integrations) if integrations else 0

    return [avg_integration, std_dev] 
