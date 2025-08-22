#!/usr/bin/env python3
"""
Simple test script for ScrollingLineChart functionality.
Run this to verify the chart works correctly.
"""

import sys
import math
import random
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor
from ScrollingLineChart import ScrollingLineChart

class ScrollingChartTest(QWidget):
    """Test widget for ScrollingLineChart"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ScrollingLineChart Test")
        self.setMinimumSize(800, 600)
        
        # Setup layout
        layout = QVBoxLayout(self)
        
        # Create chart
        self.chart = ScrollingLineChart()
        self.chart.set_chart_title("Test Chart - Multiple Data Series")
        self.chart.set_axis_titles("Time (seconds)", "Value")
        self.chart.set_max_data_points(100)
        
        # Add test series
        self.chart.add_series("Sine Wave", QColor(255, 99, 132))
        self.chart.add_series("Cosine Wave", QColor(54, 162, 235))
        self.chart.add_series("Random Walk", QColor(255, 205, 86))
        
        layout.addWidget(self.chart)
        
        # Control panel
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start Test")
        self.start_btn.clicked.connect(self.start_test)
        
        self.stop_btn = QPushButton("Stop Test")
        self.stop_btn.clicked.connect(self.stop_test)
        
        self.clear_btn = QPushButton("Clear Data")
        self.clear_btn.clicked.connect(self.clear_data)
        
        self.toggle_scroll_btn = QPushButton("Toggle Auto-Scroll")
        self.toggle_scroll_btn.clicked.connect(self.toggle_scroll)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.clear_btn)
        control_layout.addWidget(self.toggle_scroll_btn)
        control_layout.addStretch()
        
        # Status label
        self.status_label = QLabel("Status: Ready")
        control_layout.addWidget(self.status_label)
        
        layout.addLayout(control_layout)
        
        # Test data generation
        self.time = 0.0
        self.random_value = 0.0
        self.timer = QTimer()
        self.timer.timeout.connect(self.generate_test_data)
        
        # Start test automatically
        self.start_test()
    
    def start_test(self):
        """Start generating test data"""
        self.timer.start(100)  # Update every 100ms
        self.status_label.setText("Status: Running test data generation")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
    
    def stop_test(self):
        """Stop generating test data"""
        self.timer.stop()
        self.status_label.setText("Status: Stopped")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def clear_data(self):
        """Clear all chart data"""
        self.chart.clear_all_data()
        self.time = 0.0
        self.random_value = 0.0
        self.status_label.setText("Status: Data cleared")
    
    def toggle_scroll(self):
        """Toggle auto-scroll functionality"""
        self.chart.toggle_auto_scroll()
        scroll_status = "enabled" if self.chart.auto_scroll else "disabled"
        self.status_label.setText(f"Status: Auto-scroll {scroll_status}")
    
    def generate_test_data(self):
        """Generate test data for the chart"""
        # Generate different types of data patterns
        
        # Sine wave
        sine_value = 50 + 30 * math.sin(self.time * 0.2)
        
        # Cosine wave (phase shifted)
        cosine_value = 50 + 25 * math.cos(self.time * 0.15 + math.pi/4)
        
        # Random walk
        self.random_value += random.uniform(-2, 2)
        self.random_value = max(0, min(100, self.random_value))  # Clamp to 0-100
        
        # Add data points
        self.chart.add_data_point("Sine Wave", self.time, sine_value)
        self.chart.add_data_point("Cosine Wave", self.time, cosine_value)
        self.chart.add_data_point("Random Walk", self.time, self.random_value)
        
        # Update time
        self.time += 0.1
        
        # Update status with latest values
        data_points = len(self.chart.get_series_data("Sine Wave"))
        self.status_label.setText(f"Status: Running | Data points: {data_points} | Time: {self.time:.1f}s")


def main():
    """Run the test"""
    print("Starting ScrollingLineChart test...")
    print("This will create a window with a scrolling line chart showing:")
    print("- Sine wave (red)")
    print("- Cosine wave (blue)") 
    print("- Random walk (yellow)")
    print("\nUse the control buttons to:")
    print("- Start/Stop data generation")
    print("- Clear all data")
    print("- Toggle auto-scroll on/off")
    print("\nThe chart should automatically scroll and maintain a buffer of the last 100 data points.")
    
    app = QApplication(sys.argv)
    
    # Create and show test window
    test_widget = ScrollingChartTest()
    test_widget.show()
    
    print("\nTest window opened. Close the window to exit.")
    
    # Run the application
    result = app.exec()
    
    print("Test completed.")
    return result


if __name__ == "__main__":
    sys.exit(main())