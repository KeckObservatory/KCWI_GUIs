import sys,os
import subprocess
from PyQt5.QtWidgets import QLabel,QHBoxLayout,QLineEdit,QPushButton,QVBoxLayout,QApplication,QCheckBox, QTextEdit, QWidget



def main():
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())


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

        # buttons
        self.science = QPushButton('Science exposure')
        self.twiflat = QPushButton('Twilight flat')
        self.bias = QPushButton('Bias')
        self.dark = QPushButton('Dark')
        self.fpc = QPushButton('FPC exposure')
        self.pb = QPushButton(self.tr('Save Guider Image'))
        self.te = QTextEdit()
        self.test_mode = QCheckBox('Test mode (show command, no action)')

        # layout
        v_layout = QVBoxLayout(self)
        v_layout.addLayout(h1_layout)
        v_layout.addLayout(h2_layout)
        v_layout.addWidget(self.science)
        v_layout.addWidget(self.twiflat)
        v_layout.addWidget(self.bias)
        v_layout.addWidget(self.dark)
        v_layout.addWidget(self.fpc)
        v_layout.addWidget(self.pb)
        v_layout.addWidget(self.te)
        v_layout.addWidget(self.test_mode)
        self.setLayout(v_layout)

        # create button connection
        buttons = [self.science,self.twiflat,self.bias,self.dark,self.fpc,self.pb]
        for button in buttons:
            button.clicked.connect(self.btn_click)

        self.exptime.textChanged.connect(self.change_exptime)

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

    def run_command(self,command):
        try:
            kroot = os.environ['KROOT']
        except:
            kroot = ''
        cmdline = os.path.join(kroot,'rel','default','bin',command)
        if self.test_mode.isChecked():
            self.runMode = 'debug'
        else:
            self.runMode = 'normal'
        if self.runMode is not 'debug':
            p = subprocess.Popen(cmdline, stdout = subprocess.PIPE,stderr = subprocess.PIPE, shell=True)
            output, errors = p.communicate()
            if len(errors) > 0:
                output = output + errors
            self.te.setText(str(output.decode()))
        else:
            self.te.setText(str(cmdline))

    def btn_click(self):
        exptime = self.exptime.text()
        nexp = self.nexp.text()
        sender = self.sender()
        if sender.text() == 'Science exposure':
            command = 'imtype OBJECT; tintb %f; goib %d' % (float(exptime),int(nexp))
        elif sender.text() == 'Twilight flat':
            command = 'tintb %f; imtype TWIFLAT; goib %d' % (float(exptime), int(nexp))
        elif sender.text() == 'Bias':
            command = 'tintb 0; goib %d' % int(nexp)
        elif sender.text() == 'Dark':
            command = 'imtype DARK; tintb %f; goib -dark %d' % (float(exptime), int(nexp))
        elif sender.text() == 'FPC exposure':
            command = 'goifpc'
        elif sender.text() == 'Save Guider Image':
            command = 'saveGuiderImageLocal'
        else:
            command = None

        if command is not None:
            self.run_command(command)



if __name__ == "__main__":
    main()
