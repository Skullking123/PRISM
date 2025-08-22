import sys
import random
import pandas as pd
from datetime import datetime, timedelta
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
        
        # Load sample data if available
        self.load_sample_data()
        
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
            "Temperature", "Network Upload", "Network Download"
        ])
        self.metric_combo.currentTextChanged.connect(self.change_metric)
        
        # Control buttons
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
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
        self.chart.setTitle("Real-time Hardware Monitoring")
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        # Create series
        self.series = QLineSeries()
        self.series.setName("CPU Total")
        
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
        self.y_axis.setTitleText("Value (%)")
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
        self.timer.timeout.connect(self.update_chart)
        self.timer.setInterval(1000)  # Update every second
        
    def load_sample_data(self):
        """Load sample data from CSV if available"""
        try:
            self.df = pd.read_csv('/workspace/hardware_usage_log.csv')
            print(f"Loaded {len(self.df)} data points from CSV")
        except FileNotFoundError:
            print("No CSV file found, will generate random data")
            self.df = None
            
    def start_chart(self):
        """Start the chart updates"""
        self.timer.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
    def stop_chart(self):
        """Stop the chart updates"""
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
        else:
            self.y_axis.setRange(0, 100)
            self.y_axis.setTitleText("Usage (%)")
            
        # Clear existing data when changing metrics
        self.clear_chart()
        
    def get_sample_value(self, metric_name):
        """Get a sample value for the given metric"""
        if self.df is not None and len(self.df) > 0:
            # Use real data from CSV
            row_idx = random.randint(0, len(self.df) - 1)
            row = self.df.iloc[row_idx]
            
            if metric_name == "CPU Total" and "CPU Total" in row:
                return float(row["CPU Total"])
            elif metric_name == "Memory Used" and "Memory Used" in row:
                return float(row["Memory Used"])
            elif metric_name == "GPU Core" and "GPU Core" in row:
                return float(row.iloc[45])  # GPU Core column
            elif metric_name == "GPU Memory" and "GPU Memory" in row:
                return float(row.iloc[46])  # GPU Memory column
            elif metric_name == "Temperature":
                return float(row.iloc[82])  # Temperature column
            elif metric_name == "Network Upload":
                return float(row.iloc[102]) if row.iloc[102] != 0 else random.uniform(0, 100)
            elif metric_name == "Network Download":
                return float(row.iloc[103]) if row.iloc[103] != 0 else random.uniform(0, 100)
        
        # Fallback to random data
        if "Temperature" in metric_name:
            return random.uniform(30, 80)
        elif "Memory" in metric_name:
            return random.uniform(8, 24)
        elif "Network" in metric_name:
            return random.uniform(0, 500)
        else:
            return random.uniform(10, 90)
            
    def update_chart(self):
        """Update the chart with new data"""
        current_time = QDateTime.currentDateTime()
        current_metric = self.metric_combo.currentText()
        
        # Get new value
        value = self.get_sample_value(current_metric)
        
        # Add new point
        point = QPointF(current_time.toMSecsSinceEpoch(), value)
        self.data_points.append(point)
        
        # Remove old points if we exceed max_points
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
            
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


class ScrollingLineChartDemo(QWidget):
    """Demo widget showing multiple charts"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Scrolling Line Chart Demo")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Create chart
        self.chart = ScrollingLineChart()
        layout.addWidget(self.chart)
        
        # Instructions
        instructions = QLabel(
            "• Select different metrics from the dropdown\n"
            "• Click Start to begin real-time updates\n"
            "• Chart automatically scrolls to show latest data\n"
            "• Uses real hardware data if CSV file is available"
        )
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(instructions)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    demo = ScrollingLineChartDemo()
    demo.show()
    demo.resize(800, 600)
    sys.exit(app.exec())