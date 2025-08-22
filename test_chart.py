#!/usr/bin/env python3
"""Test script for the scrolling line chart"""

import sys
from PySide6.QtWidgets import QApplication
from scrolling_line_chart import ScrollingLineChartDemo

def main():
    app = QApplication(sys.argv)
    
    # Create and show the demo
    demo = ScrollingLineChartDemo()
    demo.setWindowTitle("Scrolling Line Chart Test")
    demo.resize(1000, 700)
    demo.show()
    
    # Start the chart automatically
    demo.chart.start_chart()
    
    print("Scrolling line chart started!")
    print("- The chart will update every second with new data")
    print("- Try changing metrics from the dropdown")
    print("- Use Start/Stop buttons to control updates")
    print("- The chart automatically scrolls to show latest data")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())