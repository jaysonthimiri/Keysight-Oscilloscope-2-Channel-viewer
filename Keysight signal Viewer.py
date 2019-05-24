import sys
from PyQt4.QtGui import *
import fileinput
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

def isDigit(x):
    for y in x:
        try:
            float(y)
        except ValueError:
            return False
    return True

class Window(QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.tryError=0
        
        self.signal={1:{'Rise':None, 'Fall':None, 'DigVal':1},
                     2:{'Rise1':None, 'Fall':None,'Rise2':None, 'DigVal':0, 'Period':None, 'OnTime':None}}

        self.MainData={}
        #self.Create_ReportForm()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.bBrowse = QPushButton(text=u"Browse")
        self.bBrowse.clicked.connect(self.Browse)

        self.LInFile = QLabel('Browse your input csv file')
        self.LInFile.setFixedWidth(600)

        self.cbChannelInterchange = QCheckBox("Channel Interchange")
        self.cbChannelInterchange.setChecked(False)

        self.bPlot = QPushButton(text=u"Plot")
        self.bPlot.clicked.connect(self.Plot)

        self.cbDebugMode = QCheckBox("Debug Mode")
        self.cbDebugMode.setChecked(False)

        self.bAbout = QPushButton(text=u"About")
        self.bAbout.clicked.connect(self.About)
        
        self.LOutput = QLabel()
        self.LOutput.setFixedWidth(600)
        
        layout = QGridLayout()
        layout.addWidget(self.LInFile,0,0)
        layout.addWidget(self.bBrowse,0,1)
        #layout.addWidget(self.ReportForm,0,3,5,1)
        layout.addWidget(self.bPlot,1,1)
        layout.addWidget(self.cbChannelInterchange,1,0)
        layout.addWidget(self.toolbar,2,0,1,2)
        layout.addWidget(self.LOutput,3,0,1,2)
        layout.addWidget(self.canvas,5,0,1,4)
        layout.addWidget(self.cbDebugMode,7,0)
        layout.addWidget(self.bAbout,7,3)

        self.setLayout(layout)
        
    # def Create_ReportForm(self):
    #     self.ReportForm = QGroupBox("Report")
    #     self.ReportForm.setFixedWidth(210)
    #     layout = QFormLayout()
    #     self.LVOL=QLineEdit('1.2')
    #     self.LVOL.setFixedWidth(40)
    #     self.LVOH=QLineEdit('3.0')
    #     self.LVOH.setFixedWidth(40)
    #     self.LExpChange=QLineEdit('2')
    #     self.LExpChange.setFixedWidth(40)
    #     self.bReport = QPushButton(text=u"Generate")
    #     self.bReport.clicked.connect(self.Report)
    #
    #     layout.addRow(QLabel("VOL (V)"),self.LVOL)
    #     layout.addRow(QLabel("VOH (V)"),self.LVOH)
    #     layout.addRow(QLabel("Expected OnTime Change (mS)"),self.LExpChange)
    #     layout.addRow(self.bReport)
    #
    #     self.ReportForm.setLayout(layout)
        
    def Plot(self):
        self.figure.clf()
        ax1,ax2= self.figure.subplots(2, 1, sharex=True)
        self.x_axis=[]
        self.y_axis_S1=[]
        self.y_axis_S2=[]
        
        try:
            for line in fileinput.input(self.InputFile):
                line=line.rstrip()
                line_list=line.split(',')
                if len(line_list)>2 and isDigit(line_list):
                    self.x_axis.append(float(line_list[0]))
                    if self.cbChannelInterchange.isChecked():
                        self.y_axis_S1.append(float(line_list[1]))
                        self.y_axis_S2.append(float(line_list[2]))
                    else:
                        self.y_axis_S2.append(float(line_list[1]))
                        self.y_axis_S1.append(float(line_list[2]))
        except:
            self.File_Input_Error()
            self.tryError+=1
            if self.tryError < 4:self.Plot()
            else:exit()

        self.tryError=0    
        ax1.plot(self.x_axis,self.y_axis_S1,'g')
        ax1.set_ylabel('Signal_1')

        ax2.plot(self.x_axis, self.y_axis_S2,'b')
        ax2.set_ylabel('Signal_2')

        ax2.set_xlabel('Time(S)')
        # refresh canvas
        self.canvas.draw()
        
    def File_Input_Error(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error: Invalid input file.")
        msg.setWindowTitle("Invalid input")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.buttonClicked.connect(self.Browse)
        retval = msg.exec_()
        
        
    def Browse(self):
        ''' plot some random stuff '''
        self.InputFile = str(QFileDialog.getOpenFileName(None, "Select your input csv", "", "CSV files (*.csv)"))
        self.LInFile.setText(self.InputFile)
        
    def Report(self):
        S1_Count=0
        Search_For_PWM_Change=False
        for i in range(len(self.x_axis)):
            try:
                VOL = float(self.LVOL.text())
                VOH = float(self.LVOH.text())
                ExpCh = float(self.LExpChange.text())
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error: Invalid VOL/VOH data.\nVOL :" + self.lVOH.text() + '\nVOH :' + self.LVOH.text() + '\nETC :'+self.LExpChange.text())
                msg.setWindowTitle("Invalid input")
                msg.setStandardButtons(QMessageBox.Ok)
                retval = msg.exec_()
                return
                
            ######## Signal 2 Processing...  ##########
            if self.y_axis_S2[i]>VOH and self.signal[2]['DigVal'] is 0 and self.signal[2]['Rise1'] is None:
                self.signal[2]['Rise1']=self.x_axis[i]
                self.signal[2]['DigVal']=1
                
            elif self.y_axis_S2[i]<VOL and self.signal[2]['DigVal'] is 1 and self.signal[2]['Rise1'] is not None and self.signal[2]['Fall'] is None:
                self.signal[2]['Fall']=self.x_axis[i]
                self.signal[2]['DigVal']=0
                self.signal[2]['OnTime']=self.signal[2]['Fall']-self.signal[2]['Rise1']
                
                ######## Finding PWM Change...  ##########
                if Search_For_PWM_Change is True:
                    if abs(self.signal[2]['OnTime'] - self.MainData[S1_Count]['S2_OnTime_B4_S1']) > (ExpCh/1000):
                        self.MainData[S1_Count]['PWM_ChangeAt']=self.x_axis[i]
                        self.MainData[S1_Count]['S2_Period_at_PWM_Change']=self.signal[2]['Period']
                        self.MainData[S1_Count]['S2_OnTime_at_PWM_Change']=self.signal[2]['OnTime']
                        Search_For_PWM_Change=False
        
            elif self.y_axis_S2[i]>VOH and self.signal[2]['DigVal'] is 0 and self.signal[2]['Rise1'] is not None and self.signal[2]['Fall'] is not None and self.signal[2]['Rise2'] is None:
                self.signal[2]['Rise2']=self.x_axis[i]
                self.signal[2]['DigVal']=1
                self.signal[2]['Period']=self.signal[2]['Rise2']-self.signal[2]['Rise1']
                
                self.signal[2]['Rise1']=self.signal[2]['Rise2']
                self.signal[2]['Fall']=None
                self.signal[2]['Rise2']=None
               
                
                
            ######## Signal 1 Processing...  ##########
            if self.y_axis_S1[i]<VOL and self.signal[1]['DigVal'] is 1 and self.signal[1]['Fall'] is None:
                self.signal[1]['Fall']=self.x_axis[i]
                self.signal[1]['DigVal']=0
                
            elif self.y_axis_S1[i]>VOH and self.signal[1]['DigVal'] is 0 and self.signal[1]['Rise'] is None and self.signal[1]['Fall'] is not None :
                self.signal[1]['Rise']=self.x_axis[i]
                self.signal[1]['DigVal']=1
                S1_Count+=1
                self.MainData.update({S1_Count:{'S2_Period_B4_S1':self.signal[2]['Period'],
                                               'S2_OnTime_B4_S1':self.signal[2]['OnTime'],
                                               'S1_RiseAt':self.signal[1]['Rise'],
                                               'S1_OffTime':self.signal[1]['Rise']-self.signal[1]['Fall'],
                                               'S2_Period_at_PWM_Change':None,
                                               'S2_OnTime_at_PWM_Change':None,
                                               'PWM_ChangeAt':None}})
                Search_For_PWM_Change=True
                self.signal[1]['Rise']=None
                self.signal[1]['Fall']=None
        OutFile = open('OutPut.csv','w+')
        OutFile.write('Signal 1 count,Signal 1 rise at(S),PWM Period before Signal 1(S),PWM Ontime before Signal 1(S),PWM Period at DutyCycle Change(S),PWM Ontime at DutyCycle Change(S),Signal 1 Offtime(S),Signal 1 to PWM change time(S)\n')
        Min = 99999999
        Max = 0
        for x in self.MainData.keys():
            OutFile.write(str(x) + ',' + \
                          str(self.MainData[x]['S1_RiseAt']) + ',' +  \
                          str(self.MainData[x]['S2_Period_B4_S1']) + ',' +  \
                          str(self.MainData[x]['S2_OnTime_B4_S1']) + ',' +  \
                          str(self.MainData[x]['S2_Period_at_PWM_Change']) + ',' +  \
                          str(self.MainData[x]['S2_OnTime_at_PWM_Change']) + ',' + \
                          str(self.MainData[x]['S1_OffTime']) + ',' + \
                          str(self.MainData[x]['PWM_ChangeAt']) + '\n')
            if self.MainData[x]['PWM_ChangeAt'] is not None:
                if self.MainData[x]['PWM_ChangeAt'] < Min: Min=self.MainData[x]['PWM_ChangeAt']
                if self.MainData[x]['PWM_ChangeAt'] > Max: Max=self.MainData[x]['PWM_ChangeAt']
                
        self.LOutput.setText("Minimun time to change dutycycle is : " +str(Min) +"\nMaximun time to change dutycycle is : " +str(Max))
         
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Output.csv Created!!!\nMinimun time to change dutycycle is : " +str(Min) +"\nMaximun time to change dutycycle is : " +str(Max))
        msg.setWindowTitle("Done")
        msg.setStandardButtons(QMessageBox.Ok)
        retval = msg.exec_()       
                
                
    def About(self):               
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("#-------------------------------------------------------------------------------\n \
# Name\t\t: Keysight signal viewer\n \
# Revision\t\t: 2.0\n \
# Purpose\t\t: To view the csv signals generted from Keysight oscillocope\n \
# \n \
# Author\t\t: Jayson Mathew\n \
# Contact\t\t: jaysonthmiri@gmail.com\n \
# Created\t\t: 15/3/2019\n \
#-------------------------------------------------------------------------------\n \
")
        msg.setWindowTitle("WaveViewer & PWM Excel Auto Tool")
        msg.setStandardButtons(QMessageBox.Close)
        retval = msg.exec_()
            
                
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Window()
    main.setWindowTitle("Keysight signal viewer")
    main.show()

    sys.exit(app.exec_())
