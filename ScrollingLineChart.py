import sys
import math
from collections import deque
import time
from typing import List, Tuple, Optional, Dict, Any
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, QPointF, Signal
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics
from PySide6.QtCharts import (QChart, QChartView, QLineSeries, QValueAxis, 
                              QDateTimeAxis, QAbstractSeries)

class ScrollingLineChart(QWidget):
    """
    A generic scrolling line chart widget that can display real-time data.
    Features:
    - Multiple data series support
    - Automatic scrolling with configurable buffer size
    - Customizable styling and colors
    - Real-time data updates
    - Smooth animations
    - Grid lines and axis labels
    """
    
    # Signal emitted when data point is added
    dataPointAdded = Signal(str, float)  # series_name, x_value, y_value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        
        # Chart configuration
        self.max_data_points = 100  # Maximum points to keep in buffer
        self.auto_scroll = True
        self.show_grid = True
        self.show_legend = True
        self.start = -1
        # self.animation_enabled = True
        
        # Data storage - each series has its own deque buffer
        self.data_series: Dict[str, deque] = {}
        self.series_colors: Dict[str, QColor] = {}
        self.series_objects: Dict[str, QLineSeries] = {}
        
        # Default colors for multiple series
        self.default_colors = [
            QColor(75, 192, 192),   # Teal
            QColor(255, 99, 132),   # Red
            QColor(54, 162, 235),   # Blue
            QColor(255, 205, 86),   # Yellow
            QColor(153, 102, 255),  # Purple
            QColor(255, 159, 64),   # Orange
            QColor(199, 199, 199),  # Grey
            QColor(83, 102, 255),   # Indigo
        ]
        self.color_index = 0
        
        # Setup chart
        self.setupChart()
        self.setupLayout()
        
        # Timer for auto-updating (optional)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_chart)
    
    def setupChart(self):
        """Initialize the Qt chart and its components"""
        # Create chart
        self.chart = QChart()
        self.chart.setTitle("Scrolling Line Chart")
        # self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations if self.animation_enabled else QChart.AnimationOption.NoAnimation)
        
        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Setup axes
        self.x_axis = QValueAxis()
        self.x_axis.setTitleText("Time/Index")
        self.x_axis.setLabelFormat("%.1f")
        
        self.y_axis = QValueAxis()
        self.y_axis.setTitleText("Value")
        self.y_axis.setLabelFormat("%.2f")
        
        # Add axes to chart
        self.chart.addAxis(self.x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.y_axis, Qt.AlignmentFlag.AlignLeft)
        
        # Configure grid and theme
        self.chart.setTheme(QChart.ChartTheme.ChartThemeLight)
        if self.show_grid:
            self.x_axis.setGridLineVisible(True)
            self.y_axis.setGridLineVisible(True)
    
    def setupLayout(self):
        """Setup the widget layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.chart_view)
        
        # Control panel (optional)
        self.control_panel = QFrame()
        control_layout = QHBoxLayout(self.control_panel)
        control_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add control buttons
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_auto_scroll)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_all_data)
        
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.clear_button)
        control_layout.addStretch()
        
        layout.addWidget(self.control_panel)
    
    def add_series(self, series_name: str, color: Optional[QColor] = None) -> bool:
        """
        Add a new data series to the chart
        
        Args:
            series_name: Unique name for the series
            color: Optional color for the series line
            
        Returns:
            True if series was added successfully, False if series already exists
        """
        if series_name in self.data_series:
            return False
        
        # Create data buffer
        self.data_series[series_name] = deque(maxlen=self.max_data_points)
        
        # Assign color
        if color is None:
            color = self.default_colors[self.color_index % len(self.default_colors)]
            self.color_index += 1
        self.series_colors[series_name] = color
        
        # Create Qt series object
        series = QLineSeries()
        series.setName(series_name)
        series.setColor(color)
        
        # Add to chart
        self.chart.addSeries(series)
        series.attachAxis(self.x_axis)
        series.attachAxis(self.y_axis)
        
        self.series_objects[series_name] = series
        
        # Update legend visibility
        self.chart.legend().setVisible(self.show_legend and len(self.data_series) > 1)
        
        return True
    
    def remove_series(self, series_name: str) -> bool:
        """Remove a data series from the chart"""
        if series_name not in self.data_series:
            return False
        
        # Remove from chart
        self.chart.removeSeries(self.series_objects[series_name])
        
        # Clean up data structures
        del self.data_series[series_name]
        del self.series_colors[series_name]
        del self.series_objects[series_name]
        
        # Update legend visibility
        self.chart.legend().setVisible(self.show_legend and len(self.data_series) > 1)
        
        return True
    
    def add_data_point(self, series_name: str, y_value: float):
        """
        Add a new data point to the specified series
        
        Args:
            series_name: Name of the series to add data to
            y_value: Y coordinate (the measured value)
        """
        # Create series if it doesn't exist
        if series_name not in self.data_series:
            self.add_series(series_name)
        if self.start == -1:
            self.start = time.perf_counter()
        # Add data point to buffer
        now = time.perf_counter()
        self.data_series[series_name].append((now - self.start, y_value))

        # Update the Qt series
        self.update_series_data(series_name)
        
        # Auto-adjust axes if needed
        if self.auto_scroll:
            self.auto_adjust_axes()
        
        # Emit signal
        self.dataPointAdded.emit(series_name, y_value)
    
    def add_data_points(self, series_name: str, points: List[Tuple[float, float]]):
        """Add multiple data points at once"""
        if series_name not in self.data_series:
            self.add_series(series_name)
        
        for x_val, y_val in points:
            self.data_series[series_name].append((x_val, y_val))
        
        self.update_series_data(series_name)
        
        if self.auto_scroll:
            self.auto_adjust_axes()
    
    def update_series_data(self, series_name: str):
        """Update the Qt series object with current buffer data"""
        if series_name not in self.series_objects:
            return
        
        series = self.series_objects[series_name]
        data = self.data_series[series_name]
        
        # Clear existing data
        series.clear()
        
        # Add all points from buffer
        for x_val, y_val in data:
            series.append(QPointF(x_val, y_val))
    
    def auto_adjust_axes(self):
        """Automatically adjust axis ranges based on current data"""
        if not self.data_series:
            return
        
        # Find data ranges across all series
        all_x_values = []
        all_y_values = []
        total_points = 0
        
        for data in self.data_series.values():
            if data:
                x_vals = [point[0] for point in data]
                y_vals = [point[1] for point in data]
                all_x_values.extend(x_vals)
                all_y_values.extend(y_vals)
                total_points = max(total_points, len(data))

        if not all_x_values or not all_y_values:
            return
        
        # Set axis ranges with some padding
        x_min, x_max = min(all_x_values), max(all_x_values)
        y_min, y_max = 0, max(all_y_values)
        
        # Add padding
        x_padding = (x_max - x_min) * 0.05 if x_max != x_min else 1.0
        y_padding = (y_max - y_min) * 0.1 if y_max != y_min else 1.0
        
        if total_points > 100:
            if (x_min - x_padding) < 0:
                self.x_axis.setRange(0, x_max + x_padding)
            else:
                self.x_axis.setRange(x_min - x_padding, x_max + x_padding)
        else:
            if (x_min - x_padding) < 0:
                self.x_axis.setRange(0, x_max + x_padding)
            else:
                self.x_axis.setRange(x_min - x_padding, x_max + x_padding)
        self.y_axis.setRange(0, y_max + y_padding)
    
    def set_axis_ranges(self, x_min: float, x_max: float, y_min: float, y_max: float):
        """Manually set axis ranges"""
        self.x_axis.setRange(x_min, x_max)
        self.y_axis.setRange(y_min, y_max)
    
    def clear_series_data(self, series_name: str):
        """Clear all data for a specific series"""
        if series_name in self.data_series:
            self.data_series[series_name].clear()
            self.update_series_data(series_name)
    
    def clear_all_data(self):
        """Clear all data from all series"""
        for series_name in self.data_series.keys():
            self.clear_series_data(series_name)
    
    def set_max_data_points(self, max_points: int):
        """Set the maximum number of data points to keep in buffer"""
        self.max_data_points = max_points
        
        # Update existing buffers
        for series_name, data in self.data_series.items():
            new_deque = deque(data, maxlen=max_points)
            self.data_series[series_name] = new_deque
            self.update_series_data(series_name)
    
    def toggle_auto_scroll(self):
        """Toggle automatic scrolling on/off"""
        self.auto_scroll = not self.auto_scroll
        self.pause_button.setText("Resume" if not self.auto_scroll else "Pause")
    
    def set_chart_title(self, title: str):
        """Set the chart title"""
        self.chart.setTitle(title)
    
    def set_axis_titles(self, x_title: str, y_title: str):
        """Set axis titles"""
        self.x_axis.setTitleText(x_title)
        self.y_axis.setTitleText(y_title)
    
    def set_theme(self, theme: QChart.ChartTheme):
        """Set the chart theme"""
        self.chart.setTheme(theme)
    
    def enable_legend(self, enabled: bool):
        """Enable/disable the legend"""
        self.show_legend = enabled
        self.chart.legend().setVisible(enabled and len(self.data_series) > 1)
    
    def enable_grid(self, enabled: bool):
        """Enable/disable grid lines"""
        self.show_grid = enabled
        self.x_axis.setGridLineVisible(enabled)
        self.y_axis.setGridLineVisible(enabled)
    
    def start_auto_update(self, interval_ms: int = 100):
        """Start automatic chart updates at specified interval"""
        self.update_timer.start(interval_ms)
    
    def stop_auto_update(self):
        """Stop automatic chart updates"""
        self.update_timer.stop()
    
    def refresh_chart(self):
        """Refresh the chart display - can be connected to a timer"""
        if self.auto_scroll:
            self.auto_adjust_axes()
        self.chart_view.update()
    
    def get_series_names(self) -> List[str]:
        """Get list of all series names"""
        return list(self.data_series.keys())
    
    def get_series_data(self, series_name: str) -> List[Tuple[float, float]]:
        """Get all data points for a specific series"""
        if series_name in self.data_series:
            return list(self.data_series[series_name])
        return []
    
    def get_latest_value(self, series_name: str) -> Optional[Tuple[float, float]]:
        """Get the most recent data point for a series"""
        if series_name in self.data_series and self.data_series[series_name]:
            return self.data_series[series_name][-1]
        return None


# Example usage and demo functions
class ScrollingLineChartDemo(QWidget):
    """Demo widget showing how to use the ScrollingLineChart"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Scrolling Line Chart Demo")
        self.setMinimumSize(800, 600)
        
        # Setup layout
        layout = QVBoxLayout(self)
        
        # Create chart
        self.chart = ScrollingLineChart(self)
        self.chart.set_chart_title("Real-time Data Demo")
        self.chart.set_axis_titles("Time (seconds)", "Value")
        
        # Add some demo series
        self.chart.add_series("CPU Usage", QColor(255, 99, 132))
        self.chart.add_series("Memory Usage", QColor(54, 162, 235))
        self.chart.add_series("Temperature", QColor(255, 205, 86))
        
        layout.addWidget(self.chart)
        
        # Demo data generation
        self.time_counter = 0.0
        self.demo_timer = QTimer()
        self.demo_timer.timeout.connect(self.generate_demo_data)
        self.demo_timer.start(100)  # Update every 100ms
        
        # Control buttons
        control_frame = QFrame()
        control_layout = QHBoxLayout(control_frame)
        
        start_btn = QPushButton("Start Demo")
        start_btn.clicked.connect(lambda: self.demo_timer.start(100))
        
        stop_btn = QPushButton("Stop Demo")
        stop_btn.clicked.connect(self.demo_timer.stop)
        
        control_layout.addWidget(start_btn)
        control_layout.addWidget(stop_btn)
        control_layout.addStretch()
        
        layout.addWidget(control_frame)
    
    def generate_demo_data(self):
        """Generate sample data for demonstration"""
        import random
        
        # Generate realistic-looking data
        cpu_usage = 30 + 20 * math.sin(self.time_counter * 0.1) + random.uniform(-5, 5)
        memory_usage = 45 + 15 * math.cos(self.time_counter * 0.08) + random.uniform(-3, 3)
        temperature = 65 + 10 * math.sin(self.time_counter * 0.05) + random.uniform(-2, 2)
        
        # Add data points
        self.chart.add_data_point("CPU Usage", self.time_counter, cpu_usage)
        self.chart.add_data_point("Memory Usage", self.time_counter, memory_usage)
        self.chart.add_data_point("Temperature", self.time_counter, temperature)
        
        self.time_counter += 0.1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create and show demo
    demo = ScrollingLineChartDemo()
    demo.show()
    
    sys.exit(app.exec())
