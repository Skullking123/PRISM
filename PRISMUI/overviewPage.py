import sys
from venv import logger

from PySide6.QtWidgets import QVBoxLayout, QLabel, QGroupBox, QProgressBar, QGridLayout, QWidget
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QPieSeries
from HardwareMonitor.Hardware import HardwareType
from constants import *
import threading
from PySide6.QtCore import QPointF, QTimer, Qt
from performanceLogging import HardwareLogger
import time


# class OverviewChartView(QGroupBox):
#     def __init__(self, title, logger: HardwareLogger, startTime: float, parent=None, xAxisTitle = "", yAxisTitle = "", yRange: float = 100.0):
#         super().__init__(parent)
#         self.setTitle(title)
#         self.points = []
#         self.points_line_series = QLineSeries()
#         self.xAxisTitle = xAxisTitle
#         self.yAxisTitle = yAxisTitle
#         self.logger = logger
#         self.startTime = startTime
#         # y-axis
#         self.yAxis = QValueAxis()
#         self.yAxis.setTitleText(yAxisTitle)
#         self.yAxis.setRange(0, yRange)
#         # x-axis
#         self.xAxis = QValueAxis()
#         self.xAxis.setTitleText(xAxisTitle)
#         self.xAxis.setRange(0, 60)
#         self.setLayout(QVBoxLayout())
        
#         # add the chart
#         chart = QChart()
#         chart.addSeries(self.points_line_series)
#         chart.setAxisY(self.yAxis, self.points_line_series)
#         chart.setAxisX(self.xAxis)
#         self.chart_view = QChartView(chart)
#         self.layout().addWidget(self.chart_view)
    
#     def addPoint(self, x: float, y: float):
#         self.points.append(QPointF(x, y))
#         self.points_line_series.append(QPointF(x, y))
#         window_size = 60  # seconds or units
#         if x < window_size: # create a sliding window effect 
#             self.xAxis.setRange(0, window_size)
#         else:
#             self.xAxis.setRange(x - window_size, x)
            
#         # update the chart by making a new chart and adding it
#         # modifying the already existing chart is apparently very difficult
#         chart = QChart()
#         chart.addSeries(self.points_line_series)
#         chart.setAxisY(self.yAxis)
#         chart.setAxisX(self.xAxis)
#         self.chart_view.setChart(chart)

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
        if metrics:
            for item in metrics:
                layout.addWidget(QuickInfoItem(self, item))
        self.setLayout(layout)

    def updateMetrics(self, metrics: dict[str, int]):
        for item in self.findChildren(QuickInfoItem):
            metric_name = item.metric
            if metric_name in metrics:
                item.setValue(metrics[metric_name])

