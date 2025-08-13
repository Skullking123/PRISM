import sys
from venv import logger

from PySide6.QtWidgets import QVBoxLayout, QLabel, QGroupBox
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from HardwareMonitor.Hardware import HardwareType
from constants import *
import threading
from PySide6.QtCore import QPointF, QTimer
from performanceLogging import HardwareLogger
import time


class OverviewChartView(QGroupBox):
    def __init__(self, title, logger: HardwareLogger, startTime: float, parent=None, xAxisTitle = "", yAxisTitle = "", yRange: float = 100.0):
        super().__init__(parent)
        self.setTitle(title)
        self.points = []
        self.points_line_series = QLineSeries()
        self.xAxisTitle = xAxisTitle
        self.yAxisTitle = yAxisTitle
        self.logger = logger
        self.startTime = startTime
        # y-axis
        self.yAxis = QValueAxis()
        self.yAxis.setTitleText(yAxisTitle)
        self.yAxis.setRange(0, yRange)
        # x-axis
        self.xAxis = QValueAxis()
        self.xAxis.setTitleText(xAxisTitle)
        self.xAxis.setRange(0, 60)
        self.setLayout(QVBoxLayout())
        
        # add the chart
        chart = QChart()
        chart.addSeries(self.points_line_series)
        chart.setAxisY(self.yAxis, self.points_line_series)
        chart.setAxisX(self.xAxis)
        self.chart_view = QChartView(chart)
        self.layout().addWidget(self.chart_view)
    
    def addPoint(self, x: float, y: float):
        self.points.append(QPointF(x, y))
        self.points_line_series.append(QPointF(x, y))
        window_size = 60  # seconds or units
        if x < window_size: # create a sliding window effect 
            self.xAxis.setRange(0, window_size)
        else:
            self.xAxis.setRange(x - window_size, x)
            
        # update the chart by making a new chart and adding it
        # modifying the already existing chart is apparently very difficult
        chart = QChart()
        chart.addSeries(self.points_line_series)
        chart.setAxisY(self.yAxis)
        chart.setAxisX(self.xAxis)
        self.chart_view.setChart(chart)

class Overview(QVBoxLayout):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self.label = QLabel("CPU Usage")
        self.cpuUsage = OverviewChartView("CPU Load", "Time", "Usage")
        self.addWidget(self.cpuUsage)
        self.gpuUsage = OverviewChartView("GPU Load", "Time", "Usage")
        self.addWidget(self.gpuUsage)
        self.memoryUsage = OverviewChartView("Memory Usage", "Time", "Usage")
        self.addWidget(self.memoryUsage)
        self.logger = HardwareLogger(None) # get a logger for all of the hardware
        self.startTime = time.perf_counter()
        self._setupTimers()
        
    def _updateCPUChart(self, now: float):
        # Update CPU chart with new data (called by QTimer)
        data = self.logger.read()
        elapsed = now - self.startTime
        self.cpuUsage.addPoint(elapsed, data.get("CPU Total"))

    def _updateGPUChart(self, now: float):
        # Update GPU chart with new data (called by QTimer)
        data = self.logger.read()
        self.gpuUsage.addPoint(now - self.startTime, data.get("GPU Core"))


    def _updateMemoryChart(self, now: float):
        # Update Memory chart with new data (called by QTimer)
        data = self.logger.read()
        # display memory usage as a percentage
        self.memoryUsage.addPoint(now - self.startTime, (data.get("Memory Used") / (data.get("Memory Used") + data.get("Memory Available"))) * 100)
        print(f"Point added: {now - self.startTime}, {(data.get('Memory Used') / (data.get('Memory Used') + data.get('Memory Available'))) * 100}")
    def _updateMetrics(self):
        now = time.perf_counter()
        self._updateCPUChart(now)
        self._updateGPUChart(now)
        self._updateMemoryChart(now)

    def _setupTimers(self):
        self._cpu_timer = QTimer()
        self._cpu_timer.timeout.connect(self._updateMetrics)
        self._cpu_timer.start(1000)  # 1 second

