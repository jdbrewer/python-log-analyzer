import re
from pathlib import Path
from typing import List, Dict, Any, Generator, Optional
from datetime import datetime
from .config.log_formats import LOG_FORMATS

class LogParser:
    def __init__(self, format_name: str = "standard"):
        """Initialize parser with specified log format."""
        if format_name not in LOG_FORMATS:
            raise ValueError(f"Unknown log format: {format_name}")
        
        self.format_config = LOG_FORMATS[format_name]
        self.pattern = re.compile(self.format_config["pattern"])
        self.groups = self.format_config["groups"]
        self.timestamp_format = self.format_config["timestamp_format"]

    def parse_line(self, line: str) -> Dict[str, Any]:
        """Parse a single log line into a structured dictionary."""
        match = self.pattern.match(line.strip())
        
        if not match:
            return {"raw": line, "parsed": False}
        
        # Create dictionary from matched groups
        parsed = dict(zip(self.groups, match.groups()))
        
        # Convert timestamp if present
        if "timestamp" in parsed:
            try:
                parsed["timestamp"] = datetime.strptime(
                    parsed["timestamp"], 
                    self.timestamp_format
                )
            except ValueError:
                parsed["timestamp"] = parsed["timestamp"]
        
        parsed["parsed"] = True
        return parsed

def read_logs(file_path: Path, format_name: str = "standard") -> Generator[Dict[str, Any], None, None]:
    """Read a log file and yield parsed log entries."""
    parser = LogParser(format_name)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():  # Skip empty lines
                    yield parser.parse_line(line)
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as file:
            for line in file:
                if line.strip():
                    yield parser.parse_line(line)

def load_multiple_logs(directory: Path, format_name: str = "standard") -> Generator[Dict[str, Any], None, None]:
    """Process all log files in a directory."""
    for file_path in directory.glob('*.log'):
        for log_entry in read_logs(file_path, format_name):
            # Add source file information
            log_entry["source_file"] = file_path.name
            yield log_entry
