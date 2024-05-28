import numpy as np
from PyQt6.QtWidgets import QApplication

def PE_calc(W_nm, P, dP, Par, dPar, Frag, dFrag):
    '''Calculates photofragmentation efficiency with normlaization to laser power. Usage is:
    -Wavelength, 
    -Power, 
    -Power stdev, 
    -base peak integration, 
    -base peak integration stdev, 
    -fragment peak integration, 
    -fragment peak integration stdev
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

    #get inverse of wavelength (because higher wavelength = lower power, so we want to divide if using eV)
    W_inv = 1 / W

    #likewise figure out how the error changes when taking the inverse
    dW_inv = (1 / np.square(W_inv)) * dW

    #calculate photofragmentation efficiency
    PE = -100.* (1/W) * (1/P) * np.log(Par / (Frag + Par)) #100 is a scaling factor so that numbers aren't super small

    #calculate standard deviatian in photofragmentation efficiency
    #from https://nicoco007.github.io/Propagation-of-Uncertainty-Calculator/ and simplified w/ Wolphram Alpha for easy of readability
    try:
        term1 = np.square((dW * np.log(Par / (Par + Frag))) / (np.square(W) * P))
        term2 = np.square((dP * np.log(Par / (Par + Frag))) / (np.square(P) * W))
        term3 = np.square(-1 * (dPar * Frag) / ((Par * P * W) * (Frag + Par))) 
        term4 = np.square(dFrag / ((W * P) * (Par + Frag)))

        PE_stdev = np.sqrt(term1+term2+term3+term4) * 100. #100 is a scaling factor so that the numbers arent super small

        return [PE, PE_stdev]    
    
    except Exception as e:
        print(f'Error encountered during calculation of photogfragmentaion efficiency at wavelength {W}nm: {e}.\nWriting zeros for PE and PE_stdev')
        QApplication.processEvents()      
        return [0, 0] 

def PE_calc_noNorm(W, P, dP, Par, dPar, Frag, dFrag): 
    '''Calculates photofragmentation efficiency without normlaization to laser power. Usege is:
    -Wavelength, 
    -Power, 
    -Power stdev, 
    -base peak integration, 
    -base peak integration stdev, 
    -fragment peak integration, 
    -fragment peak integration stdev
    
    Note that Wavelength, Power, and Power stdev are dummy variables - kept it like this for functionality within main function.
    '''
    
    #Check for division by zero
    if Par == 0:
        print(f'WARNING!!!!!\nDivision by zero error for wavelenth {W}nm. Power (P) is {P}, Parent integration is {Par} and Fragment integration is {Frag}.\n The sum of base peak integration (Par) and fragment peak integration (Frag) must be non-zero.\nWriting zeros for PE and PE_stdev')
        QApplication.processEvents()   
        return [0, 0]   

    #calculate photofragmentation efficiency
    efficiency = -1 * np.log(Par / (Frag + Par))

    #calculate standard deviatian in photofragmentation efficiency
    #from https://nicoco007.github.io/Propagation-of-Uncertainty-Calculator/
    try:
        term1 = np.square(-1 * (Frag / (Par + Frag) / Par) * dPar)
        term2 = np.square((1 / (Par + Frag)) * dFrag)

        PE_stdev = np.sqrt(term1+term2)
        
        return [efficiency, PE_stdev]

    except Exception as e:
        print(f'Error encountered during calculation of photogfragmentaion efficiency at wavelength {W}nm: {e}.\nWriting zeros for PE and PE_stdev')
        QApplication.processEvents()      
        return [0, 0] 

if __name__ == "__main__":

    W_nm = 200
    P = 2.2
    dP = 0.1
    Par = 2.E7
    dPar = 0.02 * Par
    Frag = 2.E6
    dFrag = 0.02 * Frag

    PE, PE_error = PE_calc(W_nm, P, dP, Par, dPar, Frag, dFrag)
    print(f'PE: {PE}')
    print(f'PE_Error: {PE_error}')