# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QPushButton, 
                               QVBoxLayout, QHBoxLayout, QLabel, QSpacerItem, 
                               QSizePolicy, QFrame)
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QResizeEvent, QPalette
from constants import *
from overviewPage import Overview
from enum import Enum
from performanceLogging import HardwareLogger
hardware = HardwareLogger(None)



class App(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PRISM Hardware Monitor")
        self.setMinimumSize(800, 600)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Create horizontal layout for sidebar and content
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Setup sidebar menu and content area
        self.setupSidebar()
        self.setupContentArea()
        
        # Add to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area, 1)  # Give content area more space
        
        # Show overview by default
        self.displayOverview()

    def setupSidebar(self):
        """Create and configure the sidebar menu"""
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setFrameStyle(QFrame.Shape.StyledPanel)
        self.sidebar.setObjectName("sidebar")
        
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Add menu buttons
        self.menu_buttons = {}
        for button in MenuButtonNames:
            if button == MenuButtonNames.EXIT:
                # Add spacer before exit button
                spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, 
                                   QSizePolicy.Policy.Expanding)
                layout.addItem(spacer)
            
            btn = QPushButton(button.name.title())
            btn.setObjectName(button.value)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, b=button: self.handleMenuClick(b))
            
            self.menu_buttons[button] = btn
            layout.addWidget(btn)

    def setupContentArea(self):
        """Create the main content display area"""
        self.content_area = QFrame()
        self.content_area.setFrameStyle(QFrame.Shape.StyledPanel)
        self.content_area.setObjectName("content_area")
        
        # Create layout for content area
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(10, 10, 10, 10)

    def handleMenuClick(self, button):
        """Handle menu button clicks"""
        print(f"{button.name} Button Clicked!")
        
        # Update button states (optional: highlight active button)
        for btn in self.menu_buttons.values():
            btn.setStyleSheet("")  # Reset style
        
        self.menu_buttons[button].setStyleSheet("background-color: #0078d4; color: white;")
        
        # Route to appropriate display method
        if button == MenuButtonNames.OVERVIEW:
            self.displayOverview()
        elif button == MenuButtonNames.CPU:
            self.displayPerformance()
        elif button == MenuButtonNames.GPU:
            self.displayPerformance()
        elif button == MenuButtonNames.RAM:
            self.displayPerformance()
        elif button == MenuButtonNames.COOLING:
            self.displayTemperatures()
        elif button == MenuButtonNames.NETWORK:
            self.displayNetwork()
        elif button == MenuButtonNames.STORAGE:
            self.displayStorage()
        elif button == MenuButtonNames.SPECIFICATIONS:
            self.displaySpecifications()
        elif button == MenuButtonNames.EXIT:
            self.close()

    def clearContent(self):
        """Clear the current content area"""
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def displayOverview(self):
        """Display the overview page"""
        self.clearContent()
        overview_widget = Overview(self.palette().color(QPalette.ColorRole.Window))
        self.content_layout.addWidget(overview_widget)

    def displayPerformance(self):
        """Display the performance page"""
        self.clearContent()
        label = QLabel("Performance Monitoring")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.content_layout.addWidget(label)

    def displayTemperatures(self):
        """Display the temperatures page"""
        self.clearContent()
        label = QLabel("Temperature Monitoring")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.content_layout.addWidget(label)

    def displaySpecifications(self):
        """Display the specifications page"""
        self.clearContent()
        label = QLabel("System Specifications")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.content_layout.addWidget(label)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = App()
    widget.show()
    sys.exit(app.exec())