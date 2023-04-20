from re import M
import sys, os
from PyQt5 import uic # load GUI file
from matplotlib.figure import Figure # Create figure on window

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import numpy as np
import tifffile

uipath = "./tomocube"
version = 1.01
print(os.getcwd())
# UIfile load
form_class = uic.loadUiType(uipath+"/gui_discriminator.ui")[0]


class MainClass(QMainWindow, form_class):
    def __init__(self) :
        super().__init__()
    # ready 
        self.setupUi(self)
    # show screen
        self.setWindowTitle("BV discriminator ver."+str(version))
        self.setWindowIcon(QIcon(uipath+"/icon.png"))
        self.show()

    # Parameter
        self.loaded_folderpath = None
        self.processed_folderpath = None
        self.selected_oriname = None
        self.selected_proname = None
        self.match_dic = None
        self.showimg = np.zeros([512,512])
        self.sli = 0
        self.time = 0

    # Mpl set
    # Put layout in Mpl_widget (vertical)
        self.hbox = QHBoxLayout(self.mpl_widget)
    # Creat canvas
        self.figure = Figure(figsize=(80,80),tight_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.addToolBar(NavigationToolbar(self.canvas, self))

    # Put canvas in layout
        self.hbox.addWidget(self.canvas)

        self.axes = self.figure.subplots(1,1)
        self.plot_img = self.axes.imshow(self.showimg,vmin=13000, vmax=14000)

    # Slider
        self.time_slider.valueChanged[int].connect(self.tchange)
        self.time_slider.setRange(0,0)

        self.sli_slider.valueChanged[int].connect(self.zchange)
        self.sli_slider.setRange(0,0)
        # Minimum bright_slider of original image
        self.minbright_slider.valueChanged[int].connect(self.thrbright)
        self.minbright_slider.setRange(0,0)
        # Maximum bright_slider of original image
        self.maxbright_slider.valueChanged[int].connect(self.thrbright)
        self.maxbright_slider.setRange(0,0)
        
    # Button
        self.load_button.clicked.connect(self.loadpath)



    def thrbright(self):
        img = self.showimg
        pass_im = img*(img<self.maxbright_slider.value())
        result = pass_im*(img>self.minbright_slider.value())
        self.plot_img.set_data(result)
        self.canvas.draw_idle()

    def tchange(self,t):
        self.showimg = self.img[t,self.sli_sbox.value(),:,:]
        # same as thrbright
        img = self.showimg
        pass_im = img*(img<self.maxbright_slider.value())
        result = pass_im*(img>self.minbright_slider.value())

        self.plot_img.set_data(result)
        self.canvas.draw_idle()

    def zchange(self,z):
        self.showimg = self.img[self.time_sbox.value(),z,:,:]
        # same as thrbright
        img = self.showimg
        pass_im = img*(img<self.maxbright_slider.value())
        result = pass_im*(img>self.minbright_slider.value())

        self.plot_img.set_data(result)
        self.canvas.draw_idle()
  

    def loadpath(self):
        self.loaded_folderpath = QFileDialog.getExistingDirectory(self, 'original location')
        self.oripath_label.setText("Original path:"+self.loaded_folderpath) # Set text
                
        loaded_filelist = os.listdir(self.loaded_folderpath)
        print(loaded_filelist)

        self.file_table.setColumnCount(1)
        self.file_table.setRowCount(len(loaded_filelist)) # set number of Row as number of file in original
        self.file_table.setHorizontalHeaderLabels(["Loaded item"])

        for i in range(len(loaded_filelist)):
            self.file_table.setItem(i,0,QTableWidgetItem(loaded_filelist[i][-10:]))
        self.file_table.setHorizontalHeaderLabels(["Loaded item"])

        image_emptylist = []
        for file_t in loaded_filelist:
            loading = tifffile.imread(self.loaded_folderpath+'/'+file_t)
            image_emptylist.append(loading)
        
        self.img = np.asarray(image_emptylist)
 
     # Set control parameter
        # t axis parameter 
        self.tmax = self.img.shape[0]
        self.time_sbox.setMaximum(self.tmax-1)
        self.time_slider.setMaximum(self.tmax-1)
        # z axis parameter 
        self.zmax = self.img.shape[1]
        self.sli_sbox.setMaximum(self.zmax-1)
        self.sli_slider.setMaximum(self.zmax-1)
        # Max brightness parameter and activate slider and sbox``
        maxintensity = np.amax(self.img)
        minintensity = np.amin(self.img)
        self.minbright_slider.setRange(minintensity,maxintensity), self.minbright_sbox.setRange(minintensity,maxintensity)
        self.maxbright_slider.setRange(minintensity,maxintensity), self.maxbright_sbox.setRange(minintensity,maxintensity),self.maxbright_sbox.setValue(maxintensity)
        self.plot_img = self.axes.imshow(self.showimg,vmin=minintensity, vmax=maxintensity)

        
    # Initialize matplotlib
        self.time_sbox.setValue(self.time)
        self.sli_sbox.setValue(self.sli)
        self.showimg = self.img[self.time,self.sli,:,:]
        self.plot_img.set_data(self.showimg)
        self.canvas.draw_idle()
        print(self.showimg.shape,self.showimg[10:110,10:110])
        
   

if __name__ == "__main__" :
    app = QApplication(sys.argv) 
    window = MainClass() 
    app.exec_()