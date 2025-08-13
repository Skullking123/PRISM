# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCharts import QChart, QChartView, QLineSeries
from PRISMUI.overviewPage import Overview
from constants import *

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from PRISMUI.mainWindow import Ui_App

class App(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_App()
        self.ui.setupUi(self)

    def setUpMenuButtons(self):
        for button in MenuButtonNames:
            btn = self.findChild(QPushButton, button.value)
            if btn:
                btn.clicked.connect(lambda _, b=button: print(f"{b.name} Button Clicked!"))
    
    def displayOverview(self):
        overview_widget = Overview(self.ui.display)
        self.ui.display.layout = overview_widget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = App()
    widget.setUpMenuButtons()
    # print(app.allWidgets())
    widget.displayOverview()
    widget.show()
    widget.setWindowTitle("PRISM Hardware Monitor")
    sys.exit(app.exec())
    
