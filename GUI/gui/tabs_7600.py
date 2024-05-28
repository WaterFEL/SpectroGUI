#import python libraries once it is verified that they are installed
from PyQt6.QtWidgets import QApplication, QHBoxLayout, QComboBox, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QMessageBox, QLabel, QGroupBox, QLineEdit, QPushButton, QFileDialog, QTextEdit, QCheckBox, QSpinBox, QSizePolicy, QDoubleSpinBox

#placeholder tab currently
class QTRAP7600_control(QWidget):
    def __init__(self, text_redirector, parent=None):
        super().__init__(parent)
        self.text_redirector = text_redirector
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        
        message = QLabel('This feature will be added in the future. For now, this tab is just a placeholder.')
        
        layout.addWidget(message)
        layout.addStretch(1)        

#placeholder tab currently        
class QTRAP7600_UVPD_processing(QWidget):
    def __init__(self, text_redirector, parent=None):
        super().__init__(parent)
        self.text_redirector = text_redirector
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        
        message = QLabel('This feature will be added in the future. For now, this tab is just a placeholder.')
        
        layout.addWidget(message)
        layout.addStretch(1)

#placeholder tab currently        
class QTRAP7600_IRMPD_processing(QWidget):
    def __init__(self, text_redirector, parent=None):
        super().__init__(parent)
        self.text_redirector = text_redirector
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        
        message = QLabel('This feature will be added in the future. For now, this tab is just a placeholder.')
        
        layout.addWidget(message)
        layout.addStretch(1)