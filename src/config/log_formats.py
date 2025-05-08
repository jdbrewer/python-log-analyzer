# Create src/config/log_formats.py with the following content:
"""Configuration for different log formats."""

LOG_FORMATS = {
    "standard": {
        "pattern": r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \[(\w+)\] (\w+): (.*)',
        "groups": ["timestamp", "level", "component", "message"],
        "timestamp_format": "%Y-%m-%d %H:%M:%S"
    },
    "nginx": {
        "pattern": r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"',
        "groups": ["ip", "timestamp", "request", "status", "size", "referer", "user_agent"],
        "timestamp_format": "%d/%b/%Y:%H:%M:%S %z"
    },
    "apache": {
        "pattern": r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"',
        "groups": ["ip", "timestamp", "request", "status", "size", "referer", "user_agent"],
        "timestamp_format": "%d/%b/%Y:%H:%M:%S %z"
    }
}