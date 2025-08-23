#!/usr/bin/env python3
"""
Example integration of ScrollingLineChart with the existing PRISM Hardware Monitor application.
This demonstrates how to use the chart component in a real application.
"""

import sys
import time
import random
import math
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFrame, QTabWidget)
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor
from ScrollingLineChart import ScrollingLineChart

class HardwareMonitorExample(QWidget):
    """Example showing how to integrate the scrolling chart with hardware monitoring"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hardware Monitor with Scrolling Charts")
        self.setMinimumSize(1000, 700)
        
        # Setup main layout
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for different chart views
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Setup different monitoring tabs
        self.setup_cpu_tab()
        self.setup_memory_tab()
        self.setup_temperature_tab()
        self.setup_combined_tab()
        
        # Data simulation timer
        self.time_counter = 0.0
        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.update_data)
        self.data_timer.start(500)  # Update every 500ms
        
        # Control panel
        self.setup_control_panel()
        main_layout.addWidget(self.control_frame)
    
    def setup_cpu_tab(self):
        """Setup CPU monitoring chart"""
        cpu_widget = QWidget()
        layout = QVBoxLayout(cpu_widget)
        
        # Create CPU usage chart
        self.cpu_chart = ScrollingLineChart()
        self.cpu_chart.set_chart_title("CPU Usage Monitor")
        self.cpu_chart.set_axis_titles("Time (seconds)", "Usage (%)")
        self.cpu_chart.set_max_data_points(150)  # Keep 150 data points
        
        # Add CPU cores as separate series
        self.cpu_chart.add_series("CPU Core 1", QColor(255, 99, 132))
        self.cpu_chart.add_series("CPU Core 2", QColor(54, 162, 235))
        self.cpu_chart.add_series("CPU Core 3", QColor(255, 205, 86))
        self.cpu_chart.add_series("CPU Core 4", QColor(75, 192, 192))
        
        # Set fixed Y-axis range for CPU percentage
        self.cpu_chart.set_axis_ranges(0, 30, 0, 100)
        self.cpu_chart.auto_scroll = False  # Use fixed range for CPU
        
        layout.addWidget(self.cpu_chart)
        
        # Add info panel
        info_panel = QFrame()
        info_layout = QHBoxLayout(info_panel)
        self.cpu_info_label = QLabel("CPU Info: Waiting for data...")
        info_layout.addWidget(self.cpu_info_label)
        layout.addWidget(info_panel)
        
        self.tab_widget.addTab(cpu_widget, "CPU Usage")
    
    def setup_memory_tab(self):
        """Setup memory monitoring chart"""
        memory_widget = QWidget()
        layout = QVBoxLayout(memory_widget)
        
        # Create memory usage chart
        self.memory_chart = ScrollingLineChart()
        self.memory_chart.set_chart_title("Memory Usage Monitor")
        self.memory_chart.set_axis_titles("Time (seconds)", "Memory (GB)")
        self.memory_chart.set_max_data_points(100)
        
        # Add memory metrics
        self.memory_chart.add_series("Used Memory", QColor(255, 99, 132))
        self.memory_chart.add_series("Available Memory", QColor(75, 192, 192))
        self.memory_chart.add_series("Cached Memory", QColor(255, 205, 86))
        
        layout.addWidget(self.memory_chart)
        
        # Add info panel
        info_panel = QFrame()
        info_layout = QHBoxLayout(info_panel)
        self.memory_info_label = QLabel("Memory Info: Waiting for data...")
        info_layout.addWidget(self.memory_info_label)
        layout.addWidget(info_panel)
        
        self.tab_widget.addTab(memory_widget, "Memory Usage")
    
    def setup_temperature_tab(self):
        """Setup temperature monitoring chart"""
        temp_widget = QWidget()
        layout = QVBoxLayout(temp_widget)
        
        # Create temperature chart
        self.temp_chart = ScrollingLineChart()
        self.temp_chart.set_chart_title("Temperature Monitor")
        self.temp_chart.set_axis_titles("Time (seconds)", "Temperature (°C)")
        self.temp_chart.set_max_data_points(200)
        
        # Add temperature sensors
        self.temp_chart.add_series("CPU Temp", QColor(255, 99, 132))
        self.temp_chart.add_series("GPU Temp", QColor(54, 162, 235))
        self.temp_chart.add_series("Motherboard", QColor(255, 205, 86))
        
        # Set reasonable temperature range
        self.temp_chart.set_axis_ranges(0, 40, 20, 90)
        self.temp_chart.auto_scroll = False
        
        layout.addWidget(self.temp_chart)
        
        # Add info panel
        info_panel = QFrame()
        info_layout = QHBoxLayout(info_panel)
        self.temp_info_label = QLabel("Temperature Info: Waiting for data...")
        info_layout.addWidget(self.temp_info_label)
        layout.addWidget(info_panel)
        
        self.tab_widget.addTab(temp_widget, "Temperature")
    
    def setup_combined_tab(self):
        """Setup combined overview with multiple small charts"""
        combined_widget = QWidget()
        layout = QVBoxLayout(combined_widget)
        
        # Create a smaller overview chart
        self.overview_chart = ScrollingLineChart()
        self.overview_chart.set_chart_title("System Overview")
        self.overview_chart.set_axis_titles("Time (seconds)", "Normalized Value")
        self.overview_chart.set_max_data_points(80)
        self.overview_chart.setMaximumHeight(300)
        
        # Add normalized metrics (0-100 scale)
        self.overview_chart.add_series("CPU Usage", QColor(255, 99, 132))
        self.overview_chart.add_series("Memory Usage", QColor(54, 162, 235))
        self.overview_chart.add_series("Disk Usage", QColor(255, 205, 86))
        self.overview_chart.add_series("Network Usage", QColor(75, 192, 192))
        
        layout.addWidget(self.overview_chart)
        
        # Add statistics panel
        stats_frame = QFrame()
        stats_layout = QVBoxLayout(stats_frame)
        stats_layout.addWidget(QLabel("System Statistics:"))
        self.stats_label = QLabel("Calculating...")
        stats_layout.addWidget(self.stats_label)
        layout.addWidget(stats_frame)
        
        self.tab_widget.addTab(combined_widget, "Overview")
    
    def setup_control_panel(self):
        """Setup control buttons"""
        self.control_frame = QFrame()
        layout = QHBoxLayout(self.control_frame)
        
        # Start/Stop monitoring
        self.start_btn = QPushButton("Start Monitoring")
        self.start_btn.clicked.connect(self.start_monitoring)
        
        self.stop_btn = QPushButton("Stop Monitoring")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        
        # Clear data
        clear_btn = QPushButton("Clear All Data")
        clear_btn.clicked.connect(self.clear_all_data)
        
        # Export data (placeholder)
        export_btn = QPushButton("Export Data")
        export_btn.clicked.connect(self.export_data)
        
        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(clear_btn)
        layout.addWidget(export_btn)
        layout.addStretch()
        
        # Status label
        self.status_label = QLabel("Status: Monitoring active")
        layout.addWidget(self.status_label)
    
    def update_data(self):
        """Simulate hardware data updates"""
        # Simulate realistic hardware data
        
        # CPU data (4 cores with different patterns)
        cpu1 = 20 + 30 * abs(math.sin(self.time_counter * 0.1)) + random.uniform(-3, 3)
        cpu2 = 25 + 25 * abs(math.cos(self.time_counter * 0.12)) + random.uniform(-3, 3)
        cpu3 = 15 + 35 * abs(math.sin(self.time_counter * 0.08)) + random.uniform(-3, 3)
        cpu4 = 30 + 20 * abs(math.cos(self.time_counter * 0.15)) + random.uniform(-3, 3)
        
        self.cpu_chart.add_data_point("CPU Core 1", self.time_counter, cpu1)
        self.cpu_chart.add_data_point("CPU Core 2", self.time_counter, cpu2)
        self.cpu_chart.add_data_point("CPU Core 3", self.time_counter, cpu3)
        self.cpu_chart.add_data_point("CPU Core 4", self.time_counter, cpu4)
        
        # Memory data (in GB)
        used_mem = 4 + 2 * math.sin(self.time_counter * 0.05) + random.uniform(-0.2, 0.2)
        available_mem = 16 - used_mem + random.uniform(-0.5, 0.5)
        cached_mem = 2 + 1 * math.cos(self.time_counter * 0.07) + random.uniform(-0.1, 0.1)
        
        self.memory_chart.add_data_point("Used Memory", self.time_counter, used_mem)
        self.memory_chart.add_data_point("Available Memory", self.time_counter, available_mem)
        self.memory_chart.add_data_point("Cached Memory", self.time_counter, cached_mem)
        
        # Temperature data
        cpu_temp = 45 + 15 * math.sin(self.time_counter * 0.03) + random.uniform(-2, 2)
        gpu_temp = 55 + 20 * math.cos(self.time_counter * 0.04) + random.uniform(-3, 3)
        mb_temp = 35 + 5 * math.sin(self.time_counter * 0.02) + random.uniform(-1, 1)
        
        self.temp_chart.add_data_point("CPU Temp", self.time_counter, cpu_temp)
        self.temp_chart.add_data_point("GPU Temp", self.time_counter, gpu_temp)
        self.temp_chart.add_data_point("Motherboard", self.time_counter, mb_temp)
        
        # Overview data (normalized to 0-100)
        avg_cpu = (cpu1 + cpu2 + cpu3 + cpu4) / 4
        mem_usage_pct = (used_mem / 16) * 100
        disk_usage = 45 + 10 * math.sin(self.time_counter * 0.02) + random.uniform(-2, 2)
        network_usage = 20 + 30 * abs(math.sin(self.time_counter * 0.2)) + random.uniform(-5, 5)
        
        self.overview_chart.add_data_point("CPU Usage", self.time_counter, avg_cpu)
        self.overview_chart.add_data_point("Memory Usage", self.time_counter, mem_usage_pct)
        self.overview_chart.add_data_point("Disk Usage", self.time_counter, disk_usage)
        self.overview_chart.add_data_point("Network Usage", self.time_counter, network_usage)
        
        # Update info labels
        self.cpu_info_label.setText(f"CPU: Avg {avg_cpu:.1f}% | Max Core: {max(cpu1,cpu2,cpu3,cpu4):.1f}%")
        self.memory_info_label.setText(f"Memory: {used_mem:.1f}GB used | {available_mem:.1f}GB available")
        self.temp_info_label.setText(f"Temps: CPU {cpu_temp:.1f}°C | GPU {gpu_temp:.1f}°C | MB {mb_temp:.1f}°C")
        
        # Update statistics
        self.stats_label.setText(f"""
        Average CPU Usage: {avg_cpu:.1f}%
        Memory Usage: {mem_usage_pct:.1f}%
        Highest Temperature: {max(cpu_temp, gpu_temp, mb_temp):.1f}°C
        Data Points Collected: {len(self.cpu_chart.get_series_data("CPU Core 1"))}
        """)
        
        self.time_counter += 0.5
    
    def start_monitoring(self):
        """Start data monitoring"""
        self.data_timer.start(500)
        self.status_label.setText("Status: Monitoring active")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
    
    def stop_monitoring(self):
        """Stop data monitoring"""
        self.data_timer.stop()
        self.status_label.setText("Status: Monitoring paused")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def clear_all_data(self):
        """Clear all chart data"""
        self.cpu_chart.clear_all_data()
        self.memory_chart.clear_all_data()
        self.temp_chart.clear_all_data()
        self.overview_chart.clear_all_data()
        self.time_counter = 0.0
    
    def export_data(self):
        """Export data to CSV (placeholder implementation)"""
        print("Export functionality would save data to CSV file")
        print(f"CPU data points: {len(self.cpu_chart.get_series_data('CPU Core 1'))}")
        print(f"Memory data points: {len(self.memory_chart.get_series_data('Used Memory'))}")
        print(f"Temperature data points: {len(self.temp_chart.get_series_data('CPU Temp'))}")


def main():
    """Main function to run the example"""
    app = QApplication(sys.argv)
    
    # Create and show the hardware monitor example
    monitor = HardwareMonitorExample()
    monitor.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
