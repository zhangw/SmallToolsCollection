# -*- coding: utf-8 -*-
"""
execute.py

使用PyQt,编写的跨平台客户端,用于查询Dell电脑质保期.

Created by <wen.zhang@wedoapp.com> on Aug 27,2013
"""

from get_machine_warranty import get_machine_warranty as gmw
from PyQt4 import QtCore, QtGui

'''
用于数据处理的Qt线程,定义了信号和UI进行消息传递
'''
class ThreadGetWarranty(QtCore.QThread):
    #注意信号变量的定义,在成员方法外
    dataok = QtCore.pyqtSignal(object,name='dataok')
    printlog = QtCore.pyqtSignal(object,name='printlog')

    def __init__(self,serials,savefileName):
        self.serials = serials
        self.savefile = savefileName
        super(ThreadGetWarranty,self).__init__()
    
    '''实现线程的执行'''
    def run(self):
        if len(self.serials) > 0:
            #use mutiple threads to get data from internet,and emit the corresponding singal.
            gmw.get_warranty_threads(self.serials,self.savefile,{'dataok':self.dataok,'log':self.printlog},threadsnum=15)
'''
GUI窗体的绘制,使用了Layout布局,包含文本框和进度条控件
'''
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        widget = QtGui.QWidget()
        self.setCentralWidget(widget)

        #QProgressBar
        self.createProgressBar()
                
        #QTextEditor
        self.createTextEditor()
        
        vbox = QtGui.QVBoxLayout()
        vbox.setMargin(5)
        vbox.addWidget(self.progressBarLayout)
        vbox.addWidget(self.logLayout)
        widget.setLayout(vbox)

        self.createActions()
        self.createMenus()

        message = "A tool used to get the warranty of dell computers in batches."
        self.statusBar().showMessage(message)

        self.setWindowTitle("Dells_Warranty_Tool")
        self.setMinimumSize(240,160)
        self.resize(480,320)
    
    def createProgressBar(self):
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.setRange(0,100)
        self.progressBar.setValue(0)
        self.progressBarLayout = QtGui.QGroupBox('Progress')
        layout = QtGui.QFormLayout()
        layout.addRow(self.progressBar)
        self.progressBarLayout.setLayout(layout)
    
    def createTextEditor(self):
        self.logText = QtGui.QTextEdit()
        self.logText.setReadOnly(True)
        self.logLayout = QtGui.QGroupBox('Log')
        layout = QtGui.QFormLayout()
        layout.addRow(self.logText)
        self.logLayout.setLayout(layout)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        menu.exec_(event.globalPos())
    
    '''导入包含电脑序列号的文件'''
    def open(self):
        options = QtGui.QFileDialog.Options()
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                "QFileDialog.getOpenFileName()",
                "",
                "Text Files (*.txt);;Csv Files (*.csv)", None, options)
        if fileName:
            self.serials = gmw.get_serials(fileName)
            if len(self.serials) > 0:
                self.isopen = True
                QtGui.QMessageBox.about(self,"Message","Please click <b>export</b> button to export data.")
            else:
                QtGui.QMessageBox.about(self,"Message","There's no avaliable data.")

    '''根据序列号查询数据,将数据存入硬盘'''    	
    def save(self):
        if hasattr(self,'isopen') and self.isopen:
            options = QtGui.QFileDialog.Options()
            fileName = QtGui.QFileDialog.getSaveFileName(self,
                    "QFileDialog.getSaveFileName()",
                    "",
                    "Text Files (*.txt);;Csv Files (*.csv)", None, options)
            if fileName:
                self.filesaved = fileName
                threadWarranty = ThreadGetWarranty(self.serials,fileName)
                threadWarranty.dataok.connect(self.handleProgressBar)
                threadWarranty.printlog.connect(self.handleTextLog)
                threadWarranty.start()
                self.threadWarranty = threadWarranty
        else:
            QtGui.QMessageBox.about(self,"Message","Please click <b>open</b> button to import data firstly.")

    def about(self):
        QtGui.QMessageBox.about(self, "About Tool",
                                "Version:1.0.\r\nPlease report bugs to wen.zhang@wedoapp.com.")

    def createActions(self):
        self.openAct = QtGui.QAction("&Open...", self,
                shortcut=QtGui.QKeySequence.Open,
                statusTip="Open an existing file contains the computer serialno", triggered=self.open)

        self.saveAct = QtGui.QAction("&Export", self,
                shortcut=QtGui.QKeySequence.Save,
                statusTip="Export the result to disk", triggered=self.save)

        self.exitAct = QtGui.QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close)
        
        self.aboutAct = QtGui.QAction("&About", self,
                statusTip="Show the application's about",
                triggered=self.about)
        
    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)
        
        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)

    '''接收后台线程传递的进度参数,控制进度条的显示'''
    def handleProgressBar(self,value):
        self.progressBar.setValue(value)
        if value == 100:
            result = "The process has been finished.\r\nThe file was saved in %s."%(self.filesaved)
            QtGui.QMessageBox.about(self,"Message",result)
            self.logText.append(result)
               
    '''接收后台线程传递的日志信息,显示在窗体'''
    def handleTextLog(self,log):
        self.logText.append(str(log))

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
