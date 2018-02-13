#!/usr/bin/env python

from PyQt4 import QtCore, QtGui, Qt
from PyQt4.QtCore import QThread, SIGNAL
from PyQt4.QtGui import QColor
from PyQt4.Qwt5 import QwtPlot, QwtPlotCurve
import gui
import sys
import PyTango
import csv
import time
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from collections import deque
#import pyqtgraph as pg
import matplotlib.pyplot as plt
import PyQt4.Qwt5 as Qwt
import pygame as pg
#import Raspberry_SHT7x
import os
mutex = QtCore.QMutex()


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class black_screen_Thread(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.running = True
        white = (255,255,255)
        pg.init()
        pg.mouse.set_visible(False)
        self. screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
        self.screen.fill((0,0,0))
        #myfont = pg.font.SysFont("monospace", 100)
        myfont = pg.font.SysFont("Comic Sans MS", 50)
        label = myfont.render("ROADRUNNER", 1, white)
        label1 = myfont.render("R", 1, white)
        label2 = myfont.render("O", 1, white)
        label3 = myfont.render("A", 1, white)
        label4 = myfont.render("D", 1, white)
        label5 = myfont.render("R", 1, white)
        label6 = myfont.render("U", 1, white)
        label7 = myfont.render("N", 1, white)
        label8 = myfont.render("N", 1, white)
        label9 = myfont.render("E", 1, white)
        label10 = myfont.render("R", 1, white)
        width = label.get_rect().width
        height = label.get_rect().height
        width1 = label1.get_rect().width
        height1 = label1.get_rect().height
        widthScreen = 800
        heightScreen = 480
        rect1 = pg.Rect((widthScreen/2 - width/2, heightScreen/2 - height/2), (width, height))
        timeToWait = 0.1
        labels = [label1, label2, label3, label4, label5, label6, label7, label8, label9, label10]
        shift = 0
        for i in labels:
            self.screen.blit(i, (widthScreen/2 - width/2 + shift, heightScreen/2 - height/2))
            pg.display.update(rect1)
            shift += width1
            time.sleep(timeToWait)
        time.sleep(0.3)
        self.screen.fill((0,0,0))
        pg.display.update(rect1)
    def run(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONUP:
                    self.running = False
            time.sleep(0.5)
        pg.quit()
    def stop(self):
        self.running = False
        self.wait()


class read_rasp_Thread(QThread):
    def __init__(self, path_sensor):
        QThread.__init__(self)
        self.running = True
        self.humidity = None
        self.temperature = None
        self.sensor = PyTango.DeviceProxy(path_sensor)
        if self.sensor.state() == PyTango.DevState.OFF:
            self.sensor.On()
        time.sleep(1)
    def run(self):
        while self.running:
            try:
                self.humidity = self.sensor.Humidity
                self.temperature = self.sensor.Temperature
                self.emit(SIGNAL('newData'), self.humidity, self.temperature)
            except:
                self.emit(SIGNAL('connectionFailed()'))
                time.sleep(0.7)
            time.sleep(2)    
        if self.sensor.state() == PyTango.DevState.ON:
            self.sensor.Stop()
    def stop(self):
        self.running = False
        self.wait()


class ExampleApp(QtGui.QMainWindow, gui.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.label_current_state.installEventFilter(self)
        self.label_sensor.installEventFilter(self)
        self.label_sensor_1.installEventFilter(self)
        self.label_sensor_2.installEventFilter(self)
        self.label_sensor_3.installEventFilter(self)
        self.label_sensor_4.installEventFilter(self)
        
        self.label_humidity.installEventFilter(self)
        self.label_humidity_1.installEventFilter(self)
        self.label_humidity_2.installEventFilter(self)
        self.label_humidity_3.installEventFilter(self)
        self.label_humidity_4.installEventFilter(self)
        
        self.label_temperature.installEventFilter(self)
        self.label_temperature_1.installEventFilter(self)
        self.label_temperature_2.installEventFilter(self)
        self.label_temperature_3.installEventFilter(self)
        self.label_temperature_4.installEventFilter(self)
        
        """self.doubleSpinBox_humidity.installEventFilter(self)
        self.doubleSpinBox_humidity1.installEventFilter(self)
        self.doubleSpinBox_humidity2.installEventFilter(self)
        self.doubleSpinBox_humidity3.installEventFilter(self)
        self.doubleSpinBox_humidity4.installEventFilter(self)
        
        self.doubleSpinBox_temperature.installEventFilter(self)
        self.doubleSpinBox_temperature1.installEventFilter(self)
        self.doubleSpinBox_temperature2.installEventFilter(self)
        self.doubleSpinBox_temperature3.installEventFilter(self)
        self.doubleSpinBox_temperature4.installEventFilter(self)"""
        
        self.stateOfCurvers = [True, True, True, True, True]
        
        self.sensors = ["p11/raspberry/sht75.01", "p11/raspberry/sht75.02", "p11/raspberry/sht75.03", "p11/raspberry/sht75.04", "p11/raspberry/sht75.05"]
        
        cwd = os.getcwd()
        self.filePath = cwd + "/data/"
        if not os.path.exists(self.filePath):
            os.makedirs(self.filePath)
        #print self.cwd
        self.filename = 'hum_data%s.csv' % time.strftime('%Y%m%d-%H%M%S')
        self.file = open(self.filePath + self.filename, 'wb')
        self.writer = csv.writer(self.file, delimiter=';', quotechar="",quoting=csv.QUOTE_NONE, escapechar=';')
        self.writer.writerow(['#Time', '#Temperature_1', 'Humidity_1', 'Temperature_2', 'Humidity_2', 'Temperature_3', 'Humidity_3', 'Temperature_4', 'Humidity_4', 'Temperature_5', 'Humidity_5', ])

        self.label_sensor.setStyleSheet("background-color: rgb(153,0,0); color: rgb(255,255,255);")
        self.label_sensor_1.setStyleSheet("background-color: rgb(153,153,0); color: rgb(255,255,255);")
        self.label_sensor_2.setStyleSheet("background-color: rgb(0,0,0); color: rgb(255,255,255);")
        self.label_sensor_3.setStyleSheet("background-color: rgb(0,0,153); color: rgb(255,255,255);")
        self.label_sensor_4.setStyleSheet("background-color: rgb(0,153,0); color: rgb(255,255,255);")

        #self.humidity = []
        #self.temperature = []
        self.humidity1 = "---"
        self.humidity2 = "---"
        self.humidity3 = "---"
        self.humidity4 = "---"
        self.humidity5 = "---"
        self.temperature1 = "---"
        self.temperature2 = "---"
        self.temperature3 = "---"
        self.temperature4 = "---"
        self.temperature5 = "---"
        
        self.doubleSpinBox_temperature.setValue(0.00)
        self.doubleSpinBox_humidity.setValue(0.00)
        self.doubleSpinBox_temperature1.setValue(0.00)
        self.doubleSpinBox_humidity1.setValue(0.00)
        self.doubleSpinBox_temperature2.setValue(0.00)
        self.doubleSpinBox_humidity2.setValue(0.00)
        self.doubleSpinBox_temperature3.setValue(0.00)
        self.doubleSpinBox_humidity3.setValue(0.00)
        self.doubleSpinBox_temperature4.setValue(0.00)
        self.doubleSpinBox_humidity4.setValue(0.00)
        
        self.containers = []
        for i in range(len(self.sensors)):
            #self.containers.append(deque(maxlen = 2250))
            self.containers.append(deque(maxlen = 111))
        #self.times = deque(maxlen = 2250)
        self.times = deque(maxlen = 111)
               
        self.qwtPlot.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend)
        self.curve1 = QwtPlotCurve("Sensor1")
        #self.curve1.setPen(Qt.QPen(Qt.Qt.red, 3, Qt.Qt.SolidLine))
        self.curve1.setPen(Qt.QPen(QColor(153,0,0), 3, Qt.Qt.SolidLine))
        self.curve2 = QwtPlotCurve("Sensor2")
        #self.curve2.setPen(Qt.QPen(Qt.Qt.yellow, 3, Qt.Qt.SolidLine))
        self.curve2.setPen(Qt.QPen(QColor(153,153,0), 3, Qt.Qt.SolidLine))
        self.curve3 = QwtPlotCurve("Sensor3")
        #self.curve3.setPen(Qt.QPen(Qt.Qt.black, 3, Qt.Qt.SolidLine))
        self.curve3.setPen(Qt.QPen(QColor(0,0,0), 3, Qt.Qt.SolidLine))
        self.curve4 = QwtPlotCurve("Sensor4")
        #self.curve4.setPen(Qt.QPen(Qt.Qt.blue, 3, Qt.Qt.SolidLine))
        self.curve4.setPen(Qt.QPen(QColor(0,0,153), 3, Qt.Qt.SolidLine))
        #self.curve5 = QwtPlotCurve("Sensor5")
        #self.curve5.setPen(Qt.QPen(Qt.Qt.green, 3, Qt.Qt.SolidLine))
        #self.curve5.setPen(Qt.QPen(QColor(0,153,0), 3, Qt.Qt.SolidLine))
        self.curve1.attach(self.qwtPlot)
        self.curve2.attach(self.qwtPlot)
        self.curve3.attach(self.qwtPlot)
        self.curve4.attach(self.qwtPlot)
        #self.curve5.attach(self.qwtPlot)
        
        #print self.qwtPlot.axisAutoScale(0)
        #print self.qwtPlot.axisAutoScale(1)
        #print self.qwtPlot.axisAutoScale(2)
        #print self.qwtPlot.axisAutoScale(3)
        #self.qwtPlot.setAxisAutoScale(0)
        #self.qwtPlot.setAxisScale(2, 0, 0.3)
        

        self.data_thread1 = read_rasp_Thread(self.sensors[0])
        self.connect(self.data_thread1, SIGNAL("newData"), self.updateData1)
        self.connect(self.data_thread1, SIGNAL("connectionFailed()"), self.connectionFailed1)
        self.data_thread2 = read_rasp_Thread(self.sensors[1])
        self.connect(self.data_thread2, SIGNAL("newData"), self.updateData2)
        self.connect(self.data_thread2, SIGNAL("connectionFailed()"), self.connectionFailed2)
        self.data_thread3 = read_rasp_Thread(self.sensors[2])
        self.connect(self.data_thread3, SIGNAL("newData"), self.updateData3)
        self.connect(self.data_thread3, SIGNAL("connectionFailed()"), self.connectionFailed3)
        self.data_thread4 = read_rasp_Thread(self.sensors[3])
        self.connect(self.data_thread4, SIGNAL("newData"), self.updateData4)
        self.connect(self.data_thread4, SIGNAL("connectionFailed()"), self.connectionFailed4)
        self.data_thread5 = read_rasp_Thread(self.sensors[4])
        self.connect(self.data_thread5, SIGNAL("newData"), self.updateData5)
        self.connect(self.data_thread5, SIGNAL("connectionFailed()"), self.connectionFailed5)
        self.data_thread1.start()
        self.data_thread2.start()
        self.data_thread3.start()
        self.data_thread4.start()
        self.data_thread5.start()

        self.connections = [True, True, True, True, True]
        self.signals= [False, False, False, False, False]
        
        self.start = time.time()
        self.TimeToWrite = time.time()
    def connectionFailed1(self):
        self.connections[0] = False
        self.updateData1("-----", "-----", True)
    def connectionFailed2(self):
        self.connections[1] = False
        self.updateData2("-----", "-----", True)
    def connectionFailed3(self):
        self.connections[2] = False
        self.updateData3("-----", "-----", True)
    def connectionFailed4(self):
        self.connections[3] = False
        self.updateData4("-----", "-----", True)
    def connectionFailed5(self):
        self.connections[4] = False
        self.updateData5("-----", "-----", True)

    def updateData1(self, humidity, temperature, failed = False):
        self.signals[0] = True
        if not failed:
            self.doubleSpinBox_humidity.setStyleSheet("background-color: rgb(255,255,255);")
            self.doubleSpinBox_temperature.setStyleSheet("background-color: rgb(255,255,255);")
            self.doubleSpinBox_humidity.setValue(humidity)
            self.doubleSpinBox_temperature.setValue(temperature)
            self.humidity1 = float("%.2f" % humidity)
            self.temperature1 = float("%.2f" % temperature)
        else:
            self.doubleSpinBox_humidity.setStyleSheet("background-color: rgb(255,0,0);")
            self.doubleSpinBox_temperature.setStyleSheet("background-color: rgb(255,0,0);")
            self.doubleSpinBox_humidity.setValue(0.00)
            self.doubleSpinBox_temperature.setValue(0.00)
            self.humidity1 = "---"
            self.temperature1 = "---"
    def updateData2(self, humidity, temperature, failed = False):
        self.signals[1] = True
        if not failed:
            self.doubleSpinBox_humidity1.setStyleSheet("background-color: rgb(255,255,255);")
            self.doubleSpinBox_temperature1.setStyleSheet("background-color: rgb(255,255,255);")
            self.doubleSpinBox_humidity1.setValue(humidity)
            self.doubleSpinBox_temperature1.setValue(temperature)
            self.humidity2 = float("%.2f" % humidity)
            self.temperature2 = float("%.2f" % temperature)
        else:
            self.doubleSpinBox_humidity1.setStyleSheet("background-color: rgb(255,0,0);")
            self.doubleSpinBox_temperature1.setStyleSheet("background-color: rgb(255,0,0);")
            self.doubleSpinBox_humidity1.setValue(0.00)
            self.doubleSpinBox_temperature1.setValue(0.00)
            self.humidity2 = "---"
            self.temperature2 = "---"
    def updateData3(self, humidity, temperature, failed = False):
        self.signals[2] = True
        if not failed:
            self.doubleSpinBox_humidity2.setStyleSheet("background-color: rgb(255,255,255);")
            self.doubleSpinBox_temperature2.setStyleSheet("background-color: rgb(255,255,255);")
            self.doubleSpinBox_humidity2.setValue(humidity)
            self.doubleSpinBox_temperature2.setValue(temperature)
            self.humidity3 = float("%.2f" % humidity)
            self.temperature3 = float("%.2f" % temperature)
        else:
            self.doubleSpinBox_humidity2.setStyleSheet("background-color: rgb(255,0,0);")
            self.doubleSpinBox_temperature2.setStyleSheet("background-color: rgb(255,0,0);")
            self.doubleSpinBox_humidity2.setValue(0.00)
            self.doubleSpinBox_temperature2.setValue(0.00)
            self.humidity3 = "---"
            self.temperature3 = "---"
    def updateData4(self, humidity, temperature, failed = False):
        self.signals[3] = True
        if not failed:
            self.doubleSpinBox_humidity3.setStyleSheet("background-color: rgb(255,255,255);")
            self.doubleSpinBox_temperature3.setStyleSheet("background-color: rgb(255,255,255);")
            self.doubleSpinBox_humidity3.setValue(humidity)
            self.doubleSpinBox_temperature3.setValue(temperature)
            self.humidity4 = float("%.2f" % humidity)
            self.temperature4 = float("%.2f" % temperature)
        else:
            self.doubleSpinBox_humidity3.setStyleSheet("background-color: rgb(255,0,0);")
            self.doubleSpinBox_temperature3.setStyleSheet("background-color: rgb(255,0,0);")
            self.doubleSpinBox_humidity3.setValue(0.00)
            self.doubleSpinBox_temperature3.setValue(0.00)
            self.humidity4 = "---"
            self.temperature4 = "---"
    def updateData5(self, humidity, temperature, failed = False):
        self.signals[4] = True
        if not failed:
            self.doubleSpinBox_humidity4.setStyleSheet("background-color: rgb(255,255,255);")
            self.doubleSpinBox_temperature4.setStyleSheet("background-color: rgb(255,255,255);")
            self.doubleSpinBox_humidity4.setValue(humidity)
            self.doubleSpinBox_temperature4.setValue(temperature)
            self.humidity5 = float("%.2f" % humidity)
            self.temperature5 = float("%.2f" % temperature)
        else:
            self.doubleSpinBox_humidity4.setStyleSheet("background-color: rgb(255,0,0);")
            self.doubleSpinBox_temperature4.setStyleSheet("background-color: rgb(255,0,0);")
            self.doubleSpinBox_humidity4.setValue(0.00)
            self.doubleSpinBox_temperature4.setValue(0.00)
            self.humidity5 = "---"
            self.temperature5 = "---"
        if self.signals[0] and self.signals[1] and self.signals[2] and self.signals[3] and self.signals[4]:
            for i in range(len(self.signals)):
                self.signals[i] = False
            if self.humidity1 == "---":
                self.containers[0].append(0)
            else:
                self.containers[0].append(self.humidity1)
            if self.humidity2 == "---":
                self.containers[1].append(0)
            else:
                self.containers[1].append(self.humidity2)
            if self.humidity3 =="---":
                self.containers[2].append(0)
            else:
                self.containers[2].append(self.humidity3)
            if self.humidity4 == "---":
                self.containers[3].append(0)
            else:
                self.containers[3].append(self.humidity4)
            if self.humidity5 == "---":
                self.containers[4].append(0)
            else:
                self.containers[4].append(self.humidity5)
            elapsedTime = (time.time() - self.start) / 60.
            self.times.append(elapsedTime)
            self.xdata = np.array(self.times)
            self.ydata1 = np.array(self.containers[0])
            self.ydata2 = np.array(self.containers[1])
            self.ydata3 = np.array(self.containers[2])        
            self.ydata4 = np.array(self.containers[3])
            self.ydata5 = np.array(self.containers[4])   
            self.plotData()
            a = ""
            for i in range(len(self.connections)):
                if not self.connections[i]:
                    a += str(i+1)+" "
            if a == "":
                self.label_current_state.setStyleSheet("color: rgb(50,150,0);")
                self.label_current_state.setText("Current state: ON")
            else:
                self.label_current_state.setStyleSheet("color: rgb(255,0,0);")
                self.label_current_state.setText("Connection to sensor N %s failed!!!\nTry properly make the connection" % a[0:-1])
            for i in range(len(self.connections)):
                self.connections[i] = True
            row = []
            timeToWrite = '%s' % time.strftime('%Y%m%d-%H%M%S')
            row.append(timeToWrite)
            if self.temperature1 == "---":
                row.append(self.temperature1)
            else:
                row.append("%.2f" % self.temperature1)
            if self.humidity1 == "---":
                row.append(self.humidity1)
            else:
                row.append("%.2f" % self.humidity1)
            if self.temperature2 == "---":
                row.append(self.temperature2)
            else:
                row.append("%.2f" % self.temperature2)
            if self.humidity2 == "---":
                row.append(self.humidity2)
            else:
                row.append("%.2f" % self.humidity2)
            if self.temperature3 == "---":
                row.append(self.temperature3)
            else:
                row.append("%.2f" % self.temperature3)
            if self.humidity3 == "---":
                row.append(self.humidity3)
            else:
                row.append("%.2f" % self.humidity3)
            if self.temperature4 == "---":
                row.append(self.temperature4)
            else:
                row.append("%.2f" % self.temperature4)
            if self.humidity4 == "---":
                row.append(self.humidity4)
            else:
                row.append("%.2f" % self.humidity4)
            if self.temperature5 == "---":
                row.append(self.temperature5)
            else:
                row.append("%.2f" % self.temperature5)
            if self.humidity5 == "---":
                row.append(self.humidity5)
            else:
                row.append("%.2f" % self.humidity5)
            self.writer.writerow(row)
            if ((time.time() - self.TimeToWrite) / 60.) > 5:
                self.file.close()
                self.file = open(self.filePath + self.filename, 'a')
                self.writer = csv.writer(self.file, delimiter=';', quotechar="",quoting=csv.QUOTE_NONE, escapechar=';')
                self.TimeToWrite = time.time()
    def plotData(self):
        #print time.time()
        self.curve1.setData(self.xdata, self.ydata1)
        self.curve2.setData(self.xdata, self.ydata2)
        self.curve3.setData(self.xdata, self.ydata3)
        self.curve4.setData(self.xdata, self.ydata4)
        #self.curve5.setData(self.xdata, self.ydata5)
        self.qwtPlot.replot()
    def eventFilter(self, obj, event):
        if (event.type() == Qt.QEvent.MouseButtonRelease) and (obj == self.label_current_state):
            self.blackScreen = black_screen_Thread()
            self.blackScreen.start()
        if (event.type() == Qt.QEvent.MouseButtonRelease) and (obj == self.label_sensor or obj == self.label_humidity or obj == self.label_temperature):
            if not self.stateOfCurvers[0]:
                self.curve1.attach(self.qwtPlot)
                self.curve2.attach(self.qwtPlot)
                self.curve3.attach(self.qwtPlot)
                self.curve4.attach(self.qwtPlot)
                #self.curve5.attach(self.qwtPlot)
                self.qwtPlot.replot()
                self.stateOfCurvers = [True, True, True, True, True]
            else:
                self.curve1.attach(self.qwtPlot)
                self.curve2.detach()
                self.curve3.detach()
                self.curve4.detach()
                #self.curve5.detach()
                self.qwtPlot.replot()
                self.stateOfCurvers = [False, True, True, True, True]
        if (event.type() == Qt.QEvent.MouseButtonRelease) and (obj == self.label_sensor_1 or obj == self.label_humidity_1 or obj == self.label_temperature_1):
            if not self.stateOfCurvers[1]:
                self.curve2.detach()
                self.curve1.attach(self.qwtPlot)
                self.curve2.attach(self.qwtPlot)
                self.curve3.attach(self.qwtPlot)
                self.curve4.attach(self.qwtPlot)
                #self.curve5.attach(self.qwtPlot)
                self.qwtPlot.replot()
                self.stateOfCurvers = [True, True, True, True, True]
            else:
                self.curve2.attach(self.qwtPlot)
                self.curve1.detach()
                self.curve3.detach()
                self.curve4.detach()
                #self.curve5.detach()
                self.qwtPlot.replot()
                self.stateOfCurvers = [True, False, True, True, True]
        if (event.type() == Qt.QEvent.MouseButtonRelease) and (obj == self.label_sensor_2 or obj == self.label_humidity_2 or obj == self.label_temperature_2):
            if not self.stateOfCurvers[2]:
                self.curve3.detach()
                self.curve1.attach(self.qwtPlot)
                self.curve2.attach(self.qwtPlot)
                self.curve3.attach(self.qwtPlot)
                self.curve4.attach(self.qwtPlot)
                #self.curve5.attach(self.qwtPlot)
                self.qwtPlot.replot()
                self.stateOfCurvers = [True, True, True, True, True]
            else:
                self.curve3.attach(self.qwtPlot)
                self.curve1.detach()
                self.curve2.detach()
                self.curve4.detach()
                #self.curve5.detach()
                self.qwtPlot.replot()
                self.stateOfCurvers = [True, True, False, True, True]
        if (event.type() == Qt.QEvent.MouseButtonRelease) and (obj == self.label_sensor_3 or obj == self.label_humidity_3 or obj == self.label_temperature_3):
            if not self.stateOfCurvers[3]:
                self.curve4.detach()
                self.curve1.attach(self.qwtPlot)
                self.curve2.attach(self.qwtPlot)
                self.curve3.attach(self.qwtPlot)
                self.curve4.attach(self.qwtPlot)
                #self.curve5.attach(self.qwtPlot)
                self.qwtPlot.replot()
                self.stateOfCurvers = [True, True, True, True, True]
            else:
                self.curve4.attach(self.qwtPlot)
                self.curve1.detach()
                self.curve2.detach()
                self.curve3.detach()
                #self.curve5.detach()
                self.qwtPlot.replot()
                self.stateOfCurvers = [True, True, True, False, True]
        if (event.type() == Qt.QEvent.MouseButtonRelease) and (obj == self.label_sensor_4 or obj == self.label_humidity_4 or obj == self.label_temperature_4):
            if not self.stateOfCurvers[4]:
                #self.curve5.detach()
                self.curve1.attach(self.qwtPlot)
                self.curve2.attach(self.qwtPlot)
                self.curve3.attach(self.qwtPlot)
                self.curve4.attach(self.qwtPlot)
                #self.curve5.attach(self.qwtPlot)
                self.qwtPlot.replot()
                self.stateOfCurvers = [True, True, True, True, True]
            else:
                #self.curve5.attach(self.qwtPlot)
                self.curve1.detach()
                self.curve2.detach()
                self.curve3.detach()
                self.curve4.detach()
                self.qwtPlot.replot()
                self.stateOfCurvers = [True, True, True, True, False]
        return QtGui.QMainWindow.eventFilter(self, obj, event)
    def stopMeasure(self):
        if self.data_thread1 is not None:
            self.data_thread1.stop()
        if self.data_thread2 is not None:
            self.data_thread2.stop()
        if self.data_thread3 is not None:
            self.data_thread3.stop()
        if self.data_thread4 is not None:
            self.data_thread4.stop()
        if self.data_thread5 is not None:
            self.data_thread5.stop()
        self.file.close()
    def __del__(self):
        self.stopMeasure()

def main():
    app = QtGui.QApplication(sys.argv)
    form = ExampleApp()
    form.showFullScreen()
    #form.show()
    app.exec_()
    


if __name__ == '__main__':
    main()
