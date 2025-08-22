import sys
import random
import pandas as pd
from datetime import datetime, timedelta
from typing import Callable, Optional, Any
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PySide6.QtCore import QTimer, QDateTime, Qt, QPointF
from PySide6.QtGui import QPen, QColor


class ScrollingLineChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_chart()
        self.setup_timer()
        self.data_points = []
        self.max_points = 100  # Maximum number of points to display
        self.time_window = 60  # Time window in seconds
        
        # Data source function - can be set externally
        self.data_source_function: Optional[Callable[[str], float]] = None
        
        # Load sample data for fallback (optional)
        self.load_sample_data()
        
    def set_data_source(self, data_function: Callable[[str], float]):
        """
        Set an external function to provide data for the chart.
        
        Args:
            data_function: A function that takes a metric name (str) and returns a float value
                          Example: lambda metric_name: get_cpu_usage() if metric_name == "CPU Total" else 0.0
        """
        self.data_source_function = data_function
        
    def add_data_point(self, value: float, timestamp: Optional[QDateTime] = None):
        """
        Manually add a single data point to the chart.
        
        Args:
            value: The data value to add
            timestamp: Optional timestamp, uses current time if None
        """
        if timestamp is None:
            timestamp = QDateTime.currentDateTime()
            
        point = QPointF(timestamp.toMSecsSinceEpoch(), value)
        self.data_points.append(point)
        
        # Remove old points if we exceed max_points
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
            
        # Update the chart
        self._update_chart_display()
        
    def add_multiple_data_points(self, data_points: list):
        """
        Add multiple data points at once.
        
        Args:
            data_points: List of tuples (value, timestamp) or (value,) for current time
        """
        for data_point in data_points:
            if isinstance(data_point, tuple):
                if len(data_point) == 2:
                    value, timestamp = data_point
                    self.add_data_point(value, timestamp)
                else:
                    value = data_point[0]
                    self.add_data_point(value)
            else:
                # Single value
                self.add_data_point(data_point)

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Control panel
        control_panel = QHBoxLayout()
        
        # Metric selector
        self.metric_label = QLabel("Metric:")
        self.metric_combo = QComboBox()
        self.metric_combo.addItems([
            "CPU Total", "Memory Used", "GPU Core", "GPU Memory",
            "Temperature", "Network Upload", "Network Download", "Custom Metric"
        ])
        self.metric_combo.currentTextChanged.connect(self.change_metric)
        
        # Control buttons
        self.start_btn = QPushButton("Start Auto-Update")
        self.stop_btn = QPushButton("Stop Auto-Update")
        self.clear_btn = QPushButton("Clear")
        
        self.start_btn.clicked.connect(self.start_chart)
        self.stop_btn.clicked.connect(self.stop_chart)
        self.clear_btn.clicked.connect(self.clear_chart)
        
        # Add to control panel
        control_panel.addWidget(self.metric_label)
        control_panel.addWidget(self.metric_combo)
        control_panel.addStretch()
        control_panel.addWidget(self.start_btn)
        control_panel.addWidget(self.stop_btn)
        control_panel.addWidget(self.clear_btn)
        
        layout.addLayout(control_panel)
        
        # Chart view will be added in setup_chart
        
    def setup_chart(self):
        """Setup the chart and its components"""
        # Create chart
        self.chart = QChart()
        self.chart.setTitle("Real-time Data Monitoring")
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        # Create series
        self.series = QLineSeries()
        self.series.setName("Data Series")
        
        # Style the series
        pen = QPen(QColor(0, 120, 215), 2)  # Blue color, 2px width
        self.series.setPen(pen)
        
        # Add series to chart
        self.chart.addSeries(self.series)
        
        # Create axes
        self.x_axis = QDateTimeAxis()
        self.x_axis.setFormat("hh:mm:ss")
        self.x_axis.setTitleText("Time")
        self.x_axis.setTickCount(6)
        
        self.y_axis = QValueAxis()
        self.y_axis.setTitleText("Value")
        self.y_axis.setRange(0, 100)
        
        # Add axes to chart
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        
        # Attach axes to series
        self.series.attachAxis(self.x_axis)
        self.series.attachAxis(self.y_axis)
        
        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(self.chart_view.RenderHint.Antialiasing)
        
        # Add chart view to layout
        self.layout().addWidget(self.chart_view)
        
    def setup_timer(self):
        """Setup the update timer"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_chart_with_external_data)
        self.timer.setInterval(1000)  # Update every second
        
    def load_sample_data(self):
        """Load sample data from CSV if available (for fallback only)"""
        try:
            self.df = pd.read_csv('/workspace/hardware_usage_log.csv')
            print(f"Loaded {len(self.df)} data points from CSV (fallback data)")
        except FileNotFoundError:
            print("No CSV file found, will use external data source or generate random data")
            self.df = None
            
    def start_chart(self):
        """Start the automatic chart updates"""
        if self.data_source_function is None:
            print("Warning: No data source function set. Chart will use fallback data.")
        
        self.timer.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
    def stop_chart(self):
        """Stop the automatic chart updates"""
        self.timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
    def clear_chart(self):
        """Clear all data from the chart"""
        self.series.clear()
        self.data_points.clear()
        
    def change_metric(self, metric_name):
        """Change the displayed metric"""
        self.series.setName(metric_name)
        self.chart.setTitle(f"Real-time {metric_name} Monitoring")
        
        # Adjust Y-axis range based on metric
        if "Temperature" in metric_name:
            self.y_axis.setRange(0, 100)
            self.y_axis.setTitleText("Temperature (°C)")
        elif "Memory" in metric_name:
            self.y_axis.setRange(0, 32)  # Assuming 32GB max
            self.y_axis.setTitleText("Memory (GB)")
        elif "Network" in metric_name:
            self.y_axis.setRange(0, 1000)  # Assuming Mbps
            self.y_axis.setTitleText("Speed (Mbps)")
        elif "Custom" in metric_name:
            self.y_axis.setRange(0, 100)  # Default range for custom metrics
            self.y_axis.setTitleText("Custom Value")
        else:
            self.y_axis.setRange(0, 100)
            self.y_axis.setTitleText("Usage (%)")
            
        # Clear existing data when changing metrics
        self.clear_chart()
        
    def get_sample_value(self, metric_name):
        """Get a sample value for the given metric (fallback method)"""
        if self.df is not None and len(self.df) > 0:
            # Use real data from CSV
            row_idx = random.randint(0, len(self.df) - 1)
            row = self.df.iloc[row_idx]
            
            if metric_name == "CPU Total" and "CPU Total" in row:
                return float(row["CPU Total"])
            elif metric_name == "Memory Used" and "Memory Used" in row:
                return float(row["Memory Used"])
            elif metric_name == "GPU Core" and len(row) > 45:
                return float(row.iloc[45])  # GPU Core column
            elif metric_name == "GPU Memory" and len(row) > 46:
                return float(row.iloc[46])  # GPU Memory column
            elif metric_name == "Temperature" and len(row) > 82:
                return float(row.iloc[82])  # Temperature column
            elif metric_name == "Network Upload" and len(row) > 102:
                return float(row.iloc[102]) if row.iloc[102] != 0 else random.uniform(0, 100)
            elif metric_name == "Network Download" and len(row) > 103:
                return float(row.iloc[103]) if row.iloc[103] != 0 else random.uniform(0, 100)
        
        # Fallback to random data
        if "Temperature" in metric_name:
            return random.uniform(30, 80)
        elif "Memory" in metric_name:
            return random.uniform(8, 24)
        elif "Network" in metric_name:
            return random.uniform(0, 500)
        elif "Custom" in metric_name:
            return random.uniform(0, 100)
        else:
            return random.uniform(10, 90)
            
    def update_chart_with_external_data(self):
        """Update the chart using external data source or fallback"""
        current_metric = self.metric_combo.currentText()
        
        # Try to get value from external data source first
        if self.data_source_function is not None:
            try:
                value = self.data_source_function(current_metric)
            except Exception as e:
                print(f"Error getting data from external source: {e}")
                value = self.get_sample_value(current_metric)
        else:
            # Use fallback data
            value = self.get_sample_value(current_metric)
        
        # Add the new data point
        self.add_data_point(value)
        
    def _update_chart_display(self):
        """Internal method to update the chart display"""
        # Update series
        self.series.replace(self.data_points)
        
        # Update X-axis range to show scrolling effect
        if len(self.data_points) > 1:
            latest_time = QDateTime.fromMSecsSinceEpoch(int(self.data_points[-1].x()))
            earliest_time = latest_time.addSecs(-self.time_window)
            
            self.x_axis.setRange(earliest_time, latest_time)
            
        # Auto-scale Y-axis based on visible data
        if len(self.data_points) > 0:
            visible_values = [p.y() for p in self.data_points[-20:]]  # Last 20 points
            if visible_values:
                min_val = min(visible_values)
                max_val = max(visible_values)
                padding = (max_val - min_val) * 0.1 if max_val != min_val else 10
                
                self.y_axis.setRange(max(0, min_val - padding), max_val + padding)

    # Legacy method for backward compatibility
    def update_chart(self):
        """Legacy method - use update_chart_with_external_data instead"""
        self.update_chart_with_external_data()


class ScrollingLineChartDemo(QWidget):
    """Demo widget showing how to use the chart with external data"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_data_source()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Scrolling Line Chart - External Data Demo")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Create chart
        self.chart = ScrollingLineChart()
        layout.addWidget(self.chart)
        
        # Instructions
        instructions = QLabel(
            "• Chart now uses external data source function\n"
            "• Select different metrics from the dropdown\n"
            "• Click 'Start Auto-Update' for automatic updates\n"
            "• Or use add_data_point() to manually add data\n"
            "• Data source function can be customized via set_data_source()"
        )
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(instructions)
        
        # Manual data input demo
        manual_controls = QHBoxLayout()
        manual_label = QLabel("Manual Input:")
        self.manual_input = QComboBox()
        self.manual_input.setEditable(True)
        self.manual_input.addItems(["25.5", "67.2", "89.1", "42.8", "15.3"])
        
        add_point_btn = QPushButton("Add Data Point")
        add_point_btn.clicked.connect(self.add_manual_point)
        
        manual_controls.addWidget(manual_label)
        manual_controls.addWidget(self.manual_input)
        manual_controls.addWidget(add_point_btn)
        manual_controls.addStretch()
        
        layout.addLayout(manual_controls)
        
    def setup_data_source(self):
        """Setup the external data source function"""
        def custom_data_source(metric_name: str) -> float:
            """Custom data source function - replace this with your own logic"""
            import time
            import math
            
            # Generate different patterns based on metric name
            t = time.time()
            
            if "CPU" in metric_name:
                return 50 + 30 * math.sin(t * 0.5) + random.uniform(-5, 5)
            elif "Memory" in metric_name:
                return 16 + 8 * math.cos(t * 0.3) + random.uniform(-1, 1)
            elif "Temperature" in metric_name:
                return 65 + 15 * math.sin(t * 0.2) + random.uniform(-2, 2)
            elif "Network" in metric_name:
                return abs(200 * math.sin(t * 0.8)) + random.uniform(0, 50)
            elif "GPU" in metric_name:
                return 40 + 35 * math.cos(t * 0.6) + random.uniform(-8, 8)
            else:
                return random.uniform(0, 100)
        
        # Set the data source for the chart
        self.chart.set_data_source(custom_data_source)
        
    def add_manual_point(self):
        """Add a manual data point to the chart"""
        try:
            value = float(self.manual_input.currentText())
            self.chart.add_data_point(value)
            print(f"Added manual data point: {value}")
        except ValueError:
            print("Invalid input - please enter a numeric value")


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    demo = ScrollingLineChartDemo()
    demo.show()
    demo.resize(1000, 700)
    sys.exit(app.exec())