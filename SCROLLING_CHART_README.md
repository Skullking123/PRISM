# ScrollingLineChart - Generic Real-time Line Chart Widget

A comprehensive, generic scrolling line chart component built with PySide6 and QtCharts. Perfect for real-time data visualization, monitoring applications, and any scenario where you need to display time-series data with automatic scrolling.

## Features

- **Multiple Data Series**: Support for multiple line series with different colors
- **Automatic Scrolling**: Configurable data buffer with automatic old data removal
- **Real-time Updates**: Optimized for high-frequency data updates
- **Customizable Styling**: Themes, colors, grid lines, legends, and more
- **Flexible Axes**: Auto-scaling or manual axis range control
- **Interactive Controls**: Built-in pause/resume, clear data, and export functionality
- **Signal Support**: Qt signals for data point additions and updates
- **Memory Efficient**: Uses deque buffers to prevent memory leaks with large datasets

## Quick Start

### Basic Usage

```python
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtGui import QColor
from ScrollingLineChart import ScrollingLineChart

app = QApplication([])

# Create chart widget
chart = ScrollingLineChart()
chart.set_chart_title("My Real-time Data")
chart.set_axis_titles("Time (s)", "Value")

# Add data series
chart.add_series("Temperature", QColor(255, 99, 132))
chart.add_series("Humidity", QColor(54, 162, 235))

# Add data points
chart.add_data_point("Temperature", 0.0, 23.5)
chart.add_data_point("Temperature", 1.0, 24.1)
chart.add_data_point("Humidity", 0.0, 45.2)
chart.add_data_point("Humidity", 1.0, 46.8)

# Show chart
chart.show()
app.exec()
```

### Advanced Configuration

```python
# Configure chart behavior
chart.set_max_data_points(200)  # Keep last 200 points
chart.enable_legend(True)       # Show legend
chart.enable_grid(True)         # Show grid lines
chart.set_theme(QChart.ChartTheme.ChartThemeDark)

# Set fixed axis ranges (disable auto-scaling)
chart.set_axis_ranges(0, 100, -10, 50)  # x_min, x_max, y_min, y_max
chart.auto_scroll = False

# Connect to data point signal
chart.dataPointAdded.connect(lambda series, x, y: print(f"{series}: ({x}, {y})"))
```

## API Reference

### ScrollingLineChart Class

#### Constructor
```python
ScrollingLineChart(parent=None)
```

#### Key Methods

##### Data Management
- `add_series(series_name: str, color: QColor = None) -> bool`
- `remove_series(series_name: str) -> bool`
- `add_data_point(series_name: str, x_value: float, y_value: float)`
- `add_data_points(series_name: str, points: List[Tuple[float, float]])`
- `clear_series_data(series_name: str)`
- `clear_all_data()`

##### Configuration
- `set_max_data_points(max_points: int)`
- `set_chart_title(title: str)`
- `set_axis_titles(x_title: str, y_title: str)`
- `set_axis_ranges(x_min: float, x_max: float, y_min: float, y_max: float)`
- `set_theme(theme: QChart.ChartTheme)`

##### Styling
- `enable_legend(enabled: bool)`
- `enable_grid(enabled: bool)`
- `toggle_auto_scroll()`

##### Data Retrieval
- `get_series_names() -> List[str]`
- `get_series_data(series_name: str) -> List[Tuple[float, float]]`
- `get_latest_value(series_name: str) -> Optional[Tuple[float, float]]`

##### Auto-Update
- `start_auto_update(interval_ms: int = 100)`
- `stop_auto_update()`
- `refresh_chart()`

#### Properties
- `max_data_points`: Maximum number of points to keep (default: 100)
- `auto_scroll`: Whether to auto-adjust axis ranges (default: True)
- `show_grid`: Whether to show grid lines (default: True)
- `show_legend`: Whether to show legend (default: True)
- `animation_enabled`: Whether to use smooth animations (default: True)

#### Signals
- `dataPointAdded(str, float, float)`: Emitted when a data point is added

## Examples

### Example 1: Hardware Monitoring

