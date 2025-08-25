import sys
from venv import logger

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QGroupBox, QProgressBar, QGridLayout, QWidget, QSpacerItem, QSizePolicy
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
from ScrollingLineChart import ScrollingLineChart
from Speedometer import Speedometer

BACKGROUND = QColor(255, 99, 132)
FREE = QColor(75, 192, 192)

NOT_FOUND = -9999

class QuickInfoGroupWidget(QGroupBox):
    def __init__(self, parent=None, title: str ="", metrics: list[(str, SensorType)] = None, vertical = True):
        super().__init__(parent)
        self.setTitle(title)
        if vertical:
            layout = QVBoxLayout(self)
        else:
            layout = QHBoxLayout(self)
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.widgets = []
        if metrics:
            last = len(metrics) - 1
            for item in range(0, len(metrics)):
                name, type = metrics[item]
                layout.addWidget(QuickInfoWidget(name, type, self))
                if item != last: # don't add a spacer after the last item
                    if vertical:
                        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
                    else:
                        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addStretch()
        self.setLayout(layout)

    def updateMetrics(self, metrics: dict[str, float]):
        # Update the metrics displayed in the QuickInfoWidgets
        # the dictionary maps metric names to their (value, unit) tuples
        for item in self.findChildren(QuickInfoWidget):
            metric_name = item.name
            if metric_name in metrics:
                item.setValue(metrics[metric_name])
        # print(self.findChildren(QuickInfoWidget))

class QuickInfoWidget(QWidget):
    def __init__(self, name: str, type: SensorType, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.type = type
        self.name = name
        self.label = QLabel(name + ": ")
        layout.addWidget(self.label)
        self.setLayout(layout)
    def setValue(self, value: float):
        if value != NOT_FOUND:
            self.label.setText(f"{self.name}: {SensorValueToString(value, self.type)}")
        else:
            self.label.setText(f"{self.name}: N/A")
        self.update()
        
class Overview(QWidget):
    def __init__(self, color: QColor, parent=None):
        super().__init__(parent)
        global BACKGROUND
        BACKGROUND = color
        self.setContentsMargins(0, 0, 0, 0)
        # self.setSpacing(0)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.initCPUView()
        self.initGPUView()
        self.initMemoryView()
        self.initNetworkView()
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.updateData)
        self.timer.start()
        
    def initCPUView(self):
        self.cpuView = QWidget(self)
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.cpuChart = DonutChart()
        self.cpuChart.set_chart_data([
            ("Used", 100, FREE)
        ], "CPU 50%")
        layout.addWidget(self.cpuChart, 0, 0)
        self.cpuInfo = QuickInfoGroupWidget(self, "CPU Info", [("Temperature", SensorType.Temperature), ("Clock Speed", SensorType.Clock)])
        layout.addWidget(self.cpuInfo, 0, 1)
        self.cpuView.setLayout(layout)
        self.layout().addWidget(self.cpuView, 0, 0)
    
    def initGPUView(self):
        self.gpuView = QWidget(self)
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.gpuChart = DonutChart()
        self.gpuChart.set_chart_data([
            ("Used", 100, FREE)
        ], "GPU 50%")
        layout.addWidget(self.gpuChart, 0, 0)
        self.gpuInfo = QuickInfoGroupWidget(self, "GPU Info", [("Temperature", SensorType.Temperature), ("Clock Speed", SensorType.Clock)])
        layout.addWidget(self.gpuInfo, 0, 1)
        self.gpuView.setLayout(layout)
        self.layout().addWidget(self.gpuView, 0, 1)

    def initMemoryView(self):
        self.memoryView = QWidget(self)
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.memoryChart = DonutChart()
        self.memoryChart.set_chart_data([
            ("Used", 50, FREE)
        ], "Memory 50%")
        layout.addWidget(self.memoryChart, 0, 0)
        self.memoryView.setLayout(layout)
        self.layout().addWidget(self.memoryView, 1, 0)
    
    def initNetworkView(self):
        self.networkView = QWidget(self)
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.networkDownloadChart = Speedometer(self)
        self.networkUploadChart = Speedometer(self)
        self.networkInfo = QuickInfoGroupWidget(self, "Network I/O", [("Download", SensorType.SmallData), ("Upload", SensorType.SmallData)], False)
        layout.addWidget(self.networkDownloadChart, 1, 0)
        layout.addWidget(self.networkUploadChart, 1, 1)
        layout.addWidget(self.networkInfo, 0, 0)
        self.networkView.setLayout(layout)
        self.layout().addWidget(self.networkView, 1, 1)

    def updateData(self):
        self._updateCPUView()
        self._updateGPUView()
        self._updateMemView()
        self._updateNetworkView()
        
    def _updateCPUView(self):
        cpu = HARDWARE.hardware["CPU"][0] # usually there is only one cpu
        cpuData = readSensorOutput(cpu)
        cpuUsage = cpuData[("CPU Total", SensorType.Load)]
        sanitized_name = cpu.Name.lower()
        if "amd" in sanitized_name and ("Core (Tctl/Tdie)", SensorType.Temperature) in cpuData:
            cpuTemperature = cpuData[("Core (Tctl/Tdie)", SensorType.Temperature)]
            # cpuTemperature = random.randint(0,101)
        elif "intel" in sanitized_name and ("CPU Package", SensorType.Temperature) in cpuData:
            cpuTemperature = cpuData[("CPU Package", SensorType.Temperature)]
        else:
            cpuTemperature = NOT_FOUND
        cpuFreq = psutil.cpu_freq()[0]
        self.cpuChart.set_chart_data([("Load", cpuUsage, FREE), ("", 100 - cpuUsage, BACKGROUND)], f"CPU: {SensorValueToString(cpuUsage, SensorType.Load)}", False)
        self.cpuInfo.updateMetrics({"Temperature": cpuTemperature, "Clock Speed": cpuFreq})
        
    def _updateGPUView(self):
        gpu = HARDWARE.hardware["GPU"][1] # 
        gpuData = readSensorOutput(gpu)
        gpuUsage = gpuData[("GPU Core", SensorType.Load)]
        gpuFreq = gpuData[("GPU Core", SensorType.Clock)]
        gpuTemp = gpuData[("GPU Core", SensorType.Temperature)]
        self.gpuChart.set_chart_data([("Load", gpuUsage, FREE), ("", 100 - gpuUsage, BACKGROUND)], f"GPU: {SensorValueToString(gpuUsage, SensorType.Load)}", False)
        self.gpuInfo.updateMetrics({"Temperature": gpuTemp, "Clock Speed": gpuFreq})
        
    def _updateMemView(self):
        memory = HARDWARE.hardware[HardwareParts.MEMORY.value][0] # usually people only have 1 set of memory
        memData = readSensorOutput(memory)
        memUsage = memData[("Memory", SensorType.Load)]
        self.memoryChart.set_chart_data([("Load", memUsage, FREE), ("", 100 - memUsage, BACKGROUND)], f"RAM: {SensorValueToString(memUsage, SensorType.Load)}", False)
        
    def _updateNetworkView(self):
        networkData = psutil.net_io_counters()
        upload = networkData[0]  / 1000000
        download = networkData[1] / 1000000
        self.networkInfo.updateMetrics({"Download": download, "Upload": upload})
        self.networkDownloadChart.setValue(download)
        self.networkUploadChart.setValue(upload)

        
        
        
        
        
        
        
