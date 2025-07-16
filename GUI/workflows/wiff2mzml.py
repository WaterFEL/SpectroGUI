import os, traceback, subprocess, time
from PyQt6.QtWidgets import QApplication

def convert_wiff_to_mzml(wiff_file, directory, mzml_directory):
    ''' Function to convert .wiff files to .mzml using msconvert
    input is .wiff file, directory that contains .wiff files, and directory to output mzml files to'''
    
    #check if required files are present
    wiff_file_check = os.path.join(directory, wiff_file)
    scan_file_check = f'{os.path.join(directory, wiff_file)}.scan'
    
    if not os.path.exists(wiff_file_check):
        print(f'The corresponding .wiff file is missing from the directory. Please add the following file to the directory, and re-run the code:\n{os.path.basename(wiff_file_check)}\n\n')
        QApplication.processEvents()
        return False

    if not os.path.exists(scan_file_check):
        print(f'The corresponding .scan file is missing from the directory. Please add the following file to the directory, and re-run the code:\n{os.path.basename(scan_file_check)}\n\n')
        QApplication.processEvents()
        return False

    try:

        # Use subprocess.run and capture output for debugging
        result = subprocess.run(['msconvert', os.path.join(directory, wiff_file), '-o', mzml_directory, '--mzML', '--64', '--verbose'],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Print command output for debugging purposes
        print(f"msconvert stdout:\n{result.stdout}")
        print(f"msconvert stderr:\n{result.stderr}")

        # Check the result and raise an error if the command failed
        if result.returncode != 0:
            print(f"msconvert failed with return code {result.returncode}. Check the output above for details.")
            return False

        time.sleep(2)

        return True

    except FileNotFoundError:
        print("msconvert (Part of proteowizard) could not be found. Did you add the required directories to your system's PATH?\n")
        QApplication.processEvents()
        return False

    except subprocess.CalledProcessError as cpe:    
        print(f'Subprocess error converting {wiff_file} to mzML: {cpe}\nTraceback: {traceback.format_exc()}\n')
        QApplication.processEvents()
        return False

    except Exception as e: 
        print(f'Unexpected error converting {wiff_file} to mzML: {e}\nTraceback: {traceback.format_exc()}\n')
        QApplication.processEvents()
        return False
