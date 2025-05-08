import pytest
from pathlib import Path
from src.ingestion import LogParser, read_logs

def test_standard_log_format():
    """Test parsing standard log format."""
    parser = LogParser("standard")
    line = "2023-05-01 10:15:30 [INFO] api: Request processed successfully in 120ms"
    result = parser.parse_line(line)
    
    assert result["parsed"] == True
    assert result["timestamp"].strftime("%Y-%m-%d %H:%M:%S") == "2023-05-01 10:15:30"
    assert result["level"] == "INFO"
    assert result["component"] == "api"
    assert "Request processed" in result["message"]

def test_nginx_log_format():
    """Test parsing nginx log format."""
    parser = LogParser("nginx")
    line = '192.168.1.1 - - [01/May/2023:10:15:30 +0000] "GET /api/v1/users HTTP/1.1" 200 1234 "https://example.com" "Mozilla/5.0"'
    result = parser.parse_line(line)
    
    assert result["parsed"] == True
    assert result["ip"] == "192.168.1.1"
    assert result["request"] == "GET /api/v1/users HTTP/1.1"
    assert result["status"] == "200"
    assert result["size"] == "1234"

def test_invalid_format():
    """Test handling of invalid log format."""
    with pytest.raises(ValueError):
        LogParser("invalid_format")

def test_invalid_line():
    """Test handling of invalid log line."""
    parser = LogParser("standard")
    line = "This is not a valid log line"
    result = parser.parse_line(line)
    
    assert result["parsed"] == False
    assert "raw" in result
