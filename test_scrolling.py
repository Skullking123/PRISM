#!/usr/bin/env python3

import sys
import time
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor
from ScrollingLineChart import ScrollingLineChart

class ScrollingTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scrolling Line Chart Test - Right to Left < 100 points")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Create chart
        self.chart = ScrollingLineChart(self)
        self.chart.set_chart_title("Right-to-Left Scrolling Test")
        self.chart.set_axis_titles("Time (seconds)", "Value")
        
        # Add test series
        self.chart.add_series("Test Data", QColor(255, 99, 132))
        
        layout.addWidget(self.chart)
        
        # Test controls
        button_layout = QVBoxLayout()
        
        self.add_point_btn = QPushButton("Add Single Point")
        self.add_point_btn.clicked.connect(self.add_single_point)
        
        self.add_many_btn = QPushButton("Add 10 Points")
        self.add_many_btn.clicked.connect(self.add_many_points)
        
        self.add_hundred_btn = QPushButton("Add 100+ Points (trigger normal scrolling)")
        self.add_hundred_btn.clicked.connect(self.add_hundred_points)
        
        self.clear_btn = QPushButton("Clear All Data")
        self.clear_btn.clicked.connect(self.clear_data)
        
        button_layout.addWidget(self.add_point_btn)
        button_layout.addWidget(self.add_many_btn)
        button_layout.addWidget(self.add_hundred_btn)
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        self.point_counter = 0
    
    def add_single_point(self):
        import random
        value = 50 + 20 * random.random()
        self.chart.add_data_point("Test Data", value)
        self.point_counter += 1
        print(f"Added point {self.point_counter}, total points: {self.get_total_points()}")
    
    def add_many_points(self):
        import random
        for i in range(10):
            value = 50 + 20 * random.random()
            self.chart.add_data_point("Test Data", value)
            self.point_counter += 1
        print(f"Added 10 points, total points: {self.get_total_points()}")
    
    def add_hundred_points(self):
        import random
        for i in range(120):  # Add more than 100 to trigger normal scrolling
            value = 50 + 20 * random.random()
            self.chart.add_data_point("Test Data", value)
            self.point_counter += 1
        print(f"Added 120 points, total points: {self.get_total_points()}")
    
    def clear_data(self):
        self.chart.clear_all_data()
        self.point_counter = 0
        print("Cleared all data")
    
    def get_total_points(self):
        total = 0
        for data in self.chart.data_series.values():
            total += len(data)
        return total

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    test = ScrollingTest()
    test.show()
    
    sys.exit(app.exec())