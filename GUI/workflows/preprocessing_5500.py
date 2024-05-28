import os
import traceback
from PyQt6.QtWidgets import QApplication

def preprocessing_5500(directory, parent_mz, search_window, frag_list_file, extract_mzml_flag, PowerNorm_flag, power_file, extract_raw_data_flag, plot_flag, height, threshold, prominence, width):

    def check_empty_negative_and_non_numeric(entry, var_name):
        '''A function to check whether values are negative or contain non-numeric characters'''
        if not entry:
            print(f'The field for the {var_name} is empty!')
            QApplication.processEvents()
            return False

        try:
            if float(entry) < 0:
                print(f'The {var_name} has been assigned a negative value, which is impossible.')
                QApplication.processEvents()
                return False
        except ValueError:
            print(f'The field for the {var_name} contains non-numeric characters!')
            QApplication.processEvents()
            return False
        except Exception as e:
            print(f'Error parsing the input for {var_name}: {e}\nTraceback: {traceback.format_exc()}\n')
            QApplication.processEvents()
            return False

        return True

    def check_empty_only(entry, var_name):
        '''A function to check whether an entry is empty (like a directory or filepath)'''
        if not entry:
            print(f'The field for the {var_name} is empty!')
            QApplication.processEvents()
            return False
        return True

    ###Directory###
    if not check_empty_only(directory, 'directory') or not os.path.isdir(directory):
        print(f'The directory provided does not exist!')
        QApplication.processEvents()
        return False

    ###parent m/z###
    if not check_empty_negative_and_non_numeric(parent_mz, 'parent mz'):
        return False

    ###search window###
    if not check_empty_negative_and_non_numeric(search_window, 'search window'):
        return False

    ###Power file checks###
    power_file_checks_passed = True
    if PowerNorm_flag:
        if not check_empty_only(power_file, 'power file') or not os.path.isfile(power_file):
            print('The power data file could not be found. Please check that you have specified the directory and file name (with its extension!) properly.')
            QApplication.processEvents()
            return False

        #Read the CSV and verify its contents are in the right format
        with open(power_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line:  #skip empty lines
                    line = line.strip().split(',')
                    if len(line) != 3:
                        print(f'This line in the power file {os.path.basename(power_file)}: {line}\ndoes not meet the required format. Each row must only contain three numeric values with the following format:\nWavelength(nm), Laser power, and the StDev of the laser power.')
                        QApplication.processEvents()
                        power_file_checks_passed = False
                        break

    if not power_file_checks_passed:
        return False

    ###Fragments file###
    if not os.path.isfile(frag_list_file):
        print(f'The fragment file {os.path.basename(frag_list_file)} does not exist. Please provide a valid file path, including the directory.')
        QApplication.processEvents()
        return False

    #Scipy peak finding parameters
    height_check = check_empty_negative_and_non_numeric(height, 'height')
    threshold_check = check_empty_negative_and_non_numeric(threshold, 'threshold')
    prominence_check = check_empty_negative_and_non_numeric(prominence, 'prominence')
    width_check = check_empty_negative_and_non_numeric(width, 'width')
    
    #Final validation
    final_check = all([height_check, threshold_check, prominence_check, width_check])
    return final_check
