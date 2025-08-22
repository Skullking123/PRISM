# Scrolling Line Chart - External Data Input

A real-time scrolling line chart implementation for PySide6 that accepts data through external functions, giving you complete control over the data source.

## 🚀 Key Features

- **External Data Source**: Provide your own data through custom functions
- **Manual Data Input**: Add individual data points or batches manually
- **Real-time Updates**: Automatic updates with smooth scrolling animation
- **Auto-scaling**: Y-axis automatically scales based on data range
- **Multiple Metrics**: Support for different data types with appropriate scaling
- **Flexible Integration**: Easy to integrate into existing applications

## 📋 Usage Methods

### Method 1: Data Source Function (Recommended)

Set up a function that the chart will call to get new data points:

```python
from scrolling_line_chart import ScrollingLineChart

# Create chart
chart = ScrollingLineChart()

# Define your data source function
def my_data_source(metric_name: str) -> float:
    """Your custom data function"""
    if metric_name == "CPU Total":
        return get_cpu_usage()  # Your function to get CPU usage
    elif metric_name == "Memory Used":
        return get_memory_usage()  # Your function to get memory usage
    elif metric_name == "Temperature":
        return get_temperature()  # Your function to get temperature
    else:
        return 0.0

# Set the data source
chart.set_data_source(my_data_source)

# Start automatic updates
chart.start_chart()
```

### Method 2: Manual Data Input

Add data points manually when you have new data:

```python
# Create chart
chart = ScrollingLineChart()

# Add single data points
chart.add_data_point(25.5)
chart.add_data_point(67.2)
chart.add_data_point(89.1)

# Add multiple points at once
data_batch = [42.8, 15.3, 78.9, 33.1]
chart.add_multiple_data_points(data_batch)

# Add point with custom timestamp
from PySide6.QtCore import QDateTime
chart.add_data_point(55.0, QDateTime.currentDateTime())
```

### Method 3: Hybrid Approach

Combine automatic updates with manual data input:

```python
# Set up data source for automatic updates
chart.set_data_source(my_data_source)
chart.start_chart()

# Still add manual points when needed
chart.add_data_point(special_measurement)
```

## 🔧 API Reference

### ScrollingLineChart Class

#### Methods

**`set_data_source(data_function: Callable[[str], float])`**
- Set an external function to provide data for the chart
- Function receives metric name as string, returns float value
- Called automatically during updates when chart is started

**`add_data_point(value: float, timestamp: Optional[QDateTime] = None)`**
- Manually add a single data point
- Uses current time if timestamp not provided
- Immediately updates the chart display

**`add_multiple_data_points(data_points: list)`**
- Add multiple data points at once
- Accepts list of values or (value, timestamp) tuples
- More efficient than multiple single additions

**`start_chart()`**
- Start automatic updates using the data source function
- Updates every second by default
- Requires data source function to be set

**`stop_chart()`**
- Stop automatic updates
- Manual data input still works

**`clear_chart()`**
- Remove all data points from the chart
- Resets the display

### Configuration Properties

- **`max_points`**: Maximum number of data points to display (default: 100)
- **`time_window`**: Time window in seconds for X-axis (default: 60)
- **Timer interval**: Update frequency in milliseconds (default: 1000)

## 📊 Available Metrics

The chart supports different metric types with automatic Y-axis scaling:

1. **CPU Total** - CPU usage percentage (0-100%)
2. **Memory Used** - RAM usage in GB (0-32GB)
3. **GPU Core** - GPU usage percentage (0-100%)
4. **GPU Memory** - GPU memory usage
5. **Temperature** - Temperature in °C (0-100°C)
6. **Network Upload** - Upload speed in Mbps (0-1000)
7. **Network Download** - Download speed in Mbps (0-1000)
8. **Custom Metric** - User-defined metric with default scaling

## 🎯 Complete Examples

### Example 1: System Monitoring

