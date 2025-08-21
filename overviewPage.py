import sys
from venv import logger

from PySide6.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QProgressBar, QGridLayout, QWidget
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QPieSeries
from PySide6.QtGui import QColor
from HardwareMonitor.Hardware import HardwareType
from HardwareMonitor.Util import SensorValueToString, SensorType
from constants import *
import threading
from PySide6.QtCore import QPointF, QTimer, Qt
from performanceLogging import HARDWARE, readSensorOutput, printSensorOutput, SensorTypeToString
import time
from DonutChart import DonutChart
import json
import psutil
import random

USED = QColor(255, 99, 132)
FREE = QColor(75, 192, 192)

class QuickInfoGroupWidget(QGroupBox):
    def __init__(self, parent=None, title: str ="", metrics: list[SensorType] = None):
        super().__init__(parent)
        self.setTitle(title)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.widgets = []
        if metrics:
            for item in metrics:
                layout.addWidget(QuickInfoWidget(item, self))
        self.setLayout(layout)

    def updateMetrics(self, metrics: dict[SensorType, float]):
        # Update the metrics displayed in the QuickInfoWidgets
        # the dictionary maps metric names to their (value, unit) tuples
        for item in self.findChildren(QuickInfoWidget):
            metric_name = item.data
            if metric_name in metrics:
                item.setValue(metrics[metric_name])
        # print(self.findChildren(QuickInfoWidget))

class QuickInfoWidget(QWidget):
    def __init__(self, data: SensorType, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.label = QLabel(SensorTypeToString(data) + ": ")
        layout.addWidget(self.label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(50)
        self.progress_bar.setTextVisible(False)
        self.data = data
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
    
    def setValue(self, value: float):
        self.progress_bar.setValue(value)
        self.label.setText(f"{SensorTypeToString(self.data)}: {SensorValueToString(value, self.data)}")
        self.update()
        
class Overview(QWidget):
    def __init__(self, color: QColor, parent=None):
        super().__init__(parent)
        global USED
        USED = color
        self.setContentsMargins(0, 0, 0, 0)
        # self.setSpacing(0)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.initCPUView()
        self.initGPUView()
        self.initMemoryView()
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.updateData)
        self.timer.start()
        
    def initCPUView(self):
        self.cpuView = QWidget()
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.cpuChart = DonutChart()
        self.cpuChart.set_chart_data([
            ("Used", 100, FREE)
        ], "CPU 50%")
        layout.addWidget(self.cpuChart, 0, 0)
        self.cpuInfo = QuickInfoGroupWidget(self, "CPU Info", [SensorType.Temperature, SensorType.Clock])
        layout.addWidget(self.cpuInfo, 0, 1)
        self.cpuView.setLayout(layout)
        self.layout().addWidget(self.cpuView, 0, 0)
    
    def initGPUView(self):
        self.gpuView = QWidget()
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.gpuChart = DonutChart()
        self.gpuChart.set_chart_data([
            ("Used", 100, FREE)
        ], "GPU 50%")
        layout.addWidget(self.gpuChart, 0, 0)
        self.gpuInfo = QuickInfoGroupWidget(self, "GPU Info", [SensorType.Temperature, SensorType.Clock])
        layout.addWidget(self.gpuInfo, 0, 1)
        self.gpuView.setLayout(layout)
        self.layout().addWidget(self.gpuView, 0, 1)

    def initMemoryView(self):
        self.memoryView = QWidget()
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.memoryChart = DonutChart()
        self.memoryChart.set_chart_data([
            ("Used", 50, FREE)
        ], "Memory 50%")
        layout.addWidget(self.memoryChart, 0, 0)
        self.memoryInfo = QuickInfoGroupWidget(self, "Memory Info", [SensorType.Clock])
        layout.addWidget(self.memoryInfo, 0, 1)
        self.memoryView.setLayout(layout)
        self.layout().addWidget(self.memoryView, 1, 0)

    def updateData(self):
        self._updateCPUView()
        self._updateGPUView()
        
    def _updateCPUView(self):
        cpu = HARDWARE.hardware["CPU"][0] # usually there is only one cpu
        cpuData = readSensorOutput(cpu)
        cpuUsage = cpuData[("CPU Total", SensorType.Load)]
        sanitized_name = cpu.Name.lower()
        if "amd" in sanitized_name:
            # cpuTemperature = cpuData[("Core (Tctl/Tdie)", SensorType.Temperature)]
            cpuTemperature = random.randint(0,101)
        elif "intel" in sanitized_name:
            cpuTemperature = cpuData[("CPU Package", SensorType.Temperature)]
        else:
            cpuTemperature = "N/A"
        cpuFreq = psutil.cpu_freq()[0]
        self.cpuChart.set_chart_data([("Load", cpuUsage, FREE), ("", 100 - cpuUsage, USED)], f"CPU: {SensorValueToString(cpuUsage, SensorType.Load)}", False)
        self.cpuInfo.updateMetrics({SensorType.Temperature: cpuTemperature, SensorType.Clock: cpuFreq})
        
    def _updateGPUView(self):
        gpu = HARDWARE.hardware["GPU"][1] # 
        gpuData = readSensorOutput(gpu)
        gpuUsage = gpuData[("GPU Core", SensorType.Load)]
        gpuFreq = gpuData[("GPU Core", SensorType.Clock)]
        gpuTemp = gpuData[("GPU Core", SensorType.Temperature)]
        self.gpuChart.set_chart_data([("Load", gpuUsage, FREE), ("", 100 - gpuUsage, USED)], f"CPU: {SensorValueToString(gpuUsage, SensorType.Load)}", False)
        self.gpuInfo.updateMetrics({SensorType.Temperature: gpuTemp, SensorType.Clock: gpuFreq})
        
        
        
        
        
        
        
        
