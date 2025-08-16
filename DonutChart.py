import sys
import math
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QRect, QTimer
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics

class DonutChart(QWidget):
    """Advanced donut chart with more customization options"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(250, 250)
        
        # Customizable properties
        self.data = []
        self.center_text = ""
        self.outer_radius_ratio = 0.8  # Ratio of available space
        self.inner_radius_ratio = 0.5  # Ratio of outer radius
        self.start_angle = 90
        self.show_percentages = True
        self.show_legend = True
        self.animation_duration = 1000  # ms
        
        # Animation
        self.animation_progress = 1.0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_step)
    
    def set_chart_data(self, data, center_text="", animate=True):
        """Set chart data and optionally animate"""
        self.data = data
        self.center_text = center_text
        
        if animate:
            self.start_animation()
        else:
            self.animation_progress = 1.0
            self.update()
    
    def set_style(self, outer_ratio=0.8, inner_ratio=0.5, start_angle=90):
        """Customize chart appearance"""
        self.outer_radius_ratio = outer_ratio
        self.inner_radius_ratio = inner_ratio
        self.start_angle = start_angle
        self.update()
    
    def start_animation(self):
        """Start chart animation"""
        self.animation_progress = 0.0
        self.animation_timer.start(16)  # ~60 FPS
    
    def animate_step(self):
        """Animation step"""
        self.animation_progress += 0.025
        if self.animation_progress >= 1.0:
            self.animation_progress = 1.0
            self.animation_timer.stop()
        self.update()
    
    def paintEvent(self, event):
        """Draw the custom donut chart"""
        if not self.data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        center = rect.center()
        
        # Calculate radii
        available_radius = min(rect.width(), rect.height()) // 2 - 10
        outer_radius = int(available_radius * self.outer_radius_ratio)
        inner_radius = int(outer_radius * self.inner_radius_ratio)
        
        # Chart rectangle
        chart_rect = QRect(
            center.x() - outer_radius,
            center.y() - outer_radius,
            outer_radius * 2,
            outer_radius * 2
        )
        
        # Draw segments
        total = sum(value for _, value, _ in self.data)
        current_angle = self.start_angle
        
        for label, value, color in self.data:
            segment_angle = (value / total) * 360 * self.animation_progress
            
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            painter.drawPie(chart_rect, int(current_angle * 16), int(segment_angle * 16))
            
            current_angle += segment_angle
        
        # Draw center hole
        center_rect = QRect(
            center.x() - inner_radius,
            center.y() - inner_radius,
            inner_radius * 2,
            inner_radius * 2
        )
        
        painter.setBrush(QBrush(self.palette().color(self.backgroundRole())))
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.drawEllipse(center_rect)
        
        # Draw center text
        if self.center_text:
            painter.setPen(QPen(Qt.GlobalColor.white))
            font = QFont()
            font.setPointSize(max(8, inner_radius // 8))
            font.setBold(True)
            painter.setFont(font)
            
            text_rect = QRect(
                center.x() - inner_radius + 5,
                center.y() - inner_radius + 5,
                (inner_radius - 5) * 2,
                (inner_radius - 5) * 2
            )
            
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.center_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Show a simple custom chart
    simple_chart = DonutChart()
    simple_chart.set_chart_data([
        ("Used", 75, QColor(255, 99, 132)),
        ("Free", 25, QColor(54, 162, 235))
    ], "Disk\n75%")
    simple_chart.setWindowTitle("Simple Donut Chart")
    simple_chart.show()
    
    sys.exit(app.exec())