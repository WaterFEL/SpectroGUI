# SpectroGUI
The main GUI that conducts and analyzes photofragmentation spectra on WaterFEL instruments

## Introduction
This repository contains a Graphical User Interface (GUI) designed for the analysis of variable wavelength Ultraviolet Photodissociation (UVPD) data. It's specifically tailored for data obtained on the modified QTRAP 5500 hybrid triple-quad in the Hopkins Lab.

## Prerequisites
Before using the UVPD Analysis GUI, ensure that the following software and packages are installed on your local machine:

### Required Software
- **GitHub Desktop**: Download from [GitHub Desktop](https://desktop.github.com/). A GitHub account is not required for installation.
- **Git**: Download from [Git SCM](https://git-scm.com/). Please install in the default location and add it to PATH if necessary. A GitHub account is not required for installation.
- **Python 3.12+**: Download and install from [Python Downloads](https://www.python.org/downloads/).
-**Proteowizard's msconvert package**: Download and install the latest version from [Proteowizard Downloads](https://proteowizard.sourceforge.io/download.html). Install in the default directory.

### Required Python Packages
The GUI depends on several Python packages. Install them using the following command in your command prompt:

```console
pip install numpy scipy lxml pandas PyQt6 pyteomics gitpython
```

### PATH Configuration

After installation, add the following directories to your system's PATH. These contain the necessary executables `msconvert.exe` and `fileinfotoxml.exe`:

```text
C:\Program Files (x86)\ProteoWizard\ProteoWizard 3.0.11392
C:\Program Files (x86)\ProteoWizard\ProteoWizard 3.0.11392\FileInfoToXml
```
*Note: The version number in the paths might vary slightly.*

### Setup and Usage

After completing the installation and configuration steps, you can proceed with setting up and using the SpectroGUI.

## QTRAP 5500 - UVPD Processing

Currently, only the UVPD processing suite from data taken on a QTRAP 5500 is available. More functionality for IRMPD and instrument control will be added in the near future. Usage of this package is as follows:

- **Directory:**: The directory containing the .wiff files. Each scan saved to the .wiff file follows the naming convention 'Laser_On_XXXnm', where XXX is the wavelength of the laser light used for UVPD.

- **Parent m/z:**: The m/z of the parent ion.

- **Search window (m/z):**: The window in which to search for peaks corresponding to the parent and fragment ions.

- **Fragment .csv file:**: A .csv containing a list of fragment m/z values and any background intensity they may have. Each fragment/background intensity pair should be on its own line of thet .csv. For details,  see the [Example](https://github.com/WaterFEL/SpectroGUI/Example/Frags_FuranylFent_Oprot_100us.csv)

- **Peak finder parameters:** Denotes the # of points in the units of your mass spectrum's x-axis in scipy's peak finder uses to determine what is a peak. THe defaults are reccomended. For more details, please see the find_peaks documentation. 

- **Extract mzML files from .wiff?:** If checked, each scan in a .wiff file will be converted into its own readable mzML file. If unchecked, the code will look for mzml files in `{Directory}/mzml_directory`.

- **Normalize to Laser Power checkbox:** If checked, normalizes photofragmentation efficiency to laser power (recommended). If unchecked, photofragmentation efficiency will not be normalized. Specify the powerdata.csv file in the corresponding dialog box. For format of the power file, see the [Example](https://github.com/WaterFEL/SpectroGUI/Example/power_data_100us.csv)

- **Print Raw Data checkbox:** If checked, the full mass spectrum for each scan in the .wiff file will be printed to a .csv.

- **Plot peak integrations?** If checked, a plot will be generated showing the integration range for the parent ion and each fragment ion. Note that this sign ificantly slows down the analysis.  

- **Adjacent averaging points**: The number of adjacent averaing points to consider when generating the smoothed data. Note that the module outputs both the original **and** smoothed data.

- - **Output .xlsx basename**: The nanme that you wish to give the output Excel file. Note that this is not need to be given a file path or extension. It will be saved to path provided in the `Directory` field. 

Please report any bugs in the issues section or to cieritan@uwaterloo.ca 
