#import python libraries once it is verified that they are installed
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QComboBox, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QMessageBox, QLabel, QGroupBox, QLineEdit, QPushButton, QFileDialog, QTextEdit, QCheckBox, QSpinBox, QSizePolicy, QDoubleSpinBox

#import module dependencies
from SCIEX.process_UVPD_5500 import *

class QTRAP5500_control(QWidget):
    def __init__(self, text_redirector, parent=None):
        super().__init__(parent)
        self.text_redirector = text_redirector
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        
        message = QLabel('This feature will be added in the future. For now, this tab is just a placeholder.')
        
        layout.addWidget(message)
        layout.addStretch(1)

class QTRAP5500_UVPD_processing(QWidget):
    def __init__(self, text_redirector, parent=None):
        super().__init__(parent)
        self.text_redirector = text_redirector
        self.initUI()

    def initUI(self):
      
        layout = QVBoxLayout(self)

        #XYZ file input section - title, input box, and explorer option for browsing xyz files
        dir_layout = QHBoxLayout()

        dir_label = QLabel('Directory:')
        self.dir_path_input = QLineEdit()
        self.dir_path_input.setPlaceholderText('Location of .wiff files or DirName of the mzml directory.')
        
        dir_button = QPushButton('Browse')
        dir_button.clicked.connect(self.browse_directory)  #Connect the button click to the browse_directory function

        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_path_input)
        dir_layout.addWidget(dir_button)
       
        layout.addLayout(dir_layout)
        layout.addSpacing(5)  

        # Base Peak Range
        basepeak_layout = QHBoxLayout()

        base_peak_label = QLabel('Parent m/z:')
        self.basepeak_input = QDoubleSpinBox()
        self.basepeak_input.setDecimals(2)
        self.basepeak_input.setMinimum(1.00)
        self.basepeak_input.setMaximum(10000.00)    
        self.basepeak_input.setSingleStep(1)    
        self.basepeak_input.setValue(203.01)
        self.basepeak_input.setMinimumWidth(50)   
        
        #search window for finding peaks (both the parent m/z and all photofragments)
        search_window_label = QLabel('Search window (m/z):')
        self.search_window_input = QDoubleSpinBox()
        self.search_window_input.setDecimals(2)
        self.search_window_input.setMinimum(0.05)
        self.search_window_input.setMaximum(10.00)    
        self.search_window_input.setSingleStep(0.05)    
        self.search_window_input.setValue(0.25)
        self.search_window_input.setMinimumWidth(50)   

        basepeak_layout.addWidget(base_peak_label)
        basepeak_layout.addWidget(self.basepeak_input)
        basepeak_layout.addSpacing(5)
        basepeak_layout.addWidget(search_window_label)
        basepeak_layout.addWidget(self.search_window_input)
        basepeak_layout.addStretch(1)

        layout.addLayout(basepeak_layout)
        layout.addSpacing(5)  

        #scipy peakfind parameters
        peak_fit_param_title = QLabel('Peak finder parameters (Defaults reccomended, values denote # of points in 0.01 increments):')
        peak_fit_param_layout = QHBoxLayout()

        height_label = QLabel('Height:')
        self.height_input = QDoubleSpinBox()
        self.height_input.setDecimals(1)
        self.height_input.setMinimum(0.0)
        self.height_input.setMaximum(10000000.0)    
        self.height_input.setSingleStep(10)    
        self.height_input.setValue(2000.0)
        self.height_input.setMinimumWidth(20)           

        threshold_label = QLabel('Threshold:')
        self.threshold_input = QDoubleSpinBox()
        self.threshold_input.setDecimals(1)
        self.threshold_input.setMinimum(0.0)
        self.threshold_input.setMaximum(10000000.0)    
        self.threshold_input.setSingleStep(10)    
        self.threshold_input.setValue(2000.0)
        self.threshold_input.setMinimumWidth(20)    

        prominence_label = QLabel('Prominence:')
        self.prominence_input = QDoubleSpinBox()
        self.prominence_input.setDecimals(1)
        self.prominence_input.setMinimum(0.0)
        self.prominence_input.setMaximum(100000.0)    
        self.prominence_input.setSingleStep(10.0)    
        self.prominence_input.setValue(200.0)
        self.prominence_input.setMinimumWidth(20)    

        width_label = QLabel('Width:')
        self.width_input = QDoubleSpinBox()
        self.width_input.setDecimals(1)
        self.width_input.setMinimum(0.0)
        self.width_input.setMaximum(1000.00)    
        self.width_input.setSingleStep(1.0)    
        self.width_input.setValue(5.0)
        self.width_input.setMinimumWidth(20)    

        peak_fit_param_layout.addWidget(height_label)
        peak_fit_param_layout.addWidget(self.height_input)
        peak_fit_param_layout.addSpacing(5)

        peak_fit_param_layout.addWidget(threshold_label)
        peak_fit_param_layout.addWidget(self.threshold_input)
        peak_fit_param_layout.addSpacing(5)        

        peak_fit_param_layout.addWidget(prominence_label)
        peak_fit_param_layout.addWidget(self.prominence_input)
        peak_fit_param_layout.addSpacing(5)        

        peak_fit_param_layout.addWidget(width_label)
        peak_fit_param_layout.addWidget(self.width_input)
        peak_fit_param_layout.addStretch(1)        

        layout.addWidget(peak_fit_param_title)
        layout.addLayout(peak_fit_param_layout)
        layout.addSpacing(5)

        #Fragment Ion Text file
        frag_layout = QHBoxLayout()
        
        fragment_file_label = QLabel('Fragment .csv file:')
        self.fragment_file_input = QLineEdit()
        self.fragment_file_input.setPlaceholderText('Directory + filename. See ReadMe for format of .csv file.')
        self.frag_file_button = QPushButton('Select .csv')
        self.frag_file_button.clicked.connect(self.browse_frag_file)  #Connect the button click to the browse_power_file function

        frag_layout.addWidget(fragment_file_label)
        frag_layout.addWidget(self.fragment_file_input)
        frag_layout.addWidget(self.frag_file_button)

        layout.addLayout(frag_layout)
        layout.addSpacing(5)  
        
        #Extract mzML from .wiff Flag
        self.extract_mzml_checkbox = QCheckBox('Extract mzML files from .wiff?')

        layout.addWidget(self.extract_mzml_checkbox)
        layout.addSpacing(5)  

        #PowerNorm Flag
        self.power_norm_checkbox = QCheckBox('Normalize to Laser Power? (Requires power data file)')
        self.power_norm_checkbox.stateChanged.connect(self.toggle_power_data_input)

        layout.addWidget(self.power_norm_checkbox)
        layout.addSpacing(5)

        #PowerNorm file input section
        power_file_layout = QHBoxLayout()

        self.power_data_label = QLabel('Power file (.csv):')
        self.power_data_file_input = QLineEdit()
        self.power_data_file_input.setPlaceholderText(r'Example: D:\SampleData\power_400_600_100us.csv')
        self.power_file_button = QPushButton('Select .csv')
        self.power_file_button.clicked.connect(self.browse_power_file)  #Connect the button click to the browse_power_file function

        #default setting is off unless the powernorm checkbox is checked
        self.power_data_label.setEnabled(False)
        self.power_data_file_input.setEnabled(False)
        self.power_file_button.setEnabled(False)

        power_file_layout.addWidget(self.power_data_label)
        power_file_layout.addWidget(self.power_data_file_input)
        power_file_layout.addWidget(self.power_file_button)

        layout.addLayout(power_file_layout)
        layout.addSpacing(5)

        #PrintRawData Flag
        self.print_raw_data_checkbox = QCheckBox('Print Raw Data?')

        layout.addWidget(self.print_raw_data_checkbox)
        layout.addSpacing(5)

        #Plot integrations flag
        self.plot_integrations_checkbox = QCheckBox('Plot peak integrations to external files for validation? (WARNING! TAKES A WHILE!)')

        layout.addWidget(self.plot_integrations_checkbox)
        layout.addSpacing(5)

        #Adjacent averaging input
        smoothing_layout = QHBoxLayout()

        smoothing_label = QLabel('# Adj. Averaging points for PE:')
        self.smoothing_input = QDoubleSpinBox()
        self.smoothing_input.setDecimals(0)
        self.smoothing_input.setMinimum(2)
        self.smoothing_input.setMaximum(25)    
        self.smoothing_input.setSingleStep(1)    
        self.smoothing_input.setValue(3)
        self.smoothing_input.setMinimumWidth(50)   

        smoothing_layout.addWidget(smoothing_label)
        smoothing_layout.addSpacing(5)
        smoothing_layout.addWidget(self.smoothing_input)
        smoothing_layout.addStretch(1)

        layout.addLayout(smoothing_layout)
        layout.addSpacing(5)

        #Fragment Ion Text file
        output_layout = QHBoxLayout()
        
        out_file_label = QLabel('Output .xlsx basename:')
        self.out_file_input = QLineEdit()
        self.out_file_input.setPlaceholderText('file basname only. No need for directory or file extension.')

        output_layout.addWidget(out_file_label)
        output_layout.addWidget(self.out_file_input)

        layout.addLayout(output_layout)
        layout.addSpacing(5)  

        #Run Button
        run_button = QPushButton('Run')
        run_button.clicked.connect(self.run_UVPD_QTRAP5500)

        layout.addWidget(run_button)
        layout.addStretch(1)

        layout.setContentsMargins(30, 30, 30, 30) 
        self.setLayout(layout)

    def browse_directory(self):
        directory_path = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if directory_path:
            self.dir_path_input.setText(directory_path)

    def toggle_power_data_input(self, state):
        #Toggle power input depenidng on whether the PowerNorm box is checked 
        enabled = state == 2  #Qt.CheckState.Checked == 2
        self.power_data_label.setEnabled(enabled)
        self.power_data_file_input.setEnabled(enabled)
        self.power_file_button.setEnabled(enabled)

    def browse_power_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select .csv file', '', 'CSV Files (*.csv)')

        #Check if a file path was selected
        if file_path:
            self.power_data_file_input.setText(file_path)

    def browse_frag_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select .csv file', '', 'CSV Files (*.csv)')

        #Check if a file path was selected
        if file_path:
            self.fragment_file_input.setText(file_path)

    def run_UVPD_QTRAP5500(self):
        
        #assign GUI inputs to variables
        directory = self.dir_path_input.text()
        basepeak = self.basepeak_input.value()
        search_window = self.search_window_input.value()
        frag_list_file = self.fragment_file_input.text()        
        extract_mzml_flag = self.extract_mzml_checkbox.isChecked()   #Checkbox for extracting .wiff files
        PowerNorm_flag = self.power_norm_checkbox.isChecked()        #Checkbox for normalizing photofragmentation efficiency to laser power
        extract_raw_data_flag = self.print_raw_data_checkbox.isChecked()     #Checkbox for printing the mass spectra used to calculate photofragmentation efficiency     
        plot_flag = self.plot_integrations_checkbox.isChecked() #Chekcbox for plotting integrations of mass spectra ot external files
        out_basename = self.out_file_input.text()

        #peak fit parameters
        height = self.height_input.value()
        threshold = self.threshold_input.value()
        prominence = self.prominence_input.value()
        width = self.width_input.value()

        #Adj. averaging smoothing input
        adj_avg_smoothing_size = self.smoothing_input.value()

        #if powernorm is checked, assign a variable to the power file. Otherwise, give the variable a None value.
        if PowerNorm_flag:
            power_file = self.power_data_file_input.text()
        else:
            power_file = None
        
        # Execute the main function, which computes photofragmentation efficiency and writes the data to a file
        process_UVPD_5500(self, directory, basepeak, search_window, frag_list_file, extract_mzml_flag, PowerNorm_flag, power_file, extract_raw_data_flag, plot_flag, height, threshold, prominence, width, adj_avg_smoothing_size, out_basename)

#placeholder tab currently
class QTRAP5500_IRMPD_processing(QWidget):
    def __init__(self, text_redirector, parent=None):
        super().__init__(parent)
        self.text_redirector = text_redirector
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        
        message = QLabel('This feature will be added in the future. For now, this tab is just a placeholder.')
        
        layout.addWidget(message)
        layout.addStretch(1)