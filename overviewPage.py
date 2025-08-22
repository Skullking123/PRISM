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

BACKGROUND = QColor(255, 99, 132)
FREE = QColor(75, 192, 192)

NOT_FOUND = -9999

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
        # Make the progress bar thicker
        self.progress_bar.setMinimumHeight(20)  # Set minimum height to 20 pixels (adjust as needed)
        
        # Optional: Style the progress bar for better appearance
        background_color = BACKGROUND.name()
        load_color = FREE.name()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #999;
                border-radius: 3px;
                background-color: {background_color};
                height: 25px;  /* Explicit height */
            }}
            QProgressBar::chunk {{
                background-color: {load_color};
                border-radius: 2px;
            }}
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(50)
        self.progress_bar.setTextVisible(False)
        self.data = data
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
    
    def setValue(self, value: float):
        if value != NOT_FOUND:
            self.progress_bar.setValue(value)
            self.label.setText(f"{SensorTypeToString(self.data)}: {SensorValueToString(value, self.data)}")
        else:
            self.progress_bar.setValue(0)
            self.label.setText(f"{SensorTypeToString(self.data)}: N/A")
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
        self.memoryView.setLayout(layout)
        self.layout().addWidget(self.memoryView, 1, 0)
    
    def initNetworkView(self):
        self.networkView = QWidget()
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        
        pass

    def updateData(self):
        self._updateCPUView()
        self._updateGPUView()
        self._updateMemView()
        
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
        self.cpuInfo.updateMetrics({SensorType.Temperature: cpuTemperature, SensorType.Clock: cpuFreq})
        
    def _updateGPUView(self):
        gpu = HARDWARE.hardware["GPU"][1] # 
        gpuData = readSensorOutput(gpu)
        gpuUsage = gpuData[("GPU Core", SensorType.Load)]
        gpuFreq = gpuData[("GPU Core", SensorType.Clock)]
        gpuTemp = gpuData[("GPU Core", SensorType.Temperature)]
        self.gpuChart.set_chart_data([("Load", gpuUsage, FREE), ("", 100 - gpuUsage, BACKGROUND)], f"GPU: {SensorValueToString(gpuUsage, SensorType.Load)}", False)
        self.gpuInfo.updateMetrics({SensorType.Temperature: gpuTemp, SensorType.Clock: gpuFreq})
        
    def _updateMemView(self):
        memory = HARDWARE.hardware[HardwareParts.MEMORY.value][0] # usually people only have 1 set of memory
        memData = readSensorOutput(memory)
        memUsage = memData[("Memory", SensorType.Load)]
        self.memoryChart.set_chart_data([("Load", memUsage, FREE), ("", 100 - memUsage, BACKGROUND)], f"RAM: {SensorValueToString(memUsage, SensorType.Load)}", False)
        
    def _updateNetworkView(self):
        pass
        
        
        
        
        
        
        
        
        
        
