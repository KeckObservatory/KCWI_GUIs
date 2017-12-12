import sys,os
import subprocess
from PyQt5.QtWidgets import QCheckBox,QRadioButton,QLabel,QHBoxLayout,QLineEdit,QPushButton,QVBoxLayout,QApplication,QAction,qApp,QWidget, QTextEdit



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

    def init_ui(self):
        # create objects
        #self.lbl = QLabel('Offsetig mode')
        #self.en = QRadioButton('East-North (arcseconds')
        #self.xy = QRadioButton('Magiq coordinates (arcseconds)')
        #self.xyp = QRadioButton('Magiq coordinates (pixels)')
        #self.sl = QRadioButton('Slicer (slices)')
        # layout for radio buttons
        #v1_layout = QVBoxLayout()
        #v1_layout.addWidget(self.en)
        #v1_layout.addWidget(self.xy)
        #v1_layout.addWidget(self.xyp)
        #v1_layout.addWidget(self.sl)

        # value of offset
        self.lbl1 = QLabel('Value')
        self.value = QLineEdit()
        self.value.setText('1')
        self.lbl5 = QLabel('positive value, arcseconds or slices')
        h1_layout = QHBoxLayout()
        h1_layout.addWidget(self.lbl1)
        h1_layout.addWidget(self.value)
        h1_layout.addWidget(self.lbl5)

        # direction of offset
        self.lbl2 = QLabel('Move object in guider')
        self.up = QPushButton('Up')
        self.down = QPushButton('Down')
        self.left = QPushButton('Left')
        self.right = QPushButton('Right')

        h2_layout = QHBoxLayout()
        h2_layout.addWidget(self.lbl2)
        h2_layout.addWidget(self.up)
        h2_layout.addWidget(self.down)
        h2_layout.addWidget(self.left)
        h2_layout.addWidget(self.right)

        # direction of offset
        self.lbl3 = QLabel('Move telescope')
        self.e = QPushButton('E')
        self.w = QPushButton('W')
        self.n = QPushButton('N')
        self.s = QPushButton('S')

        h3_layout = QHBoxLayout()
        h3_layout.addWidget(self.lbl3)
        h3_layout.addWidget(self.e)
        h3_layout.addWidget(self.w)
        h3_layout.addWidget(self.n)
        h3_layout.addWidget(self.s)

        # direction of offset
        self.lbl4 = QLabel('Move object across slicer')
        self.sliceleft = QPushButton('Slice Left')
        self.sliceright = QPushButton('Slice Right')
        h4_layout = QHBoxLayout()
        h4_layout.addWidget(self.lbl4)
        h4_layout.addWidget(self.sliceleft)
        h4_layout.addWidget(self.sliceright)


        self.te = QTextEdit()
        self.take_guider = QCheckBox('Take guider image after move')
        # layout
        v_layout = QVBoxLayout(self)
        #v_layout.addLayout(v1_layout)
        v_layout.addLayout(h1_layout)
        v_layout.addLayout(h2_layout)
        v_layout.addLayout(h3_layout)
        v_layout.addLayout(h4_layout)
        v_layout.addWidget(self.te)
        v_layout.addWidget(self.take_guider)

        self.setLayout(v_layout)

        # associate action
        buttons = [self.up, self.down, self.right, self.left, self.e, self.w, self.s, self.n, self.sliceleft, self.sliceright]
        for button in buttons:
                button.clicked.connect(self.btn_click)

    def run_command(self, command):
        try:
            kroot = os.environ['KROOT']
        except:
            kroot = ''
        cmdline = os.path.join(kroot,'rel','default','bin',command)
        if self.runMode is not 'debug':
            p = subprocess.Popen(cmdline, stdout = subprocess.PIPE,stderr = subprocess.PIPE, shell=True)
            output, errors = p.communicate()
            self.te.setText(str(output))
        else:
            self.te.setText(str(cmdline))

    def btn_click(self):
        sender = self.sender()
        value = self.value.text()

        if sender.text() == 'Up':
            command = '%s 0 -%f' % ('gxy', float(value))
        elif sender.text() == 'Down':
            command = '%s 0 %f' % ('gxy', float(value))
        elif sender.text() == 'Left':
            command = '%s %f 0' % ('gxy', float(value))
        elif sender.text() == 'Right':
            command = '%s -%f 0' % ('gxy', float(value))
        elif sender.text() == 'E':
            command = '%s %f 0' % ('en', float(value))
        elif sender.text() == 'W':
            command = '%s -%f 0' % ('en', float(value))
        elif sender.text() == 'N':
            command = '%s 0 %f' % ('en', float(value))
        elif sender.text() == 'S':
            command = '%s 0 -%f' % ('en', float(value))
        elif sender.text() == 'Slice Left':
            command = '%s left %f' % ('moveSlicer',float(value))
        elif sender.text() == 'Slice Right':
            command = '%s right %f' % ('moveSlicer',float(value))
        else:
            command = None

        if command is not None:
            self.run_command(command)

        if self.take_guider.isChecked():
            self.run_command('saveGuiderImageLocal')



if __name__ == "__main__":
    main()
