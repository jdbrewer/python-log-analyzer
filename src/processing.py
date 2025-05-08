import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

def logs_to_dataframe(logs: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert log dictionaries to a pandas DataFrame."""
    df = pd.DataFrame(logs)
    return df

def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform the log DataFrame."""
    # Create clean copy
    result = df.copy()
    
    # Convert timestamp strings to datetime objects
    if "timestamp" in result.columns:
        result["timestamp"] = pd.to_datetime(result["timestamp"])
    
    # Filter out unparsed entries
    if "parsed" in result.columns:
        result = result[result["parsed"] == True]
    
    # Extract hour of day for time-based analysis
    if "timestamp" in result.columns:
        result["hour"] = result["timestamp"].dt.hour
        result["date"] = result["timestamp"].dt.date
    
    return result

def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived features to the DataFrame."""
    result = df.copy()
    
    # Calculate time differences between log entries
    if "timestamp" in result.columns:
        result = result.sort_values("timestamp")
        result["time_delta"] = result["timestamp"].diff().dt.total_seconds()
    
    # Add error flag
    if "level" in result.columns:
        result["is_error"] = result["level"].isin(["ERROR", "CRITICAL", "FATAL"])
    
    return result