class QuickInfoItem(QWidget):
    def __init__(self, parent=None, metric: str = ""):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.label = QLabel(metric + ": ")
        layout.addWidget(self.label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
    
    def setValue(self, value: int, unit = ""):
        self.progress_bar.setValue(value)
        self.label.setText(f"{self.metric}: {value} {unit}")

class Overview(QGridLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.logger = HardwareLogger(None)
        self.initCPUView()
        self.initGPUView()
        self.initMemoryView()

    def initCPUView(self):
        self.cpuView = QGridLayout()
        self.cpuView.setContentsMargins(0, 0, 0, 0)
        # cpu temperatures
        tempLabel = QLabel("Temperature: ")
        tempProgBar = QProgressBar()
        tempProgBar.setRange(0, 100)
        tempProgBar.setValue(60)
        tempProgBar.setTextVisible(False)
        # cpu clock speed
        clockspeedLabel = QLabel("Clock Speed: ")
        clockspeedProgBar = QProgressBar()
        clockspeedProgBar.setRange(0, 100)
        clockspeedProgBar.setValue(50)
        clockspeedProgBar.setTextVisible(False)
        # cpu fan speed
        fanspeedLabel = QLabel("Fan Speed: ")
        fanspeedProgBar = QProgressBar()
        fanspeedProgBar.setRange(0, 100)
        fanspeedProgBar.setValue(75)
        fanspeedProgBar.setTextVisible(False)
        # create the infoLayout and add everything to it
        # the info will display to the right of the pie chart displaying the CPU usage
        infoLayout = QVBoxLayout()
        infoLayout.setSpacing(0)
        infoLayout.setContentsMargins(0, 0, 0, 0)
        infoLayout.addWidget(tempLabel)
        infoLayout.addWidget(tempProgBar)
        infoLayout.addWidget(clockspeedLabel)
        infoLayout.addWidget(clockspeedProgBar)
        infoLayout.addWidget(fanspeedLabel)
        infoLayout.addWidget(fanspeedProgBar)
        info = QGroupBox("CPU Info")
        info.setLayout(infoLayout)
        # pie chart for the CPU usage
        cpuPieChart = QChart()
        series = QPieSeries()
        series.append("Used", 50)
        series.append("Free", 50)
        cpuPieChart.addSeries(series)
        cpuPieChart.setTitle("CPU Usage")
        cpuPieChartView = QChartView(cpuPieChart)   
        # add the widgets into our grid layout
        self.cpuView.addWidget(cpuPieChartView, 0, 0)
        self.cpuView.addWidget(info, 0, 1)
        # add the cpu view to the grid
        self.addLayout(self.cpuView, 0, 0)
    
    def initGPUView(self):
        self.gpuView = QGridLayout()
        self.gpuView.setContentsMargins(0, 0, 0, 0)
        # gpu temperatures
        tempLabel = QLabel("Temperature: ")
        tempProgBar = QProgressBar()
        tempProgBar.setRange(0, 100)
        tempProgBar.setValue(60)
        tempProgBar.setTextVisible(False)
        # gpu clock speed
        clockspeedLabel = QLabel("Clock Speed: ")
        clockspeedProgBar = QProgressBar()
        clockspeedProgBar.setRange(0, 100)
        clockspeedProgBar.setValue(50)
        clockspeedProgBar.setTextVisible(False)
        # gpu fan speed
        fanspeedLabel = QLabel("Fan Speed: ")
        fanspeedProgBar = QProgressBar()
        fanspeedProgBar.setRange(0, 100)
        fanspeedProgBar.setValue(75)
        fanspeedProgBar.setTextVisible(False)
        # create the infoLayout and add everything to it
        # the info will display to the right of the pie chart displaying the CPU usage
        infoLayout = QVBoxLayout()
        infoLayout.setSpacing(0)
        infoLayout.setContentsMargins(0, 0, 0, 0)
        infoLayout.addWidget(tempLabel)
        infoLayout.addWidget(tempProgBar)
        infoLayout.addWidget(clockspeedLabel)
        infoLayout.addWidget(clockspeedProgBar)
        infoLayout.addWidget(fanspeedLabel)
        infoLayout.addWidget(fanspeedProgBar)
        info = QGroupBox("GPU Info")
        info.setLayout(infoLayout)
        # pie chart for the GPU usage
        gpuPieChart = QChart()
        series = QPieSeries()
        series.append("Used", 50)
        series.append("Free", 50)
        gpuPieChart.addSeries(series)
        gpuPieChart.setTitle("GPU Usage")
        gpuPieChartView = QChartView(gpuPieChart)
        # add the widgets into our grid layout
        self.gpuView.addWidget(gpuPieChartView, 0, 0)
        self.gpuView.addWidget(info, 0, 1)
        # add the gpu view to the grid
        self.addLayout(self.gpuView, 0, 1)

    def initMemoryView(self):
        self.memoryView = QVBoxLayout()
        self.memoryView.setContentsMargins(0, 0, 0, 0)
        # memory usage
        usageLabel = QLabel("Usage: ")
        memoryPieChart = QChart()
        series = QPieSeries()
        series.append("Used", 50)
        series.append("Free", 50)
        memoryPieChart.addSeries(series)
        memoryPieChart.setTitle("Memory Usage")
        memoryPieChartView = QChartView(memoryPieChart)
        # add the widgets into our memory view layout
        self.memoryView.addWidget(memoryPieChartView)
        self.memoryView.addWidget(usageLabel)
        self.addLayout(self.memoryView, 1, 0)
    
    def update(self):
        
        pass
