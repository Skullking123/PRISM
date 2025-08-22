#!/usr/bin/env python3
"""
Comprehensive example showing different ways to use the ScrollingLineChart with external data.

This example demonstrates:
1. Setting up a custom data source function
2. Manual data point addition
3. Batch data point addition
4. Integration with real hardware monitoring
5. Custom metric handling
"""

import sys
import time
import math
import random
import threading
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox
from PySide6.QtCore import QTimer
from scrolling_line_chart import ScrollingLineChart


class ChartUsageDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_charts()
        
    def setup_ui(self):
        """Setup the user interface with multiple chart examples"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("ScrollingLineChart Usage Examples")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Chart 1: Data source function example
        layout.addWidget(QLabel("Example 1: Custom Data Source Function"))
        self.chart1 = ScrollingLineChart()
        layout.addWidget(self.chart1)
        
        # Chart 2: Manual data input example
        layout.addWidget(QLabel("Example 2: Manual Data Input"))
        self.chart2 = ScrollingLineChart()
        layout.addWidget(self.chart2)
        
        # Manual controls for chart 2
        manual_controls = QHBoxLayout()
        manual_controls.addWidget(QLabel("Add Value:"))
        
        self.value_input = QSpinBox()
        self.value_input.setRange(0, 100)
        self.value_input.setValue(50)
        manual_controls.addWidget(self.value_input)
        
        add_single_btn = QPushButton("Add Single Point")
        add_single_btn.clicked.connect(self.add_single_point)
        manual_controls.addWidget(add_single_btn)
        
        add_batch_btn = QPushButton("Add Batch Points")
        add_batch_btn.clicked.connect(self.add_batch_points)
        manual_controls.addWidget(add_batch_btn)
        
        manual_controls.addStretch()
        layout.addLayout(manual_controls)
        
        # Instructions
        instructions = QLabel(
            "Chart 1: Uses a custom data source function that generates sine waves\n"
            "Chart 2: Manual data input - use the controls to add individual or batch data points"
        )
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(instructions)
        
    def setup_charts(self):
        """Setup the chart configurations"""
        
        # Chart 1: Custom data source function
        def my_data_source(metric_name: str) -> float:
            """Example data source function"""
            t = time.time()
            
            if "CPU" in metric_name:
                # Simulate CPU usage with sine wave + noise
                return max(0, min(100, 50 + 30 * math.sin(t * 0.5) + random.uniform(-5, 5)))
            elif "Memory" in metric_name:
                # Simulate memory usage with cosine wave
                return max(0, min(32, 16 + 8 * math.cos(t * 0.3) + random.uniform(-1, 1)))
            elif "Temperature" in metric_name:
                # Simulate temperature with slower oscillation
                return max(30, min(90, 65 + 15 * math.sin(t * 0.2) + random.uniform(-2, 2)))
            elif "Custom" in metric_name:
                # Custom metric with complex pattern
                return 50 + 20 * math.sin(t * 0.8) * math.cos(t * 0.3) + random.uniform(-3, 3)
            else:
                return random.uniform(0, 100)
        
        # Set the data source for chart 1
        self.chart1.set_data_source(my_data_source)
        
        # Configure chart 2 for manual input
        self.chart2.metric_combo.setCurrentText("Custom Metric")
        
    def add_single_point(self):
        """Add a single data point to chart 2"""
        value = self.value_input.value()
        self.chart2.add_data_point(value)
        print(f"Added single point: {value}")
        
    def add_batch_points(self):
        """Add multiple data points to chart 2"""
        base_value = self.value_input.value()
        
        # Generate 5 points with some variation
        batch_data = []
        for i in range(5):
            value = base_value + random.uniform(-10, 10)
            batch_data.append(max(0, min(100, value)))
        
        self.chart2.add_multiple_data_points(batch_data)
        print(f"Added batch points: {batch_data}")


class RealTimeDataDemo(QWidget):
    """Example showing how to integrate with real-time data sources"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_data_simulation()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Real-time Data Integration Example")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Create chart
        self.chart = ScrollingLineChart()
        layout.addWidget(self.chart)
        
        # Control buttons
        controls = QHBoxLayout()
        
        start_simulation_btn = QPushButton("Start Data Simulation")
        start_simulation_btn.clicked.connect(self.start_simulation)
        controls.addWidget(start_simulation_btn)
        
        stop_simulation_btn = QPushButton("Stop Data Simulation")
        stop_simulation_btn.clicked.connect(self.stop_simulation)
        controls.addWidget(stop_simulation_btn)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Data source info
        self.data_info = QLabel("Data simulation stopped")
        layout.addWidget(self.data_info)
        
    def setup_data_simulation(self):
        """Setup simulated real-time data source"""
        self.simulation_running = False
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.update_simulated_data)
        
        # Set up the data source function
        def real_time_data_source(metric_name: str) -> float:
            """Simulate getting data from a real system"""
            # In a real application, this would call actual system monitoring APIs
            # like psutil.cpu_percent(), psutil.virtual_memory().percent, etc.
            
            if "CPU" in metric_name:
                # Simulate CPU spikes and normal usage
                if random.random() < 0.1:  # 10% chance of spike
                    return random.uniform(80, 95)
                else:
                    return random.uniform(10, 40)
                    
            elif "Memory" in metric_name:
                # Simulate gradual memory usage changes
                current_time = time.time()
                base_usage = 60 + 20 * math.sin(current_time * 0.1)
                return max(30, min(90, base_usage + random.uniform(-5, 5)))
                
            elif "Temperature" in metric_name:
                # Simulate temperature that responds to CPU load
                cpu_load = random.uniform(10, 80)  # Simulated CPU load
                temp = 40 + (cpu_load * 0.5) + random.uniform(-3, 3)
                return max(35, min(85, temp))
                
            else:
                return random.uniform(0, 100)
        
        self.chart.set_data_source(real_time_data_source)
        
    def start_simulation(self):
        """Start the data simulation"""
        self.simulation_running = True
        self.simulation_timer.start(500)  # Update every 500ms
        self.data_info.setText("Data simulation running - generating realistic system data")
        
    def stop_simulation(self):
        """Stop the data simulation"""
        self.simulation_running = False
        self.simulation_timer.stop()
        self.data_info.setText("Data simulation stopped")
        
    def update_simulated_data(self):
        """Update method for simulation (if needed for additional processing)"""
        # This method could be used for additional data processing
        # or logging before the data goes to the chart
        pass


