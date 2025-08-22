import sys
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QApplication
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PySide6.QtCore import QTimer, QDateTime, Qt, QPointF
from PySide6.QtGui import QPen, QColor


class GenericScrollingChart(QWidget):
    """A simple, generic scrolling line chart widget"""
    
    def __init__(self, parent=None, title="Scrolling Chart", y_label="Value"):
        super().__init__(parent)
        
        # Configuration
        self.max_points = 100  # Maximum points to display
        self.time_window = 60  # Time window in seconds
        self.chart_title = title
        self.y_axis_label = y_label
        
        # Data storage
        self.data_points = []
        
        # Setup UI and chart
        self.setup_ui()
        self.setup_chart()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Control buttons
        controls = QHBoxLayout()
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear)
        
        controls.addWidget(self.clear_btn)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Chart will be added in setup_chart()
        
    def setup_chart(self):
        """Setup the chart components"""
        # Create chart
        self.chart = QChart()
        self.chart.setTitle(self.chart_title)
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        # Create data series
        self.series = QLineSeries()
        self.series.setName("Data")
        
        # Style the line
        pen = QPen(QColor(0, 120, 215), 2)  # Blue line, 2px width
        self.series.setPen(pen)
        
        # Add series to chart
        self.chart.addSeries(self.series)
        
        # Create time axis (X-axis)
        self.x_axis = QDateTimeAxis()
        self.x_axis.setFormat("hh:mm:ss")
        self.x_axis.setTitleText("Time")
        self.x_axis.setTickCount(6)
        
        # Create value axis (Y-axis)
        self.y_axis = QValueAxis()
        self.y_axis.setTitleText(self.y_axis_label)
        self.y_axis.setRange(0, 100)  # Default range
        
        # Add axes to chart
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        
        # Attach axes to series
        self.series.attachAxis(self.x_axis)
        self.series.attachAxis(self.y_axis)
        
        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(self.chart_view.RenderHint.Antialiasing)
        
        # Add chart to layout
        self.layout().addWidget(self.chart_view)
        
    def add_point(self, value: float, timestamp: Optional[QDateTime] = None):
        """
        Add a data point to the chart
        
        Args:
            value: The Y value to add
            timestamp: Optional timestamp, uses current time if None
        """
        if timestamp is None:
            timestamp = QDateTime.currentDateTime()
            
        # Create point
        point = QPointF(timestamp.toMSecsSinceEpoch(), value)
        self.data_points.append(point)
        
        # Remove old points if we exceed maximum
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
            
        # Update chart
        self._update_display()
        
    def add_points(self, values: list):
        """
        Add multiple data points at once
        
        Args:
            values: List of values or (value, timestamp) tuples
        """
        for value in values:
            if isinstance(value, tuple):
                self.add_point(value[0], value[1])
            else:
                self.add_point(value)
                
    def clear(self):
        """Clear all data from the chart"""
        self.data_points.clear()
        self.series.clear()
        
    def set_y_range(self, min_val: float, max_val: float):
        """Set the Y-axis range"""
        self.y_axis.setRange(min_val, max_val)
        
    def set_auto_scale(self, enabled: bool = True):
        """Enable or disable automatic Y-axis scaling"""
        self.auto_scale_enabled = enabled
        if enabled:
            self._auto_scale_y_axis()
            
    def _update_display(self):
        """Update the chart display"""
        # Update series with all points
        self.series.replace(self.data_points)
        
        # Update X-axis to show scrolling effect
        if len(self.data_points) > 1:
            latest_time = QDateTime.fromMSecsSinceEpoch(int(self.data_points[-1].x()))
            earliest_time = latest_time.addSecs(-self.time_window)
            self.x_axis.setRange(earliest_time, latest_time)
            
        # Auto-scale Y-axis if enabled
        self._auto_scale_y_axis()
        
    def _auto_scale_y_axis(self):
        """Automatically scale the Y-axis based on visible data"""
        if not self.data_points:
            return
            
        # Get recent values for scaling
        recent_values = [p.y() for p in self.data_points[-20:]]
        if recent_values:
            min_val = min(recent_values)
            max_val = max(recent_values)
            
            # Add some padding
            if max_val == min_val:
                padding = 10
            else:
                padding = (max_val - min_val) * 0.1
                
            self.y_axis.setRange(
                max(0, min_val - padding), 
                max_val + padding
            )


class SimpleScrollingChartDemo(QWidget):
    """Simple demo showing the generic scrolling chart"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_timer()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Generic Scrolling Line Chart")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Create chart
        self.chart = GenericScrollingChart(
            title="Sample Data", 
            y_label="Values"
        )
        layout.addWidget(self.chart)
        
        # Controls
        controls = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Demo")
        self.stop_btn = QPushButton("Stop Demo")
        add_random_btn = QPushButton("Add Random Point")
        
        self.start_btn.clicked.connect(self.start_demo)
        self.stop_btn.clicked.connect(self.stop_demo)
        add_random_btn.clicked.connect(self.add_random_point)
        
        controls.addWidget(self.start_btn)
        controls.addWidget(self.stop_btn)
        controls.addWidget(add_random_btn)
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Instructions
        instructions = QLabel(
            "• Click 'Start Demo' to see automatic scrolling with random data\n"
            "• Click 'Add Random Point' to manually add data points\n"
            "• Click 'Clear' to remove all data"
        )
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(instructions)
        
    def setup_timer(self):
        """Setup timer for demo data"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.add_demo_data)
        self.timer.setInterval(1000)  # 1 second
        
    def start_demo(self):
        """Start the demo with automatic data"""
        self.timer.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
    def stop_demo(self):
        """Stop the demo"""
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
    def add_demo_data(self):
        """Add a random data point for demo"""
        import random
        import math
        import time
        
        # Generate sample data with some pattern
        t = time.time()
        value = 50 + 30 * math.sin(t * 0.5) + random.uniform(-10, 10)
        value = max(0, min(100, value))  # Clamp to 0-100
        
        self.chart.add_point(value)
        
    def add_random_point(self):
        """Add a single random point"""
        import random
        value = random.uniform(0, 100)
        self.chart.add_point(value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    demo = SimpleScrollingChartDemo()
    demo.setWindowTitle("Generic Scrolling Line Chart")
    demo.resize(800, 600)
    demo.show()
    
    sys.exit(app.exec())