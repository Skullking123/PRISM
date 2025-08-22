# Scrolling Line Chart

A real-time scrolling line chart implementation for hardware monitoring using PySide6 and QtCharts.

## Features

- **Real-time Data Updates**: Chart updates every second with new data points
- **Automatic Scrolling**: X-axis automatically scrolls to show the latest data
- **Multiple Metrics**: Support for various hardware metrics (CPU, Memory, GPU, Temperature, Network)
- **Auto-scaling**: Y-axis automatically scales based on visible data
- **Interactive Controls**: Start/Stop/Clear buttons for chart control
- **Data Source Flexibility**: Uses real CSV data when available, falls back to simulated data

## Usage

### Standalone Mode
```bash
python scrolling_line_chart.py
```

### Test Mode
```bash
python test_chart.py
```

### Integrated Mode
Run the main application and navigate to:
- **CPU/GPU/RAM** sections for performance monitoring
- **Cooling** section for temperature monitoring  
- **Network** section for network traffic monitoring

## Available Metrics

1. **CPU Total** - Overall CPU usage percentage
2. **Memory Used** - RAM usage in GB
3. **GPU Core** - GPU core usage percentage
4. **GPU Memory** - GPU memory usage
5. **Temperature** - System temperature in °C
6. **Network Upload** - Upload speed in Mbps
7. **Network Download** - Download speed in Mbps

## Chart Controls

- **Metric Dropdown**: Select which hardware metric to display
- **Start Button**: Begin real-time data updates
- **Stop Button**: Pause data updates
- **Clear Button**: Remove all data points from chart

## Configuration

### Time Window
- Default: 60 seconds of data visible
- Modify `time_window` property to change

### Update Frequency
- Default: 1 second intervals
- Modify timer interval in `setup_timer()` method

### Maximum Points
- Default: 100 data points maximum
- Modify `max_points` property to change

## Data Sources

1. **CSV File**: Reads from `hardware_usage_log.csv` if available
2. **Simulated Data**: Generates realistic random values as fallback

## Technical Details

### Architecture
- `ScrollingLineChart`: Main chart widget class
- `QLineSeries`: Data series for line plotting
- `QDateTimeAxis`: Time-based X-axis with scrolling
- `QValueAxis`: Auto-scaling Y-axis
- `QTimer`: Real-time update mechanism

### Key Methods
- `update_chart()`: Adds new data points and manages scrolling
- `change_metric()`: Switches between different hardware metrics
- `get_sample_value()`: Retrieves data from CSV or generates random values

## Integration

To integrate into your own application:

```python
from scrolling_line_chart import ScrollingLineChart

# Create chart widget
chart = ScrollingLineChart()

# Add to your layout
layout.addWidget(chart)

# Start updates
chart.start_chart()
```

## Requirements

- PySide6
- pandas (for CSV data reading)
- QtCharts module

## Customization

### Adding New Metrics
1. Add metric name to `metric_combo` items
2. Update `get_sample_value()` method with data source
3. Adjust Y-axis ranges in `change_metric()` method

### Styling
Modify the `setup_chart()` method to customize:
- Line colors and thickness
- Chart themes
- Axis formatting
- Animation settings