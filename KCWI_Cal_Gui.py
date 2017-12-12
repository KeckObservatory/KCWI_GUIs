import sys, os, subprocess
from PyQt5.QtWidgets import QWidget, QHBoxLayout,QTableWidget, QTableWidgetItem, QVBoxLayout, QRadioButton
from PyQt5.QtWidgets import QPushButton, QCheckBox, QLineEdit, QLabel, QApplication, QTextEdit
from pymongo import MongoClient
from PyQt5 import QtCore
from ConfigManager import save_state

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
        self.save = QPushButton('Save states to disk')
        self.genfiles = QPushButton('1 - Generate calibration scripts')
        self.gencals = QPushButton('2 - Generate calibration flat files')

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

        self.runcals = QPushButton('3 - Run cals')

        buttons = [self.reload,self.list,self.save, self.gencals, self.genfiles, self.runcals]
        for button in buttons:
                button.setFixedWidth(buttonSize)
        self.program.textChanged.connect(self.set_program)
        self.reload.clicked.connect(self.refresh_data)
        self.list.clicked.connect(self.ListConfigs)
        self.save.clicked.connect(self.saveStates)
        self.genfiles.clicked.connect(self.run_generate_cal_script)
        self.gencals.clicked.connect(self.run_generate_cal_files)
        self.runcals.clicked.connect(self.run_calibrations)

        self.layout = QVBoxLayout()
        self.layout.addLayout(self.hlayout1)
        self.layout.addWidget(self.tableWidget)

        self.vlayout1 = QVBoxLayout()
        self.vlayout1.addWidget(self.list)
        self.vlayout1.addWidget(self.save)
        self.vlayout1.addWidget(self.reload)
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
        self.output.setText(str(output))

    def on_radio_button_toggled(self):
        radiobutton = self.sender()

        if radiobutton.isChecked():
            print("Selected mode is %s" % (radiobutton.caltype))
        self.caltype = radiobutton.caltype

    def run_command(self,command):
        try:
            kroot = os.environ['KROOT']
        except:
            kroot = ''
        cmdline = os.path.join(kroot, 'rel', 'default', 'bin', command)

        if self.runMode is 'debug':
            self.output.setText('Simulation mode\n Running:\n %s' % (cmdline))
            return '',''
        try:
            p = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, errors = p.communicate()
        except RuntimeError:
            output = ''
            errors = 'Cannot execute command %s' % command
        except FileNotFoundError:
            output = ''
            errors = 'The command does not exist'
        self.output.setText('')
        for line in output.decode().split('\n'):
            self.output.append(str(line))
        #self.output.setText(str(output.decode()))
        if errors:
            self.output.setText(str(errors))

        return output, errors

    def run_local(self,command):
        cmdline = os.path.join(self.outdir.text(), command)
        if self.runMode is 'debug':
            self.output.setText('Simulation mode\n Running:\n %s' % (cmdline))
            return '',''
        try:
            p = subprocess.Popen(['csh',cmdline], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, errors = p.communicate()
        except RuntimeError:
            output = ''
            errors = 'Cannot execute command %s' % command
        except FileNotFoundError:
            output = ''
            errors = 'The command (%s) does not exist' % (cmdline)
        self.output.setText('')
        for line in output.decode().split('\n'):
            self.output.append(str(line))
        #self.output.setText(str(output.decode()))
        if errors:
            for line in errors.decode().split('\n'):
                self.output.append(str(errors))

        return output, errors


    def runOutdir(self):
        output, errors = self.run_command('outdir')
        self.usePwd.setCheckState(QtCore.Qt.Unchecked)
        self.outdir.setText(str(output.decode().replace('\n','')))
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
        output, errors = self.run_command('generate_cal_script.py')
        #if output != '':
        #    self.output.setText(str(output))

    def run_generate_cal_files(self):
        output, errors = self.run_local('generate_cal_files.csh')
        #if output != '':
        #    self.output.setText(str(output))

    def run_calibrations(self):
        if self.caltype == 'all':
            script = 'all_calibrations.csh'
        elif self.caltype == 'internal':
            script = 'nodome_calibrations.csh'
        elif self.caltype == 'dome':
            script = 'dome_calibrations.csh'

        output, errors = self.run_local(script)
        #if output != '':
        #    self.output.setText(str(output))





if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
