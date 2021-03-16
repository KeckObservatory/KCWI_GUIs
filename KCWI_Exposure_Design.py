#! @KPYTHON3@

import sys,os
import subprocess
from PyQt5.QtWidgets import QFrame, QLabel,QHBoxLayout,QLineEdit,QPushButton,QVBoxLayout,QApplication,QCheckBox, QTextEdit, QWidget, QProgressBar, QGridLayout
from PyQt5.QtCore import QThread, pyqtSignal, QProcess
from PyQt5 import QtGui


class separator(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(3)
        #self.setFixedWidth(100)

class Exposure_GUI(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.runMode = ''
        self.auto_object_mode = ''
        self.applyColor = 'LawnGreen'
        self.scienceColor = 'LawnGreen'
        self.twilightColor = 'Gold'
        self.biasColor = 'Gold'
        self.darkColor = 'Gold'
        self.fpcColor = 'Orange'
        self.abortColor = 'Red'
        self.buttonSize = 120
        self.Bold = QtGui.QFont()
        self.Bold.setBold(True)
        self.init_ui()
        self.setWindowTitle("KCWI Exposure Control")
        self.start_keyword_monitor()

    def init_ui(self):
        # create objects
        # labels
        ########### EXPOSURE
        self.lbl1 = QLabel('Exptime')
        self.exptime = QLineEdit()
        self.lbl2 = QLabel('Number of exp.')
        self.nexp = QLineEdit()
        self.update_exptime = QPushButton('Set Exptime')
        self.update_exptime.setStyleSheet("background-color : %s" % self.applyColor)

        # set defaults
        self.exptime.setText('1')
        self.nexp.setText('1')

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.lbl1,0,0)
        grid_layout.addWidget(self.exptime,1,0)
        grid_layout.addWidget(self.update_exptime,2,0)

        grid_layout.addWidget(self.lbl2, 0,1)
        grid_layout.addWidget(self.nexp, 1,1)

        self.separator1 = separator()

        ############ OBJECT
        self.lbl3 = QLabel('Object')
        self.object = QLineEdit()
        self.objectUpdate = QPushButton('Set Object')
        self.objectUpdate.setStyleSheet("background-color : %s" % self.applyColor)
        grid_layout.addWidget(self.lbl3,0,2)
        grid_layout.addWidget(self.object,1,2)
        self.objectUpdate.clicked.connect(self.change_object)
        grid_layout.addWidget(self.objectUpdate,2,2)


        ############# SKYPA
        self.lbl4 = QLabel('Sky PA')
        self.skypa = QLineEdit()
        self.skypaUpdate = QPushButton('Set Sky PA')
        self.skypaUpdate.setStyleSheet("background-color : %s" % self.applyColor)       
        grid_layout.addWidget(self.lbl4,0,3)
        grid_layout.addWidget(self.skypa,1,3)
        grid_layout.addWidget(self.skypaUpdate,2,3)
        self.skypaUpdate.clicked.connect(self.change_skypa)


        # buttons
        # science exposure
        self.science = QPushButton('Science \n exposure')
        self.science.setFont(self.Bold)
        self.science.setFixedHeight(80)
        self.science.setMinimumWidth(120)
        self.science.setStyleSheet("background-color : %s" % self.scienceColor)
        # twilight flat
        self.twiflat = QPushButton('Twilight flat')
        self.twiflat.setStyleSheet("background-color : %s" % self.twilightColor)
        # Bias
        self.bias = QPushButton('Bias')
        self.bias.setStyleSheet("background-color : %s" % self.biasColor)
        # dark
        self.dark = QPushButton('Dark')
        self.dark.setStyleSheet("background-color : %s" % self.darkColor)
        # focal plane camera
        self.fpc = QPushButton('FPC exposure')
        self.fpc.setStyleSheet("background-color : %s" % self.fpcColor)
        # abort
        self.abort_script = QPushButton('Abort script')
        self.abort_script.setStyleSheet("background-color : %s" % self.abortColor)

        self.separator2 = separator()

        buttons = QVBoxLayout()
        buttons.addWidget(self.science)
        buttons.addWidget(self.twiflat)
        buttons.addWidget(self.bias)
        buttons.addWidget(self.dark)
        buttons.addWidget(self.fpc)
        buttons.addWidget(self.abort_script)


        # Exposure progress bar
        #label_style = 'border: 1px inset grey; background-color: white'
        #label_style = 'background-color: white'
        label_style = ''

        self.exposure_bar_lbl = QLabel('Exposure progress')        
        self.exposure_bar = QProgressBar()
        self.readout_bar_lbl = QLabel('Readout progress')
        self.readout_bar = QProgressBar()

        
        self.lbl_exptime_name = QLabel('Elapsed time')
        self.lbl_exptime_name.setFont(self.Bold)
        self.lbl_exptime_progress = QLabel('0')
        self.lbl_exptime_progress.setStyleSheet(label_style)

        self.lbl_imtype = QLabel('Image type')
        self.lbl_imtype.setFont(self.Bold)
        self.lbl_imtype_result = QLabel('0')
        self.lbl_imtype_result.setStyleSheet(label_style)
        
        self.lbl_frameno = QLabel('Next frame')
        self.lbl_frameno.setFont(self.Bold)
        self.lbl_frameno_result = QLabel('0')
        self.lbl_frameno_result.setStyleSheet(label_style)

        self.lbl_binning = QLabel('Binning')
        self.lbl_binning.setFont(self.Bold)
        self.lbl_binning_result = QLabel('0')
        self.lbl_binning_result.setStyleSheet(label_style)
        
        self.lbl_ampmode = QLabel('Amplifier')
        self.lbl_ampmode.setFont(self.Bold)
        self.lbl_ampmode_result = QLabel('0')
        self.lbl_ampmode_result.setStyleSheet(label_style)

        self.lbl_ccdmode = QLabel('CCD speed')
        self.lbl_ccdmode.setFont(self.Bold)
        self.lbl_ccdmode_result = QLabel('0')
        self.lbl_ccdmode_result.setStyleSheet(label_style)
        
        self.lbl_progname = QLabel('Program ID')
        self.lbl_progname.setFont(self.Bold)
        self.lbl_progname_result = QLabel('')
        self.lbl_progname_result.setStyleSheet(label_style)
        
        self.lbl_statenam = QLabel('Instrument State Name')
        self.lbl_statenam.setFont(self.Bold)
        self.lbl_statenam_result = QLabel('')
        self.lbl_statenam_result.setStyleSheet(label_style)

        self.lbl_slicer = QLabel('Slicer')
        self.lbl_slicer.setFont(self.Bold)
        self.lbl_slicer_result = QLabel('')
        self.lbl_slicer_result.setStyleSheet(label_style)

        self.lbl_grating = QLabel('Grating')
        self.lbl_grating.setFont(self.Bold)
        self.lbl_grating_result = QLabel('')
        self.lbl_grating_result.setStyleSheet(label_style)

        self.lbl_filter = QLabel('Filter')
        self.lbl_filter.setFont(self.Bold)
        self.lbl_filter_result = QLabel('')
        self.lbl_filter_result.setStyleSheet(label_style)

        status_layout1 = QVBoxLayout()
        status_layout1.addWidget(self.exposure_bar_lbl)
        status_layout1.addWidget(self.exposure_bar)
        status_layout1.addWidget(self.readout_bar_lbl)
        status_layout1.addWidget(self.readout_bar)
        #status_layout1.addWidget(self.lbl_exptime_name)
        #status_layout1.addWidget(self.lbl_exptime_progress)
        
        status_layout2 = QGridLayout()
        # first row
        status_layout2.addWidget(self.lbl_exptime_name,0,0)
        status_layout2.addWidget(self.lbl_exptime_progress,1,0)
        status_layout2.addWidget(self.lbl_imtype,0,1)
        status_layout2.addWidget(self.lbl_imtype_result,1,1)
        status_layout2.addWidget(self.lbl_frameno,0,2)
        status_layout2.addWidget(self.lbl_frameno_result,1,2)
        # second row
        status_layout2.addWidget(self.lbl_binning,2,0)
        status_layout2.addWidget(self.lbl_binning_result,3,0)
        status_layout2.addWidget(self.lbl_ampmode,2,1)
        status_layout2.addWidget(self.lbl_ampmode_result,3,1)
        status_layout2.addWidget(self.lbl_ccdmode,2,2)
        status_layout2.addWidget(self.lbl_ccdmode_result,3,2)
        # third row
        status_layout2.addWidget(self.lbl_progname,4,0)
        status_layout2.addWidget(self.lbl_progname_result,5,0)
        status_layout2.addWidget(self.lbl_statenam,4,1, 1,2)
        status_layout2.addWidget(self.lbl_statenam_result,5,1, 1,2)
        # fourth row
        status_layout2.addWidget(self.lbl_slicer, 6, 0)
        status_layout2.addWidget(self.lbl_slicer_result, 7, 0)
        status_layout2.addWidget(self.lbl_grating, 6, 1)
        status_layout2.addWidget(self.lbl_grating_result, 7, 1)
        status_layout2.addWidget(self.lbl_filter, 6, 2)
        status_layout2.addWidget(self.lbl_filter_result, 7, 2)

        #status_layout.addStretch()
        status_layout = QVBoxLayout()
        status_layout.addLayout(status_layout1)
        status_layout.addLayout(status_layout2)

        # output
        self.output = QTextEdit()
        self.test_mode = QCheckBox('Test mode (show command, no action)')
        self.test_mode.clicked.connect(self.setRunMode)
        # automatically set object
        self.auto_object = QCheckBox('Automatically set object from Telescope Pointing Information')
        self.auto_object.clicked.connect(self.setAutoObject)


        # combine buttons and status in a horizontal layout
        buttons_status = QHBoxLayout()
        buttons_status.addLayout(buttons)
        buttons_status.addLayout(status_layout)

        # create the master Vertical layout

        master_layout = QVBoxLayout()
        master_layout.addLayout(grid_layout)
        master_layout.addWidget(self.separator1)
        master_layout.addLayout(buttons_status)
        master_layout.addWidget(self.separator2)
        #master_layout.addWidget(self.abort_script)
        master_layout.addWidget(self.output)        
        master_layout.addWidget(self.test_mode)
        master_layout.addWidget(self.auto_object)

        self.setLayout(master_layout)

