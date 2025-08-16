import sys
from venv import logger

from PySide6.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QProgressBar, QGridLayout, QWidget
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QPieSeries
from PySide6.QtGui import QColor
from HardwareMonitor.Hardware import HardwareType
from constants import *
import threading
from PySide6.QtCore import QPointF, QTimer, Qt
from performanceLogging import HardwareLogger
import time
from DonutChart import DonutChart



class UsagePieChart(QChartView):
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create donut chart
        self.series = QPieSeries()
        self.series.append("Used", 70)
        self.series.append("Free", 30)
        self.series.setHoleSize(0.6)  # 0.0 = pie, 1.0 = full hole

        chart = QChart()
        chart.addSeries(self.series)
        chart.setTitle(title)
        chart.legend().hide()

        chart_view = QChartView(chart)
        chart_view.setRenderHint(chart_view.RenderHint.Antialiasing)
        layout.addWidget(chart_view)

        # Create label and overlay it
        self.label = QLabel("70%")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 24px; font-weight: bold; background: transparent;")
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

    def setValue(self, used: int, free: int):
        self.series.clear()
        self.series.append("Used", used)
        self.series.append("Free", free)
        self.label.setText(f"{used}%")

class QuickInfoGroupWidget(QGroupBox):
    def __init__(self, parent=None, title: str ="", metrics: list[str] = None):
        super().__init__(parent)
        self.setTitle(title)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.widgets = []
        if metrics:
            for item in metrics:
                layout.addWidget(QuickInfoWidget(self, item))
        self.setLayout(layout)

    def updateMetrics(self, metrics: dict[str, (int, str)]):
        # Update the metrics displayed in the QuickInfoWidgets
        # the dictionary maps metric names to their (value, unit) tuples
        for item in self.findChildren(QuickInfoWidget):
            metric_name = item.metric
            if metric_name in metrics:
                item.setValue(metrics[metric_name])

class QuickInfoWidget(QWidget):
    def __init__(self, parent=None, metric: str = ""):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.label = QLabel(metric + ": ")
        layout.addWidget(self.label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(50)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
    
    def setValue(self, value: int, unit: str):
        self.progress_bar.setValue(value)
        self.label.setText(f"{self.metric}: {value} {unit}")

class Overview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        # self.setSpacing(0)
        self.logger = HardwareLogger(None)
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.initCPUView()
        self.initGPUView()
        self.initMemoryView()
        
    def initCPUView(self):
        self.cpuView = QWidget()
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.cpuChart = DonutChart()
        self.cpuChart.set_chart_data([
            ("Used", 50, QColor(255, 99, 132)),
            ("Free", 50, QColor(75, 192, 192))
        ], "CPU 50%")
        layout.addWidget(self.cpuChart, 0, 0)
        self.cpuInfo = QuickInfoGroupWidget(self, "CPU Info", ["Temperature", "Clock Speed"])
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
            ("Used", 50, QColor(255, 99, 132)),
            ("Free", 50, QColor(75, 192, 192))
        ], "GPU 50%")
        layout.addWidget(self.gpuChart, 0, 0)
        self.gpuInfo = QuickInfoGroupWidget(self, "GPU Info", ["Temperature", "Clock Speed"])
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
            ("Used", 50, QColor(255, 99, 132)),
            ("Free", 50, QColor(75, 192, 192))
        ], "Memory 50%")
        layout.addWidget(self.memoryChart, 0, 0)
        self.memoryInfo = QuickInfoGroupWidget(self, "Memory Info", ["Clock Speed"])
        layout.addWidget(self.memoryInfo, 0, 1)
        self.memoryView.setLayout(layout)
        self.layout().addWidget(self.memoryView, 1, 0)

    def update(self, data = {}):
        cpuData = {}
        cpuData["CPU Total"] = data["CPU Total"]
