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
        #create a file to bypass the 250 character limit of msconvert, then delete it
        temp_command_file = os.path.join(directory, 'msconvert_command.txt')
        
        with open(temp_command_file, 'w') as opf:
            opf.write('"{os.path.join(directory, wiff_file)}" -o "{mzml_directory}" --mzML --64\n') 

        subprocess.run(['msconvert', os.path.join(directory, wiff_file), '-o', mzml_directory, '--mzML', '--64'])
        os.remove(temp_command_file)
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