def example_1_basic_usage():
    """Example 1: Basic usage with a simple data source function"""
    
    app = QApplication(sys.argv)
    
    # Create chart
    chart = ScrollingLineChart()
    
    # Define your data source function
    def my_data_function(metric_name: str) -> float:
        """Your custom data function"""
        if metric_name == "CPU Total":
            return get_cpu_usage()  # Your function to get CPU usage
        elif metric_name == "Memory Used":
            return get_memory_usage()  # Your function to get memory usage
        else:
            return 0.0
    
    # Set the data source
    chart.set_data_source(my_data_function)
    
    # Show and start
    chart.show()
    chart.start_chart()
    
    return app.exec()


def example_2_manual_data():
    """Example 2: Manual data input"""
    
    app = QApplication(sys.argv)
    
    # Create chart
    chart = ScrollingLineChart()
    chart.show()
    
    # Add data points manually
    chart.add_data_point(25.5)
    chart.add_data_point(67.2)
    chart.add_data_point(89.1)
    
    # Add multiple points at once
    data_batch = [42.8, 15.3, 78.9, 33.1]
    chart.add_multiple_data_points(data_batch)
    
    return app.exec()


# Placeholder functions for example 1
def get_cpu_usage():
    """Placeholder - replace with your actual CPU monitoring function"""
    return random.uniform(0, 100)

def get_memory_usage():
    """Placeholder - replace with your actual memory monitoring function"""
    return random.uniform(0, 32)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Show the comprehensive demo
    demo = ChartUsageDemo()
    demo.setWindowTitle("ScrollingLineChart Usage Examples")
    demo.resize(1200, 800)
    demo.show()
    
    # Start automatic updates on chart 1
    demo.chart1.start_chart()
    
    sys.exit(app.exec())