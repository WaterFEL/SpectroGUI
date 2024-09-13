'''
SpectroGUI - Instrument control and data processing for action spectroscopy measurements at WaterFEL
v0.1 (2024-05-28)
Author: Christian Ieritano (cieritan@uwaterloo.ca)

Contents: 
-GUI is launched via this .py file. This module checks that all dependencies are installed on the user's machine
-gui layout in GUI/gui.py and update function
-GUI layout for each main tab (i.e., QTRAP 5500, QTRAP 7600) are in GUI/gui/tabs_####.py
-Workflows for processing mass spectra on SCIEX-based instruments are in GUI/SCIEX

Functionality to be added:
-Instrument control for QTRAP5500 (WaterFEL end station #1)
-Instrument control and data processing for QTRAP7600 (WaterFEL end station #2)
'''

#Import modules needed for preparation of GUI launch
import importlib, platform, os, sys, shutil, subprocess
from pathlib import Path

# Before the GUI launches, check that the user has the required packages to run the UVPD analysis GUI
#The most troublesome package is Git, which also requires GitHub desktop to be on the user's machine. First, we check if it is installed.

def find_github_desktop():
    '''A function to dynamically locate GitHub Desktop'''
    os_type = platform.system()
    paths_to_check = []

    #Check process for Windows users
    if os_type == 'Windows':
        
        # First, try to find the path in the registry
        try:
            #Irrespective of install location of Git desktop, there should always be a registry key here for windows users
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Uninstall\GitHubDesktop') as key:
                path, _ = winreg.QueryValueEx(key, 'InstallLocation')
                git_exe = Path(path) / 'git.exe'
                if git_exe.exists():
                    return str(git_exe.parent)
        except FileNotFoundError:
            pass
        except OSError:
            pass

        #If unsucessful, try some other default locations.  
        paths_to_check.extend([
            Path(os.environ.get('LOCALAPPDATA', '')) / 'GitHubDesktop',
            Path(os.environ.get('PROGRAMFILES', '')) / 'GitHub Desktop',
            Path(os.environ.get('PROGRAMFILES(X86)', '')) / 'GitHub Desktop',
            Path(os.environ.get('USERPROFILE', '')) / 'AppData' / 'Local' / 'GitHubDesktop'
            # Users can add more Windows-specific paths here if they installed GitHub Desktop to a non-default location.
        ])

    # Check process for Mac users (I don't have a MAc so I have not been able to check if this works; I'm going off of stack exchange here)
    elif os_type == 'Darwin':
        paths_to_check.extend([
            Path('/Applications/GitHub Desktop.app'),
            Path.home() / 'Applications' / 'GitHub Desktop.app'
        ])
        # Users can add more Mac-specific paths here if they installed GitHub Desktop to a non-default location.

    # Check process for Linux users (I don't have have a Linux machine so I have not been able to check if this works; I'm going off of stack exchange here)
    elif os_type == 'Linux':
        paths_to_check.extend([
            Path('/usr/bin/github-desktop'),
            Path('/usr/local/bin/github-desktop')
        ])
        # Users can add more Mac-specific paths here if they installed GitHub Desktop to a non-default location.
    
    for path in paths_to_check:
        if (os_type == 'Windows' and path.is_dir()) or (os_type in ['Darwin', 'Linux'] and path.exists()):
            return str(path)
    
    return None

def find_git_executable():
    os_type = platform.system()
    
    if os_type == 'Windows':
        # Try to find the Git path in the registry
        try:
            import winreg
            # Check both HKEY_LOCAL_MACHINE and HKEY_CURRENT_USER
            for hkey in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                with winreg.OpenKey(hkey, r'Software\GitForWindows') as key:
                    path, _ = winreg.QueryValueEx(key, 'InstallPath')
                    git_exe = Path(path) / 'bin' / 'git.exe'
                    if git_exe.exists():
                        return str(git_exe)
        except FileNotFoundError:
            pass
        except OSError:
            pass

    # For macOS and Linux, as well as a failsafe for Windows
    git_path = shutil.which('git')
    if git_path is not None:
        return git_path

    # Common paths to check for Git on Unix-like systems
    unix_paths = [
        '/usr/local/bin/git',  # Common for macOS and some Linux distros
        '/opt/local/bin/git',  # Common for installations via MacPorts
        '/usr/bin/git',        # Common for Linux distros
        '/bin/git',            # Less common, but worth checking
        # more can be added as needed
    ]

    for path in unix_paths:
        if Path(path).is_file():
            return path

    # If Git executable not found, idk you probably didn't install it
    return None
    