```python
import psutil
from scrolling_line_chart import ScrollingLineChart

def system_monitor_data(metric_name: str) -> float:
    """Get real system monitoring data"""
    if metric_name == "CPU Total":
        return psutil.cpu_percent()
    elif metric_name == "Memory Used":
        return psutil.virtual_memory().used / (1024**3)  # GB
    elif metric_name == "Temperature":
        # Get CPU temperature if available
        try:
            temps = psutil.sensors_temperatures()
            if 'cpu' in temps:
                return temps['cpu'][0].current
        except:
            pass
        return 50.0  # Fallback
    return 0.0

# Setup chart
chart = ScrollingLineChart()
chart.set_data_source(system_monitor_data)
chart.show()
chart.start_chart()
```

### Example 2: Custom Data Stream

```python
import time
import math

def custom_data_stream(metric_name: str) -> float:
    """Generate custom data patterns"""
    t = time.time()
    
    if "Sensor 1" in metric_name:
        return 50 + 30 * math.sin(t * 0.5)
    elif "Sensor 2" in metric_name:
        return 25 + 20 * math.cos(t * 0.3)
    return 0.0

chart = ScrollingLineChart()
chart.set_data_source(custom_data_stream)
```

### Example 3: Manual Data Processing

```python
# Process data from external source
def process_sensor_data():
    """Process data from your sensor/API/database"""
    # Your data processing logic here
    sensor_reading = read_sensor()  # Your sensor reading function
    processed_value = apply_filters(sensor_reading)
    
    # Add to chart
    chart.add_data_point(processed_value)

# Setup periodic processing
timer = QTimer()
timer.timeout.connect(process_sensor_data)
timer.start(2000)  # Every 2 seconds
```

## 🔗 Integration Examples

### With Existing Applications

```python
# In your existing PySide6 application
from scrolling_line_chart import ScrollingLineChart

class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Add chart to your layout
        self.chart = ScrollingLineChart()
        self.layout.addWidget(self.chart)
        
        # Connect to your data source
        self.chart.set_data_source(self.get_application_data)
        
    def get_application_data(self, metric_name: str) -> float:
        """Get data from your application"""
        return self.application_state.get_metric(metric_name)
```

### With Threading

```python
import threading
import queue

class ThreadedDataChart:
    def __init__(self):
        self.chart = ScrollingLineChart()
        self.data_queue = queue.Queue()
        
        # Start data collection thread
        self.data_thread = threading.Thread(target=self.collect_data)
        self.data_thread.daemon = True
        self.data_thread.start()
        
        # Process queue periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_queue)
        self.timer.start(100)
        
    def collect_data(self):
        """Collect data in background thread"""
        while True:
            data = expensive_data_collection()
            self.data_queue.put(data)
            time.sleep(1)
            
    def process_queue(self):
        """Process data from queue in main thread"""
        try:
            while True:
                data = self.data_queue.get_nowait()
                self.chart.add_data_point(data)
        except queue.Empty:
            pass
```

## 🧪 Testing

Run the examples to test different functionality:

```bash
# Basic functionality test
python3 scrolling_line_chart.py

# Comprehensive usage examples
python3 chart_usage_example.py

# Simple test
python3 test_chart.py
```

## 🛠 Customization

### Custom Metrics

Add your own metric types by modifying the `change_metric()` method:

```python
# In your subclass or modified version
def change_metric(self, metric_name):
    if "My Custom Metric" in metric_name:
        self.y_axis.setRange(0, 1000)
        self.y_axis.setTitleText("Custom Units")
    # ... existing code
```

### Visual Styling

Customize appearance in the `setup_chart()` method:

```python
# Change line color and thickness
pen = QPen(QColor(255, 0, 0), 3)  # Red, 3px thick
self.series.setPen(pen)

# Change chart theme
self.chart.setTheme(QChart.ChartTheme.ChartThemeDark)
```

## 📦 Requirements

- PySide6
- pandas (optional, for CSV fallback data)
- Python 3.7+

## 🤝 Integration Tips

1. **Performance**: For high-frequency data, consider batching updates
2. **Threading**: Use Qt's signal/slot mechanism for thread-safe updates
3. **Memory**: The chart automatically limits stored points (configurable)
4. **Error Handling**: Data source functions should handle exceptions gracefully
5. **Testing**: Test with various data patterns and edge cases

The ScrollingLineChart is now fully customizable and ready to integrate with any data source you provide!