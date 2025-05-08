import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def create_log_level_distribution(df: pd.DataFrame, output_path: Path):
    """Create a pie chart showing distribution of log levels."""
    if "level" not in df.columns:
        return
        
    plt.figure(figsize=(10, 6))
    level_counts = df["level"].value_counts()
    plt.pie(level_counts, labels=level_counts.index, autopct='%1.1f%%')
    plt.title("Log Level Distribution")
    plt.savefig(output_path / "level_distribution.png")
    plt.close()

def create_hourly_distribution(df: pd.DataFrame, output_path: Path):
    """Create a bar chart showing log distribution by hour."""
    if "hour" not in df.columns:
        return
        
    plt.figure(figsize=(12, 6))
    hourly = df["hour"].value_counts().sort_index()
    sns.barplot(x=hourly.index, y=hourly.values)
    plt.title("Log Distribution by Hour")
    plt.xlabel("Hour of Day")
    plt.ylabel("Number of Logs")
    plt.xticks(range(0, 24))
    plt.savefig(output_path / "hourly_distribution.png")
    plt.close()

def create_component_error_chart(df: pd.DataFrame, output_path: Path):
    """Create a bar chart showing error rates by component."""
    component_stats = df.groupby("component").agg(
        total=("component", "count"),
        errors=("is_error", "sum")
    )
    component_stats["error_rate"] = (component_stats["errors"] / component_stats["total"]) * 100
    component_stats = component_stats.sort_values("error_rate", ascending=False)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(x=component_stats.index, y=component_stats["error_rate"])
    plt.title("Error Rate by Component")
    plt.xlabel("Component")
    plt.ylabel("Error Rate (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path / "component_error_rates.png")
    plt.close()

def create_time_series_plot(df: pd.DataFrame, output_path: Path):
    """Create a time series plot showing log volume over time."""
    if "timestamp" not in df.columns:
        return
    
    # Resample to 15-minute intervals
    time_series = df.set_index("timestamp")
    counts = time_series.resample("15T").size()
    
    plt.figure(figsize=(15, 6))
    counts.plot()
    plt.title("Log Volume Over Time")
    plt.xlabel("Time")
    plt.ylabel("Number of Logs")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(output_path / "time_series.png")
    plt.close()
    
    # Also plot error counts if available
    if "is_error" in df.columns:
        error_series = time_series[time_series["is_error"]].resample("15T").size()
        
        plt.figure(figsize=(15, 6))
        plt.plot(counts.index, counts.values, label="All Logs")
        plt.plot(error_series.index, error_series.values, label="Errors", color="red")
        plt.title("Log Volume and Errors Over Time")
        plt.xlabel("Time")
        plt.ylabel("Number of Logs")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(output_path / "error_time_series.png")
        plt.close()