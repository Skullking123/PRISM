from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtCore import Qt, QPropertyAnimation, Property
import math

class Speedometer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self.min_value = 0
        self.max_value = 500
        self.setMinimumSize(200, 200)
        
        # Create animation
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(500)  # Animation duration in milliseconds

    # Property getter and setter for animation
    def getValue(self):
        return self._value

    def setValue(self, value):
        # Animate to new value
        self.animation.stop()
        self.animation.setStartValue(self._value)
        self.animation.setEndValue(value)
        self.animation.start()

    def setValueDirect(self, value):
        # Internal setter used by the property
        self._value = max(self.min_value, min(value, self.max_value))
        self.update()

    # Create the animated property
    value = Property(float, getValue, setValueDirect)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Calculate sizes
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) / 2 - 20  # Increased margin for labels

        # Draw the arc (background)
        painter.setPen(QPen(Qt.white, 2))
        painter.drawArc(int(center_x - radius), int(center_y - radius),
                       int(radius * 2), int(radius * 2),
                       220 * 16, -260 * 16)
        
        # Draw tick marks and labels
        painter.save()
        painter.translate(center_x, center_y)
        
        # Number of major ticks
        num_ticks = 10
        value_range = self.max_value - self.min_value
        
        for i in range(num_ticks + 1):
            # Calculate angle for this tick
            angle = 220 - (260 / num_ticks * i)
            angle_rad = -1 * math.radians(angle)
            
            # Calculate tick start and end points
            outer_x = radius * math.cos(angle_rad)
            outer_y = radius * math.sin(angle_rad)
            inner_x = (radius - 10) * math.cos(angle_rad)  # Tick length = 10
            inner_y = (radius - 10) * math.sin(angle_rad)
            
            # Draw tick
            painter.setPen(QPen(Qt.white, 2))
            painter.drawLine(int(inner_x), int(inner_y),
                           int(outer_x), int(outer_y))
            
            # Draw label
            value = self.min_value + (value_range * i / num_ticks) 
            text = f"{int(value)}"
            
            # Calculate label position
            label_radius = radius - 25 # make the label 5 pixels closer to the center than the end of the tick
            label_x = label_radius * math.cos(angle_rad)
            label_y = label_radius * math.sin(angle_rad)
            
            # Center the text
            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(text)
            text_height = metrics.height()
            
            painter.save()
            painter.translate(label_x, label_y)
            # Draw text centered at the position
            painter.drawText(-text_width/2, text_height/2, text)
            painter.restore()

        painter.restore()

        # Draw the needle
        painter.save()
        painter.translate(center_x, center_y)
        offset = (260 * (self.value - self.min_value) /
                       (self.max_value - self.min_value)) # calculate the what fraction of the span to point at 
        angle = 220 - offset
        angle_rad = -1 * math.radians(angle)
        
        painter.setPen(QPen(Qt.red, 2))
        painter.drawLine(0, 0, # center the needle to pivot at the center of the speedomter
                        int(radius * 0.8 * math.cos(angle_rad)),
                        int(radius * 0.8 * math.sin(angle_rad)))
        painter.restore()

        # Draw the current value
        painter.drawText(int(center_x - 20), int(center_y + radius/2),
                        f"{self.value:.1f}")