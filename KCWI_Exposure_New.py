import sys,os
import subprocess
from PyQt5.QtWidgets import QFrame, QLabel,QHBoxLayout,QLineEdit,QPushButton,QVBoxLayout,QApplication,QCheckBox, QTextEdit, QWidget
from PyQt5 import QtCore



def main():
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())

class separator(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setLineWidth(3)

class MyWindow(QWidget):
    def __init__(self, *args):
        super().__init__()
        #self.runMode = 'debug'
        self.runMode = ''
        self.init_ui()
        self.setWindowTitle("KCWI Exposure Control")

    def init_ui(self):
        # create objects
        # labels
        self.lbl1 = QLabel('Exptime')
        self.lbl2 = QLabel('Number of exp.')
        h1_layout = QHBoxLayout()
        h1_layout.addWidget(self.lbl1)
        h1_layout.addWidget(self.lbl2)
        # entry fields
        self.exptime = QLineEdit()
        self.nexp = QLineEdit()
        h2_layout = QHBoxLayout()
        h2_layout.addWidget(self.exptime)
        h2_layout.addWidget(self.nexp)
        # set defaults
        self.exptime.setText('1')
        self.nexp.setText('1')
        # update the exposure time
        self.update_exptime = QPushButton('Apply/Update')
        self.separator1 = separator()

        # buttons
        self.science = QPushButton('Science exposure')
        self.twiflat = QPushButton('Twilight flat')
        self.bias = QPushButton('Bias')
        self.dark = QPushButton('Dark')
        self.fpc = QPushButton('FPC exposure')
        #self.pb = QPushButton(self.tr('Save Guider Image'))
        self.te = QTextEdit()
        self.test_mode = QCheckBox('Test mode (show command, no action)')

        # layout
        v_layout = QVBoxLayout(self)
        v_layout.addLayout(h1_layout)
        v_layout.addLayout(h2_layout)
        v_layout.addWidget(self.update_exptime)
        v_layout.addWidget(self.separator1)
        v_layout.addWidget(self.science)
        v_layout.addWidget(self.twiflat)
        v_layout.addWidget(self.bias)
        v_layout.addWidget(self.dark)
        v_layout.addWidget(self.fpc)
        #v_layout.addWidget(self.pb)
        v_layout.addWidget(self.te)
        v_layout.addWidget(self.test_mode)
        self.setLayout(v_layout)

        # create button connection
        buttons = [self.science,self.twiflat,self.bias,self.dark,self.fpc]
        for button in buttons:
            button.clicked.connect(self.btn_click)

        self.update_exptime.clicked.connect(self.change_exptime)

    def change_exptime(self):
        exptime = self.exptime.text()
        try:
            kroot = os.environ['KROOT']
        except:
            kroot = ""
        if exptime:
            cmdline = os.path.join(kroot, 'rel', 'default', 'bin', 'tintb %d' % float(exptime))
            if self.runMode is not 'debug':
                p = subprocess.Popen(cmdline, stdout = subprocess.PIPE,stderr = subprocess.PIPE, shell=True)
                output, errors = p.communicate()
                if len(errors) > 0:
                    output = output + errors
                self.te.setText(str(output.decode()))
            else:
                self.te.setText(str(cmdline))

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

    def onFinished(self, exitCode, exitStatus):
        print("Process finished")
        self.showOutput("Exit code: %d\n" % exitCode)
        self.showOutput("Exit status: %s\n" % exitStatus)

    def onStart(self):
        print("Process started")

    def launchError(self, error):
        if error != QtCore.QProcess.Crashed:
            self.showOutput("Warning! There was a problem running the requested function.")

    def run_command(self,command, command_arguments=[], use_kroot=False, csh=False):
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

    # def run_command(self,command):
    #     try:
    #         kroot = os.environ['KROOT']
    #     except:
    #         kroot = ''
    #     cmdline = os.path.join(kroot,'rel','default','bin',command)
    #     if self.test_mode.isChecked():
    #         self.runMode = 'debug'
    #     else:
    #         self.runMode = 'normal'
    #     if self.runMode is not 'debug':
    #         p = subprocess.Popen(cmdline, stdout = subprocess.PIPE,stderr = subprocess.PIPE, shell=True)
    #         output, errors = p.communicate()
    #         if len(errors) > 0:
    #             output = output + errors
    #         self.te.setText(str(output.decode()))
    #     else:
    #         self.te.setText(str(cmdline))

    def btn_click(self):
        exptime = self.exptime.text()
        nexp = self.nexp.text()
        sender = self.sender()
        if sender.text() == 'Science exposure':
            commands = [['imtype',['OBJECT']], ['tintb',[float(exptime)]], ['goib', [int(nexp)]]]
        elif sender.text() == 'Twilight flat':
            commands = [['tintb', [float(exptime)]],['imtype',['TWIFLAT']], ['goib', [int(nexp)]]]
        elif sender.text() == 'Bias':
            commands = [['tintb', [0]], ['goib',[int(nexp)]]]
        elif sender.text() == 'Dark':
            commands = [['imtype', ['DARK']], ['tintb',[float(exptime)]], ['goib',['-dark',int(nexp)]]]
        elif sender.text() == 'FPC exposure':
            commands = [['goifpc']]
        #elif sender.text() == 'Save Guider Image':
        #    command = 'saveGuiderImageLocal'
        else:
            command = None

        if commands is not None:
            for command in commands:
                program = command[0]
                arguments = command[1]
            self.run_command(program, arguments)



if __name__ == "__main__":
    main()
