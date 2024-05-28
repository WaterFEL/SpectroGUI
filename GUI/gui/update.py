import git, os, sys, shutil, subprocess, stat, time
from datetime import datetime
from PyQt6.QtWidgets import QApplication

def Update_GUI_files(repo_url, root, ID_file, repo_SHA, delete_dir_function, ensure_update):
    '''Updates the .py files associated with the MobCal-MPI GUI. Inputs are the repo URL,  the directory where the GUI .py launcher is located, and a .txt file containing the SHA value of the user's local clone of the GUI.'''

    # Define the repository URL
    temp_dir = os.path.join(root, 'temp')

    #only clone the repo once when updating the Update.py file
    if ensure_update:
        print(f'{datetime.now().strftime("[ %H:%M:%S ]")} Cloning {repo_url} ...')
        QApplication.processEvents()

        #Remove the temporary directory if it exists
        if os.path.isdir(temp_dir):
            delete_dir_function(temp_dir)
        
        #Clone the GitHub repository to the temporary directory
        try: 
            repo = git.Repo.clone_from(repo_url, temp_dir, branch='master')
            print(f'{datetime.now().strftime("[ %H:%M:%S ]")} Cloning complete.')
            QApplication.processEvents()
        
        except Exception as e: 
            print(f'An exception occured when attempting to clone the ORCA Analysis GUI repo: {e}')
            print('This block is most commonly entered due to lack of an internet connection, although the error message above may indicate otherwise... Use your best judgement :)')
            print('Please feel free to use the local version of the GUI and update once your internet connection is retored.')
            QApplication.processEvents()
            return

        print(f'{datetime.now().strftime("[ %H:%M:%S ]")} Ensuring that the local version of {os.path.join(root, "gui", "Update.py")} is up to date...')
        QApplication.processEvents()
        
        #create a location to write a python script to update Update.py to the most recent version
        update_script_path = os.path.join(temp_dir, 'initial_update.py')
        
        #ensure that the Update.py script is replaced with the most recent version before updating any other files, as dependencies can change over time
        update_files = {str(os.path.join(root, 'gui', 'update.py')): str(os.path.join(temp_dir, 'GUI', 'gui', 'update.py'))} #Update function
    
    else:
        print(f'{datetime.now().strftime("[ %H:%M:%S ]")} Updating all .py modules to their most recent version...')
        QApplication.processEvents()

        #create a location to write a python script to update Update.py to the most recent version
        update_script_path = os.path.join(temp_dir, 'Allfiles_update.py')

        #A handy dictionary to hold the paths of the files to be updated for subsequent looping. Syntax is as follows- Path to local file : Path to cloned GitHub file
        update_files = {
            #Launcher
            str(os.path.join(root, 'Launcher.py')): str(os.path.join(temp_dir, 'GUI', 'Launcher.py')), #GUI launcher

            #GUI configuration files
            str(os.path.join(root, 'gui', 'gui.py')): str(os.path.join(temp_dir, 'GUI', 'gui', 'gui.py')), #GUI configuration .py file
            str(os.path.join(root, 'gui', 'icon.jpg')): str(os.path.join(temp_dir, 'GUI', 'gui', 'icon.jpg')), #GUI configuration .py file
            str(os.path.join(root, 'gui', 'tabs_5500.py')): str(os.path.join(temp_dir, 'GUI', 'gui', 'tabs_5500.py')), #GUI layout for all tabs related to the QTRAP5500
            str(os.path.join(root, 'gui', 'tabs_7600.py')): str(os.path.join(temp_dir, 'GUI', 'gui', 'tabs_7600.py')), #GUI layout for all tabs related to the QTRAP7600

            #SCIEX specific workflows
            str(os.path.join(root, 'SCIEX', 'process_UVPD_5500.py')): str(os.path.join(temp_dir, 'GUI', 'workflows', 'process_UVPD_5500.py')), #Main function for processing UVPD data taken on the QTRAP 5500 

            #Generic workflows
            str(os.path.join(root, 'workflows', 'calc_PE.py')): str(os.path.join(temp_dir, 'GUI', 'workflows', 'calc_PE.py')), #Functions to calculate photofrag efficiency
            str(os.path.join(root, 'workflows', 'integrate_mzml.py')): str(os.path.join(temp_dir, 'GUI', 'workflows', 'integrate_mzml.py')), #Function to integrate mass spectra extracted from mzML files
            str(os.path.join(root, 'workflows', 'preprocessing_5500.py')): str(os.path.join(temp_dir, 'GUI', 'workflows', 'preprocessing_5500.py')), #Function to validate inputs provided to the GUI in the QTRAP5500 tabs
            str(os.path.join(root, 'workflows', 'RawData_from_mzml.py')): str(os.path.join(temp_dir, 'GUI', 'workflows', 'RawData_from_mzml.py')), #Function to extract and print raw data to a .csv file
            str(os.path.join(root, 'workflows', 'wiff2mzml.py')): str(os.path.join(temp_dir, 'GUI', 'workflows', 'wiff2mzml.py')), #Function to convert .wiff files (SCIEX format) to readable mzml files
        }
    
    #update process for Windows users
    if os.getenv('APPDATA') is not None:
               
        with open(update_script_path, 'w') as opf:
            opf.write('import os, sys\n')
            opf.write('import shutil\n')
            
            #Write the logic to update each file
            for local_path, github_path in update_files.items():
                opf.write(f'if os.path.isfile(r"{local_path}"): os.remove(r"{local_path}")\n')
                opf.write(f'elif os.path.isdir(r"{local_path}"): shutil.rmtree(r"{local_path}")\n')
                opf.write(f'shutil.move(r"{github_path}", r"{os.path.dirname(local_path)}")\n')
            opf.write('sys.exit(0)')
            
            #ensure file updates; without this, users can encounter issues if the .py file is created on cloud services like OneDrive
            opf.flush()
            os.fsync(opf.fileno())
        
        time.sleep(5) #a short delay so that Cloud-based services have enough time to update.

        #Execute the update script and exit
        try:
            subprocess.Popen(['python', update_script_path], shell=True)

        except subprocess.SubprocessError as e:
            print(f'{datetime.now().strftime("[ %H:%M:%S ]")} A subprocess error occurred while updating files from the script {update_script_path}: {e}')
            return

        except Exception as e:
            print(f'{datetime.now().strftime("[ %H:%M:%S ]")} An unexpected error occurred when trying execute {update_script_path}: {e}')
            print('Please report this error and the sequence of events that caused it to appear to the issues section of the GitHub repo.')
            return

        with open(ID_file,'w') as opf:
            opf.write(repo_SHA)

        return
    
    #Update process for Mac/Linux users
    else:
        for local_path, github_path in update_files.items():
            #Similar to Windows, but using direct Python commands instead of writing to a script
            if os.path.isfile(local_path):
                os.remove(local_path)
            shutil.move(github_path, os.path.dirname(local_path))

        #Update the ID file
        with open(ID_file, 'w') as opf:
            opf.write(repo_SHA)

        return