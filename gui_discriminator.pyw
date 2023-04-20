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

uipath = "./discriminator"
version = 1.01
print(os.getcwd())
# UIfile load
form_class = uic.loadUiType(uipath+"/gui_discriminator.ui")[0]

def match_todic(original_folderpath,processed_folderpath):
    original_filelist = os.listdir(original_folderpath)
    processed_filelist = os.listdir(processed_folderpath)
    print(original_filelist)
    print(processed_filelist)
    match_dic = {original_file:processed_file for original_file in original_filelist for processed_file in processed_filelist if original_file[-9:] == processed_file[-9:] }
    return match_dic

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
        self.original_folderpath = None
        self.processed_folderpath = None
        self.selected_oriname = None
        self.selected_proname = None
        self.match_dic = None
        self.bvimg = np.zeros([512,512])
        self.sli = 12

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
        self.plot_original = self.axes.imshow(self.bvimg,cmap='Reds',alpha=0.5, vmin=0, vmax=4095)
        self.plot_processed = self.axes.imshow(self.bvimg,cmap='Greens',alpha=0.5, vmin=0, vmax=4095)
    # Slider
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
        self.good_button.clicked.connect(self.goodstat)
        self.bad_button.clicked.connect(self.badstat)
        self.discard_button.clicked.connect(self.discardstat)

    # Table setting
        self.file_table.cellClicked.connect(self.loadimg)
    
    def goodstat(self):
        os.rename(self.original_folderpath+"/"+self.selected_oriname, self.original_folderpath+"/g"+self.selected_oriname[-9:]) #rename original file
        # if recover data
        if not os.path.exists(self.processed_folderpath+'/'+self.selected_proname):
            tifffile.imsave(self.processed_folderpath+'/'+self.selected_proname,self.processed)
            print("file_recovered")
        # update table
        match_dic = match_todic(self.original_folderpath,self.processed_folderpath)
        original_filelist = list(match_dic.keys())
        for i in range(len(original_filelist)):
            self.file_table.setItem(i,0,QTableWidgetItem(original_filelist[i]))
            self.file_table.setItem(i,1,QTableWidgetItem(match_dic.get(original_filelist[i])))
        print("status: good")
            
    def badstat(self):
        # rename original file and remove processed file
        os.rename(self.original_folderpath+"/"+self.selected_oriname, self.original_folderpath+"/b"+self.selected_oriname[-9:])
        os.remove(self.processed_folderpath+'/'+self.selected_proname)
        # update table
        match_dic = match_todic(self.original_folderpath,self.processed_folderpath)
        original_filelist = list(match_dic.keys())
        for i in range(len(original_filelist)):
            self.file_table.setItem(i,0,QTableWidgetItem(original_filelist[i]))
            self.file_table.setItem(i,1,QTableWidgetItem(match_dic.get(original_filelist[i])))
        print("status: bad")
        
    def discardstat(self):
        # rename original file and remove processed file
        os.rename(self.original_folderpath+"/"+self.selected_oriname, self.original_folderpath+"/d"+self.selected_oriname[-9:])
        os.remove(self.processed_folderpath+'/'+self.selected_proname)
        # update table
        match_dic = match_todic(self.original_folderpath,self.processed_folderpath)
        original_filelist = list(match_dic.keys())
        for i in range(len(original_filelist)):
            self.file_table.setItem(i,0,QTableWidgetItem(original_filelist[i]))
            self.file_table.setItem(i,1,QTableWidgetItem(match_dic.get(original_filelist[i])))
        print("status: discard")
            
    def loadimg(self):
        row = self.file_table.selectedItems()
        self.selected_oriname , self.selected_proname = row[0].text(),row[1].text()
        original_path = self.original_folderpath+'/'+ self.selected_oriname
        processed_path = self.processed_folderpath+'/'+self.selected_proname

        original = tifffile.imread(original_path)
    # Channel selection
        self.bvim = original[:,0,:,:]
        self.processed = tifffile.imread(processed_path)
    # Set control parameter
        # z axis parameter 
        self.zmax = self.bvim.shape[0]
        self.sli_sbox.setMaximum(self.zmax-1)
        self.sli_slider.setMaximum(self.zmax-1)
        # Max brightness parameter and activate slider and sbox``
        maxintensity = np.amax(self.bvim)
        self.minbright_slider.setRange(0,maxintensity), self.minbright_sbox.setRange(0,maxintensity)
        self.maxbright_slider.setRange(0,maxintensity), self.maxbright_sbox.setRange(0,maxintensity),self.maxbright_sbox.setValue(maxintensity)
    # Initialize matplotlib
        self.surf_im = np.zeros(self.bvim.shape)
        self.sli_sbox.setValue(self.sli)
        self.bvimg = self.bvim[self.sli,:,:]
        self.plot_original.set_data(self.bvimg)
        self.canvas.draw_idle()

    def thrbright(self):
        img = self.bvimg
        max = (img>self.maxbright_slider.value()-1)*4095
        pass_im = max+img*(img<self.maxbright_slider.value())
        result = pass_im*(img>self.minbright_slider.value())
        self.plot_original.set_data(result)
        self.canvas.draw_idle()



    def zchange(self,z):
        self.bvimg = self.bvim[z,:,:]
        # same as thrbright
        img = self.bvimg
        max = (img>self.maxbright_slider.value()-1)*4095
        pass_im = max+img*(img<self.maxbright_slider.value())
        result = pass_im*(img>self.minbright_slider.value())

        result2 = (self.processed[z,:,:]>0)*2000
        self.plot_original.set_data(result)
        self.plot_processed.set_data(result2)
        self.canvas.draw_idle()
  

    def loadpath(self):
        self.original_folderpath = QFileDialog.getExistingDirectory(self, 'original location')
        self.oripath_label.setText("Original path:"+self.original_folderpath) # Set text
        
        self.processed_folderpath = QFileDialog.getExistingDirectory(self, 'processed location')
        self.propath_label.setText("Processed path:"+self.processed_folderpath) # Set text

        
        match_dic = match_todic(self.original_folderpath,self.processed_folderpath)
        original_filelist = list(match_dic.keys())
        self.file_table.setColumnCount(2)
        self.file_table.setRowCount(len(original_filelist)) # set number of Row as number of file in original
        self.file_table.setHorizontalHeaderLabels(["Orignal item", "Processed item"])

        for i in range(len(original_filelist)):
            self.file_table.setItem(i,0,QTableWidgetItem(original_filelist[i]))
            self.file_table.setItem(i,1,QTableWidgetItem(match_dic.get(original_filelist[i])))

    

if __name__ == "__main__" :
    app = QApplication(sys.argv) 
    window = MainClass() 
    app.exec_()