```python
import sys
import random
import math
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor
from ScrollingLineChart import ScrollingLineChart

class HardwareMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hardware Monitor")
        
        layout = QVBoxLayout(self)
        
        # Create chart
        self.chart = ScrollingLineChart()
        self.chart.set_chart_title("System Resources")
        self.chart.set_axis_titles("Time (s)", "Usage (%)")
        self.chart.set_axis_ranges(0, 30, 0, 100)
        self.chart.auto_scroll = False
        
        # Add series
        self.chart.add_series("CPU", QColor(255, 99, 132))
        self.chart.add_series("Memory", QColor(54, 162, 235))
        self.chart.add_series("Disk", QColor(255, 205, 86))
        
        layout.addWidget(self.chart)
        
        # Setup data timer
        self.time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(200)  # Update every 200ms
    
    def update_data(self):
        # Simulate hardware data
        cpu = 30 + 20 * math.sin(self.time * 0.1) + random.uniform(-5, 5)
        memory = 45 + 15 * math.cos(self.time * 0.08) + random.uniform(-3, 3)
        disk = 20 + 10 * math.sin(self.time * 0.05) + random.uniform(-2, 2)
        
        self.chart.add_data_point("CPU", self.time, cpu)
        self.chart.add_data_point("Memory", self.time, memory)
        self.chart.add_data_point("Disk", self.time, disk)
        
        self.time += 0.2

app = QApplication(sys.argv)
monitor = HardwareMonitor()
monitor.show()
sys.exit(app.exec())
```

### Example 2: Stock Price Tracking

```python
import sys
import random
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor
from ScrollingLineChart import ScrollingLineChart

class StockTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stock Price Tracker")
        
        layout = QVBoxLayout(self)
        
        # Create chart
        self.chart = ScrollingLineChart()
        self.chart.set_chart_title("Stock Prices")
        self.chart.set_axis_titles("Time", "Price ($)")
        self.chart.set_max_data_points(50)
        
        # Add stock series
        self.chart.add_series("AAPL", QColor(255, 99, 132))
        self.chart.add_series("GOOGL", QColor(54, 162, 235))
        self.chart.add_series("MSFT", QColor(255, 205, 86))
        
        layout.addWidget(self.chart)
        
        # Initial prices
        self.prices = {"AAPL": 150.0, "GOOGL": 2800.0, "MSFT": 300.0}
        self.time = 0
        
        # Setup timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_prices)
        self.timer.start(1000)  # Update every second
    
    def update_prices(self):
        for stock, price in self.prices.items():
            # Simulate price movement
            change = random.uniform(-0.02, 0.02)  # ±2% change
            new_price = price * (1 + change)
            self.prices[stock] = new_price
            
            self.chart.add_data_point(stock, self.time, new_price)
        
        self.time += 1

app = QApplication(sys.argv)
tracker = StockTracker()
tracker.show()
sys.exit(app.exec())
```

## Integration with Existing Applications

The ScrollingLineChart is designed to integrate seamlessly with existing PySide6/PyQt applications. See `chart_integration_example.py` for a comprehensive example showing integration with a hardware monitoring application.

### Key Integration Points:

1. **Import the component**: `from ScrollingLineChart import ScrollingLineChart`
2. **Create chart instances**: `chart = ScrollingLineChart(parent)`
3. **Configure as needed**: Set titles, colors, data limits
4. **Connect data sources**: Use timers or signals to feed data
5. **Add to layouts**: Treat like any other QWidget

## Requirements

- Python 3.7+
- PySide6
- QtCharts (included with PySide6)

## Performance Notes

- The chart uses efficient deque buffers to manage data
- Automatic data point limiting prevents memory leaks
- Chart updates are optimized for real-time performance
- For high-frequency updates (>10Hz), consider batching data points

## Customization

The chart supports extensive customization:

- **Colors**: 8 default colors, custom colors supported
- **Themes**: Light, Dark, Blue Cerulean, Brown Sand, Blue NCS, High Contrast, Blue Icy, Qt themes
- **Axes**: Custom ranges, labels, formatting
- **Animation**: Enable/disable smooth transitions
- **Grid**: Show/hide grid lines
- **Legend**: Show/hide, positioning

## License

This component is part of the PRISM Hardware Monitor project. See the main project license for details.