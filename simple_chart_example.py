#!/usr/bin/env python3
"""
Simple example of using the GenericScrollingChart
"""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import QTimer
from generic_scrolling_chart import GenericScrollingChart


def basic_usage_example():
    """Basic usage example"""
    
    app = QApplication(sys.argv)
    
    # Create a simple chart
    chart = GenericScrollingChart(title="My Data", y_label="Temperature °C")
    
    # Add some data points
    chart.add_point(25.5)
    chart.add_point(27.2)
    chart.add_point(29.1)
    
    # Add multiple points
    chart.add_points([30.5, 32.1, 28.9, 26.7])
    
    # Set Y-axis range if needed
    chart.set_y_range(0, 50)
    
    # Show the chart
    chart.show()
    chart.resize(600, 400)
    
    return app.exec()


class MyApp(QWidget):
    """Example of integrating the chart into your own application"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_data_timer()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create chart
        self.chart = GenericScrollingChart(
            title="Live Sensor Data", 
            y_label="Sensor Reading"
        )
        layout.addWidget(self.chart)
        
        # Add control button
        self.toggle_btn = QPushButton("Start Data Stream")
        self.toggle_btn.clicked.connect(self.toggle_data_stream)
        layout.addWidget(self.toggle_btn)
        
        self.data_running = False
        
    def setup_data_timer(self):
        """Setup timer for simulated data"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.add_sensor_data)
        self.timer.setInterval(500)  # Every 500ms
        
    def toggle_data_stream(self):
        """Start/stop the data stream"""
        if self.data_running:
            self.timer.stop()
            self.toggle_btn.setText("Start Data Stream")
            self.data_running = False
        else:
            self.timer.start()
            self.toggle_btn.setText("Stop Data Stream")
            self.data_running = True
            
    def add_sensor_data(self):
        """Simulate getting sensor data"""
        import random
        
        # Simulate sensor reading
        sensor_value = random.uniform(20, 80)
        
        # Add to chart
        self.chart.add_point(sensor_value)


if __name__ == "__main__":
    # Run the integrated app example
    app = QApplication(sys.argv)
    
    my_app = MyApp()
    my_app.setWindowTitle("Simple Chart Integration")
    my_app.resize(700, 500)
    my_app.show()
    
    sys.exit(app.exec())