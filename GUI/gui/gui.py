#import python libraries once it is verified that they are installed
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QComboBox, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QMessageBox, QLabel, QGroupBox, QLineEdit, QPushButton, QFileDialog, QTextEdit, QCheckBox, QSpinBox, QSizePolicy, QDoubleSpinBox
from PyQt6.QtCore import QCoreApplication, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QScreen, QIcon, QTextCursor
import numpy as np

#Import code dependencies
from gui.tabs_5500 import *
from gui.tabs_7600 import *

#Import the update function on your local machine, and update it to the most recent version from GitHub
import gui.update as update_module
from importlib import reload

import platform, os, time, shutil, stat, sys, subprocess, traceback
from datetime import datetime
from io import StringIO

#############################################
# Redirect all print statements to GUI window
#############################################

class TextRedirect(StringIO):
    def __init__(self, update_output=None, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self.update_output = update_output

    #Override the write method of the parent class (StringIO)
    def write(self, text):
        
        #Call the write method of the parent class to perform the default writing
        super().write(text)
        
        #Invoke the stored callback function to notify external components with the written text
        self.update_output(text)

#############################################
#               Main GUI Layout
#############################################
        
class SpectroGUI(QMainWindow):
    #initiate the print state redirector for all GUI classes
    def __init__(self):
        super().__init__()

        self.output_text_edit = QTextEdit()
        self.text_redirector = TextRedirect(update_output=self.update_output_text)
        sys.stdout = self.text_redirector

        self.initUI()

    def initUI(self):

        #Set up GUI main window, define tab layout, and generate output text box 
        self.setWindowTitle('WaterFEL Analysis Suite')

        #Dynamically adjust the size of the GUI window with the size of the user's screen
        #Get the primary screen's geometry
        screen = QApplication.primaryScreen().geometry()
        
        #Set GUI size to 30% of screen width x 40% of screen height, centered on the screen
        width = screen.width() * 0.3
        height = screen.height() * 0.4
        self.setGeometry(int((screen.width() - width) / 2), int((screen.height() - height) / 2), int(width), int(height))

        main_widget = QWidget(self)
        main_layout = QVBoxLayout(main_widget)

        #overall tab
        main_tabs = QTabWidget()

        #First tab level - instrument end-stations
        QTRAP_5500_MainTab = QTabWidget()
        QTRAP_7600_MainTab = QTabWidget()

        #Second Tab Level: QTRAP 5500 sub-tabs
        self.QTRAP5500_control_tab = QTRAP5500_control(self.output_text_edit)
        QTRAP_5500_MainTab.addTab(self.QTRAP5500_control_tab, 'Instrument control')

        self.QTRAP5500_UVPD_tab = QTRAP5500_UVPD_processing(self.output_text_edit)
        QTRAP_5500_MainTab.addTab(self.QTRAP5500_UVPD_tab, 'UVPD processing')

        self.QTRAP5500_IRMPD_tab = QTRAP5500_IRMPD_processing(self.output_text_edit)
        QTRAP_5500_MainTab.addTab(self.QTRAP5500_IRMPD_tab, 'IRMPD processing')

        #Second tab level: QTRAP 6600 sub-tabs
        self.QTRAP7600_control_tab = QTRAP7600_control(self.output_text_edit)
        QTRAP_7600_MainTab.addTab(self.QTRAP7600_control_tab, 'Instrument control')

        self.QTRAP7600_UVPD_tab = QTRAP7600_UVPD_processing(self.output_text_edit)
        QTRAP_7600_MainTab.addTab(self.QTRAP7600_UVPD_tab, 'UVPD processing')

        self.QTRAP7600_IRMPD_tab = QTRAP7600_IRMPD_processing(self.output_text_edit)
        QTRAP_7600_MainTab.addTab(self.QTRAP7600_IRMPD_tab, 'IRMPD processing')

        #Add tabs to main tab
        main_tabs.addTab(QTRAP_5500_MainTab, 'QTRAP 5500')
        main_tabs.addTab(QTRAP_7600_MainTab, 'QTRAP 7600')
        main_layout.addWidget(main_tabs)

        #Create and add a window for print statements to show up within the GUI interface
        output_title_label = QLabel('Status window')
        output_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(output_title_label)
        self.output_text_edit.setMinimumHeight(150)  
        main_layout.addWidget(self.output_text_edit)
        
        #assign final GUI layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        #redirect text to output window
        sys.stdout = self.text_redirector

    def update_output_text(self, text):
        self.output_text_edit.insertPlainText(text)
        
        #move the cursor to the end of the text edit to ensure it scrolls to the bottom
        self.output_text_edit.moveCursor(QTextCursor.MoveOperation.End)
        self.output_text_edit.ensureCursorVisible()
       
    def closeEvent(self, event):       
        event.ignore() # Do not let the application close without a prompt
        self.close_application()
    
    def closeEvent(self, event):
        choice = QMessageBox.question(self, 'Exit Confirmation',
                                      'Are you sure you wish to exit?',
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if choice == QMessageBox.StandardButton.Yes:
            #restore original stdout (ie. normal printing) before closing the application
            sys.stdout = sys.__stdout__
            event.accept()
        
        else:
            event.ignore()  #ignore event to keep app open
        
    def check_for_update_and_prompt(self):
        
        #The GUI is likely to the updated throughout the years, so its best practice to implement some update functionality - users may not check GitHub frequently. 
        def get_latest_commit_sha(repo_url, branch='HEAD'):
            '''Grabs the SHA value associated with the latest commit to a GitHub repo. Function takes a URL as input.''' 
            try:
                #Run the git ls-remote command
                result = subprocess.run(['git', 'ls-remote', repo_url, branch], capture_output=True, text=True)

                #Check if the command was successful
                if result.returncode != 0:
                    print(f'{datetime.now().strftime("[ %H:%M:%S ]")} Error when obtaining the latest SHA value from the PodPals GitHub repo (likely due to lack of an internet connection):\n{result.stderr}')
                    print(f'{datetime.now().strftime("[ %H:%M:%S ]")} If you have an internet connection, it is possible something intrinsic to the repository has been modifed. Pleaser re-clone the GitHub repo, then try to launch again from the updated files.')
                    return

                #Parse the output to get the SHA
                output = result.stdout.split()
                return output[0] if output else None
            
            except Exception as e:
                print(f'{datetime.now().strftime("[ %H:%M:%S ]")} An unknown error occurred when obtaining the latest SHA value from the PodPals GitHub repo: {e}')
                print(f'Please report this error to the Issues section of the GitHub repo.')
                return

        def delete_dir(directory):
            '''Windows has special permissions on read-only folders - here's a function that deals with it using shutil.rmtree'''

            os_type = platform.system()

            def handleRemoveReadonly(func, path, exc_info):
                '''A function to deal with the error encourntered when trying to delete a file using shutil.rmtree that is read-only in Windows.'''
                
                #from: https://stackoverflow.com/questions/4829043/how-to-remove-read-only-attrib-directory-with-python-in-windows
                os.chmod(path, stat.S_IWRITE)
                os.unlink(path)

            try:
                if os_type == 'Windows':
                    shutil.rmtree(directory, onexc=handleRemoveReadonly)
                
                #no special read/write perms needed to delete read only folders on Mac/Linux platforms
                else:
                    shutil.rmtree(directory)
            
            #If using Python versions <3.9, syntax for encountering errors when deleting directories is different.
            except TypeError:

                try:
                    shutil.rmtree(directory, onerror=handleRemoveReadonly) 

                except:
                    print(f'{datetime.now().strftime("[ %H:%M:%S ]")} Encountered error when attempting to delete {directory}. This is probably because your python version is <3.9. Please update to Python 3.12+ to rectify this - you can also manually delete the temp folder after the GUI loads. ')
                    pass

            except PermissionError:
                print(f'{datetime.now().strftime("[ %H:%M:%S ]")} Encountered permission error when attempting to delete {directory}. This is probably caused by a OneDrive sync issue - you can manually delete the GUI/temp folder after the GUI loads. ')
                pass

            except Exception as e: 
                print(f'{datetime.now().strftime("[ %H:%M:%S ]")} An unexpected error encountered trying to remove {directory}: {e}.\n Please report this error and your workflow / system specs to the Issues section on Github. You can delete still delete GUI/temp manually.')         
                #Get the current working directory and define the temporary directory path
                pass

        '''Main Update function'''

        #Safer way of getting working directory as opposed to os.getcwd() - found this out the hard way when trying to update the GUI when the parent git folder was linked to VScode's internal file explorer, where os.getcwd() defaulted to the directory specified to VScode's explorer.
        root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        #URL of the MobCal-MPI repo
        repo_url = 'https://github.com/WaterFEL/SpectroGUI'

        #get SHA value of repo-ID
        repo_SHA = get_latest_commit_sha(repo_url)

        #File to store the local version's SHA value
        ID_file = os.path.join(root, 'ID.txt') 
        try:
            with open(ID_file,'r') as opf:
                file_content = opf.read()
                file_content = file_content.strip()
    
        except FileNotFoundError:
            print(f'{os.path.basename(ID_file)} could not be found in {os.path.dirname(ID_file)}. Please re-download from the PorPals GitHub repo, and re-run the GUI launcher.')
            return

        #Check if the file is in the correct format
        if '\n' in file_content or '\r' in file_content or ' ' in file_content:
            print(f'{datetime.now().strftime("[ %H:%M:%S ]")} {ID_file} is not in the correct format. Please re-download this file from the PodPals GitHub repo and re-run the GUI launcher.')
            return

        local_SHA = file_content.strip()            
        #Remove the temporary directory if it exists and only if the local and repo SHAs match
        if repo_SHA == local_SHA: 
            temp_dir = os.path.join(root, 'temp')
            if os.path.isdir(temp_dir):
                try:
                    delete_dir(temp_dir)
                except Exception as e:
                    print(f'{datetime.now().strftime("[ %H:%M:%S ]")} There was a problem deleting the /temp folder that was made from the previous update procedure: {e}.')
                    print('Please delete this manually. You can continue to use the GUI whether the /temp folder was deleted or not.')
                    pass
            
            print(f'{datetime.now().strftime("[ %H:%M:%S ]")} WaterFELs SpectroGUI is up to date! Please report any unhandled/unclear errors to the issues section of the GitHub repository.')

        else:
            choice_title = 'Update available!'
            choice_prompt = 'An update to SpectroGUI is available. Would you like to update now?'
            choice = QMessageBox.question(self, choice_title, choice_prompt, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if choice == QMessageBox.StandardButton.Yes:
                print(f'{datetime.now().strftime("[ %H:%M:%S ]")} SpectroGUI is being updated. Any errors encountered during the update process will be printed below.')
                
                #Ensure that the update function is globally accessible
                Update_GUI_files = update_module.Update_GUI_files

                #Run the update function to get the most recent version of Update.py
                ensure_update = True

                while ensure_update:
                    Update_GUI_files(repo_url, root, ID_file, repo_SHA, delete_dir, ensure_update)
                    ensure_update = False
                
                #After Update.py is updated to its most recent version, reload it and reimport the Update function
                reload(update_module)
                Update_GUI_files = update_module.Update_GUI_files
                from gui.update import Update_GUI_files

                #update the rest of the ORCA GUI .py modules to their most recent version using calls from the now up-to-date Update.py file
                Update_GUI_files(repo_url, root, ID_file, repo_SHA, delete_dir, ensure_update)                

                print(f' {datetime.now().strftime("[ %H:%M:%S ]")} The SpectroGUI files have been succesfully updated to their current version. Please close and reload the GUI.')
                return

            else:
                print(f'{datetime.now().strftime("[ %H:%M:%S ]")} The user has opted to use their local version of the WaterFEL SpectroGUI.')
                return