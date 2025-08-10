from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton

import sys


app = QApplication([])
window = QWidget()
window.setWindowTitle('Hello World')
window.show()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        button = QPushButton("Press Me!")

        self.setFixedSize(QSize(400, 300))

        # Set the central widget of the Window.
        self.setCentralWidget(button)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()