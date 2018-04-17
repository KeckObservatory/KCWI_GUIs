import sys, os, subprocess
from PyQt5.QtWidgets import QWidget, QHBoxLayout,QTableWidget, QTableWidgetItem, QVBoxLayout, QRadioButton
from PyQt5.QtWidgets import QPushButton, QCheckBox, QLineEdit, QLabel, QApplication, QTextEdit
from pymongo import MongoClient
from PyQt5 import QtCore
from ConfigManager import save_state, state_file_name
#from QtCore import QStringList

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'KCWI Calibration GUI'
        self.left = 50
        self.right = 50
        self.width = 1000
        self.height = 600
        self.programId = ''
        #self.runMode = 'debug'
        self.runMode = ''
        self.caltype = 'all'
        self.init_ui()
        self.processOutput='Click on the right or define'


    def init_ui(self):
        # program id
        self.lbl1 = QLabel('Program ID')
        self.program = QLineEdit()
        self.program.setFixedWidth(100)
        # output directory
        self.lbl2 = QLabel('Output directory')
        self.outdir = QLineEdit()
        self.outdir.setFixedWidth(300)
        self.outdir.editingFinished.connect(self.setWorkingDirectory)
        # use outdir for output directory
        self.useOutdir = QCheckBox('Use KCWI outdir')
        self.useOutdir.setCheckState(QtCore.Qt.Unchecked)
        self.useOutdir.clicked.connect(self.runOutdir)
        # use current directory
        self.usePwd = QCheckBox('Use current directory')
        self.usePwd.setCheckState(QtCore.Qt.Unchecked)
        self.usePwd.clicked.connect(self.runPwd)

        self.hlayout1 = QHBoxLayout()
        self.hlayout1.addWidget(self.lbl1)
        self.hlayout1.addWidget(self.program)
        self.hlayout1.addWidget(self.lbl2)
        self.hlayout1.addWidget(self.outdir)
        self.hlayout1.addWidget(self.useOutdir)
        self.hlayout1.addWidget(self.usePwd)
        self.hlayout1.addStretch(3)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.right, self.width, self.height)
        self.createTable()

        buttonSize = 250

        self.reload = QPushButton('Reload configurations')
        self.list = QPushButton('List checked configurations')
        self.save = QPushButton('1 - Save states to disk')
        self.genfiles = QPushButton('2 - Generate calibration scripts')
        self.gencals = QPushButton('3 - Generate calibration flat files')

        # radio buttons for calibrations
        self.hlayout3 = QHBoxLayout()

        self.radiobutton = QRadioButton("All")
        self.radiobutton.setChecked(True)
        self.radiobutton.caltype = "all"
        self.radiobutton.toggled.connect(self.on_radio_button_toggled)
        self.hlayout3.addWidget(self.radiobutton)
        self.radiobutton = QRadioButton("Dome")
        self.radiobutton.setChecked(False)
        self.radiobutton.caltype = "dome"
        self.radiobutton.toggled.connect(self.on_radio_button_toggled)
        self.hlayout3.addWidget(self.radiobutton)
        self.radiobutton = QRadioButton("Internal")
        self.radiobutton.setChecked(False)
        self.radiobutton.caltype = "internal"
        self.radiobutton.toggled.connect(self.on_radio_button_toggled)
        self.hlayout3.addWidget(self.radiobutton)

        self.runcals = QPushButton('4 - Run cals')

        buttons = [self.reload,self.list,self.save, self.gencals, self.genfiles, self.runcals]
        for button in buttons:
                button.setFixedWidth(buttonSize)
        self.program.textChanged.connect(self.set_program)
        self.reload.clicked.connect(self.refresh_data)
        self.list.clicked.connect(self.ListConfigs)
        self.save.clicked.connect(self.saveStates)
        self.genfiles.clicked.connect(self.run_generate_cal_script)
        #self.genfiles.clicked.connect(self.showcurrent)
        self.gencals.clicked.connect(self.run_generate_cal_files)
        self.runcals.clicked.connect(self.run_calibrations)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.hlayout1)
        self.layout.addWidget(self.tableWidget)

        self.vlayout1 = QVBoxLayout()
        #self.vlayout1.addWidget(self.list)
        self.vlayout1.addWidget(self.reload)
        self.vlayout1.addWidget(self.save)
        self.vlayout1.addWidget(self.genfiles)
        self.vlayout1.addWidget(self.gencals)
        self.vlayout1.addLayout(self.hlayout3)
        self.vlayout1.addWidget(self.runcals)

        self.hlayout2 = QHBoxLayout()
        self.hlayout2.addLayout(self.vlayout1)
        self.output = QTextEdit()
        self.hlayout2.addWidget(self.output)

        self.layout.addLayout(self.hlayout2)
        self.setLayout(self.layout)
        self.show()

    def set_program(self):
        self.programId = self.program.text()
        self.refresh_data()

    def load_data(self):
        client = MongoClient('observinglogs')
        db = client.KCWI
        configurations = list(
            db.Configurations.find({'progname': self.programId}, {'statenam': 1, 'image_slicer': 1, 'filterb': 1, 'gratingb': 1,
                                                          'cwaveb': 1, 'pwaveb': 1, 'binningb': 1}))
        client.close()
        currentRow = 0
        for configuration in configurations:
            self.tableWidget.insertRow(currentRow)
            print("Setting row %d to %s\n" % (currentRow, configuration['statenam']))
            qwidget = QWidget()
            checkbox = QCheckBox()
            checkbox.setCheckState(QtCore.Qt.Unchecked)
            qhboxlayout = QHBoxLayout(qwidget)
            qhboxlayout.addWidget(checkbox)
            qhboxlayout.setContentsMargins(0, 0, 0, 0)
            self.tableWidget.setCellWidget(currentRow, 0, qwidget)
            self.tableWidget.setItem(currentRow, 1, QTableWidgetItem(configuration['statenam']))
            self.tableWidget.setItem(currentRow, 2, QTableWidgetItem(configuration['image_slicer']))
            self.tableWidget.setItem(currentRow, 3, QTableWidgetItem(configuration['filterb']))
            self.tableWidget.setItem(currentRow, 4, QTableWidgetItem(configuration['gratingb']))
            self.tableWidget.setItem(currentRow, 5, QTableWidgetItem(configuration['cwaveb']))
            self.tableWidget.setItem(currentRow, 6, QTableWidgetItem(configuration['pwaveb']))
            self.tableWidget.setItem(currentRow, 7, QTableWidgetItem(configuration['binningb']))
            currentRow += 1


    def refresh_data(self):
        self.tableWidget.setRowCount(0)
        self.load_data()


    def createTable(self):

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setRowCount(0)
        col_headers = ['Calibrate?','State Name', 'Slicer', 'Blue Filter', 'Blue Grating', 'CWaveB', 'PWaveB', 'Binning']
        self.tableWidget.setHorizontalHeaderLabels(col_headers)
        self._list=[]
        self.load_data()
        self.show()

    def ListConfigs(self):
        checked_list = []
        for i in range(self.tableWidget.rowCount()):
            if self.tableWidget.cellWidget(i, 0).findChild(type(QCheckBox())).isChecked():
                checked_list.append(self.tableWidget.item(i, 1).text())
        self.output.setText(str(checked_list))

    def saveStates(self):
        output = ''
        for i in range(self.tableWidget.rowCount()):
            if self.tableWidget.cellWidget(i, 0).findChild(type(QCheckBox())).isChecked():
                if self.runMode is not 'debug':
                    currentOutput = save_state(self.tableWidget.item(i, 1).text(),self.program.text(), self.outdir.text())
                else:
                    currentOutput = 'Simulate mode: saving state %s\n' % (self.tableWidget.item(i, 1).text())
                output += currentOutput
                output += '---------------------------------------------------\n'
            else:
                # remote the state file if the state is not "checked"
                fileName = state_file_name(self.tableWidget.item(i, 1).text(), self.program.text())
                if os.path.isfile(fileName):
                    os.unlink(fileName)

        self.showOutput(str(output))

    def on_radio_button_toggled(self):
        radiobutton = self.sender()

        if radiobutton.isChecked():
            self.showOutput("Selected mode is %s" % (radiobutton.caltype))
        self.caltype = radiobutton.caltype

    # this section of the code deals with running processes using the build-in QProcess class
    def dataReady(self):
        cursor = self.output.textCursor()
        cursor.movePosition(cursor.End)
        self.processOutput = str(self.process.readAll(), 'utf-8')
        cursor.insertText("%s\n" % self.processOutput)
        #cursor.insertText(str(self.process.readAll(), 'utf-8'))
        self.output.ensureCursorVisible()
        print(self.processOutput)


    def showOutput(self, text):
        cursor = self.output.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        self.output.ensureCursorVisible()

    def showcurrent(self):
        self.run_command_qprocess('pwd', use_kroot=False)

    def onFinished(self, exitCode, exitStatus):
        print("Process finished")
        self.showOutput("Exit code: %d\n" % exitCode)
        self.showOutput("Exit status: %s\n" % exitStatus)

    def onStart(self):
        print("Process started")

    def launchError(self, error):
        if error != QtCore.QProcess.Crashed:
            self.showOutput("Warning! There was a problem running the requested function.")

    def run_command_qprocess(self,command, command_arguments=[], use_kroot=False, csh=False):
        if use_kroot is True:
            try:
                kroot = os.environ['KROOT']
            except:
                kroot = ''
            cmdline = os.path.join(kroot,'rel','default','bin', command)
        else:
            cmdline = command
        print("Running: %s\n" % cmdline)
        self.process = QtCore.QProcess(self)
        self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.process.readyRead.connect(self.dataReady)
        self.process.finished.connect(self.onFinished)
        self.process.error.connect(self.launchError)
        if self.runMode is 'debug':
            self.showOutput('Simulation mode\n Running:\n %s' % (cmdline))
        else:
            self.showOutput('Running: %s\n' % (cmdline))
            if csh is True:
                self.process.start('csh', [cmdline])
            else:
                self.process.start(cmdline, command_arguments)
            self.showOutput('Done\n')
        self.process.waitForFinished()



    def runOutdir(self):
        self.run_command_qprocess('outdir',use_kroot=True)
        self.usePwd.setCheckState(QtCore.Qt.Unchecked)
        self.outdir.setText(self.processOutput.replace("\n",""))
        self.setWorkingDirectory()

    def runPwd(self):
        self.outdir.setText(str(os.getcwd()))
        self.useOutdir.setCheckState(QtCore.Qt.Unchecked)
        self.setWorkingDirectory()

    def setWorkingDirectory(self):
        if os.path.isdir(self.outdir.text()):
            os.chdir(self.outdir.text())
            self.output.setText("Output directory changed to %s\n" % (self.outdir.text()))
        else:
            self.output.setText("Output directory does not exist\n")

    def run_generate_cal_script(self):
        self.run_command_qprocess('generate_cal_script.py', use_kroot=True)

    def run_generate_cal_files(self):
        self.run_command_qprocess('generate_cal_files.csh', use_kroot=False, csh=True)

    def run_calibrations(self):
        if self.caltype == 'all':
            script = 'all_calibrations.csh'
        elif self.caltype == 'internal':
            script = 'nodome_calibrations.csh'
        elif self.caltype == 'dome':
            script = 'dome_calibrations.csh'

        self.run_command_qprocess(script, use_kroot=False, csh=True)






if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
