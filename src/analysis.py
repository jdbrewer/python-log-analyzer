import pandas as pd
from typing import Dict, Any, List, Tuple

def get_error_rate(df: pd.DataFrame) -> float:
    """Calculate the percentage of error logs."""
    if "is_error" not in df.columns:
        return 0.0
    return df["is_error"].mean() * 100

def find_busiest_hour(df: pd.DataFrame) -> Tuple[int, int]:
    """Find the hour with most log entries."""
    if "hour" not in df.columns:
        return (0, 0)
    hourly_counts = df["hour"].value_counts()
    busiest_hour = hourly_counts.idxmax()
    return (busiest_hour, hourly_counts[busiest_hour])

def get_component_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze log counts and error rates by component."""
    if "component" not in df.columns:
        return pd.DataFrame()
        
    # Group by component and count logs
    component_stats = df.groupby("component").agg(
        total_logs=("component", "count"),
    )
    
    # Add error counts if available
    if "is_error" in df.columns:
        error_counts = df[df["is_error"]].groupby("component").size()
        component_stats["error_logs"] = error_counts
        component_stats["error_logs"] = component_stats["error_logs"].fillna(0).astype(int)
        component_stats["error_rate"] = (component_stats["error_logs"] / component_stats["total_logs"]) * 100
    
    return component_stats.sort_values("total_logs", ascending=False)

def detect_anomalies(df: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
    """Detect potential anomalies in log frequency."""
    if "timestamp" not in df.columns:
        return pd.DataFrame()
        
    # Resample to 5-minute intervals
    time_series = df.set_index("timestamp")
    counts = time_series.resample("5T").size()
    
    # Calculate rolling mean and standard deviation
    rolling_mean = counts.rolling(window=12).mean()  # 1 hour window
    rolling_std = counts.rolling(window=12).std()
    
    # Identify anomalies
    anomalies = counts[(counts - rolling_mean) > threshold * rolling_std]
    
    return pd.DataFrame({
        "timestamp": anomalies.index,
        "log_count": anomalies.values,
        "expected": rolling_mean.loc[anomalies.index].values,
        "deviation": (anomalies.values - rolling_mean.loc[anomalies.index].values) / rolling_std.loc[anomalies.index].values
    })