def add_to_path(new_path):
    '''Takes a path as input and adds it to the system's PATH environment variable if it isn't already there'''
    os_type = platform.system()

    # Windows uses semicolons (;) as path separator
    if os_type == 'Windows':
        path_separator = ';'
    else:
        # Both macOS (Darwin) and Linux use colons (:) as path separator
        path_separator = ':'

    # Check if new_path is already in PATH
    if new_path not in os.environ['PATH'].split(path_separator):
        os.environ['PATH'] = new_path + path_separator + os.environ['PATH']

def check_git():
    '''Checks if GitHub Desktop and Git are installed on the Users PC and adds it to PATH, and if it isn't, promts them to instal it before continuing'''
    
    #Check for GitHub Desktop
    git_desktop_path = find_github_desktop()

    if not git_desktop_path:
        print('GitHub Desktop is not installed. Please install from the following URL to the default directory:')
        print('https://desktop.github.com/')
        sys.exit(0)
    
    else:
        #If GitHub desktop is found, add it to the system's PATH
        add_to_path(git_desktop_path)

    #Check for Git
    git_path = find_git_executable()

    if not git_path:
        print('Git is not installed. Please install from the following URL to the default directory:')
        print('https://git-scm.com/')
        sys.exit(0)
    
    else:
        #If GitHub is found, add it to the system's PATH
        add_to_path(git_path)

#Now with those functions set up, we can check for the required python modules 

def check_python_packages(required_packages):
    for package in required_packages:
        try:
            importlib.import_module(package)
        except ModuleNotFoundError:
            offer_package_install(package)

def offer_package_install(package):
    print(f'{package} cannot be found. Would you like to install it (y/n)?')
    if input().lower() == 'y':
        print(f'Installing {package}...')
        #git imports as gitpython despite is being called git (github why????????????????????)
        package_name = 'gitpython' if package == 'git' else package
        subprocess.run([sys.executable, '-m', 'pip', 'install', package_name])
    else:
        sys.exit('Exiting: Required package not installed.')

if __name__ == '__main__':
    #Check that github desktop is installed
    check_git()

    #check that all required python modules are installed
    required_packages = ['PyQt6', 'lxml', 'pyteomics', 'numpy', 'scipy', 'pandas']
    check_python_packages(required_packages)

def check_dependencies():
    #Setup a dictionary showing of the module dependencies of required modules and their functions, organized by functionality
    dependencies = {
        'gui': [
            'gui.gui.WaterFEL_Suite',
            'gui.Update.Update_GUI_files',
        ],

        'main': [
            'Python.main.main',
        ],

        'workflows': [
            'Python.workflows.convert_wiff_to_mzml',
            'Python.workflows.integrate_spectra',
            'Python.workflows.extract_RawData',
            'Python.workflows.PE_calc',
            'Python.workflows.PE_calc_noNorm',
        ]
    }

    missing_dependencies = []

    #Attempt to import each dependency
    for category, funcs in dependencies.items():
        for func in funcs:
            try:
                module_name, function_name = func.rsplit('.', 1) #split at first occurance of the period
                module = __import__(module_name, fromlist=[function_name])
                getattr(module, function_name) #test import
            
            except ImportError as e:
                missing_dependencies.append([category, func])
                print(f'ImportError for {func}: {e}')
            
            except AttributeError as e:
                missing_dependencies.append([category, func])
                print(f'Attribute error when importing {func}: {e}')

    if missing_dependencies:
        cwd = os.path.dirname(os.path.realpath(__file__))
        formatted_dependencies = ",\n".join([f'{category}: {os.path.join(cwd, (func.split(".")[0]))}' for category, func in missing_dependencies])
        print('The following Python modules are missing. Please reclone the repo from Github and try again, ensuring the missing Python modules are available in the following locations:\n', formatted_dependencies)
        return False
    
    else:
        return True

#import everything from the main GUI .py file, including the check_for_update_and_prompt function called below
from gui.gui import *

if __name__ == '__main__':
    
    #check if msconvert is available in the systems PATH
    def check_msconvert():
        try:
            subprocess.run(['msconvert'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            return False   
        #The msconvert module from Proteowizard could not be found. It is either not installed or not available in your systems PATH
        except FileNotFoundError:
            return False
     
    #Check if msconvert is available
    if not check_msconvert():
        print('The msconvert executable is not available on your machine. Please install ProteoWizard and/or make sure the directory that contains msconvert it is in your system PATH. Please see the readme on the main GitHub page.')
    
    #Check for all dependencies
    #dependencies_check = check_dependencies()
    dependencies_check = True
    #If dependencies are present, proceed to launch the GUI
    if dependencies_check:
        app = QApplication(sys.argv)

        #set the app icon for both the GUI window and taskbar - sorry windows users, you'll only ever see the icon in the GUI window!
        icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gui', 'icon.jpg')
        app.setWindowIcon(QIcon(icon_path))

        main_win = SpectroGUI()
        main_win.show() #show the main window
        main_win.check_for_update_and_prompt()  #Check for updates after showing the window    
        sys.exit(app.exec())
        
