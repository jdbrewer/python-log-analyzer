from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import argparse
import sys
import time

from src.ingestion import load_multiple_logs
from src.processing import logs_to_dataframe, preprocess_dataframe, enrich_data
from src.analysis import get_error_rate, find_busiest_hour, get_component_stats, detect_anomalies
from src.visualization import create_log_level_distribution, create_hourly_distribution, create_component_error_chart, create_time_series_plot
from src.web.app import run_server

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze log files and generate insights.')
    parser.add_argument('--log-dir', type=str, default='./data', 
                        help='Directory containing log files')
    parser.add_argument('--output-dir', type=str, default='./output', 
                        help='Directory to save output files')
    parser.add_argument('--anomaly-threshold', type=float, default=3.0, 
                        help='Threshold for anomaly detection (standard deviations)')
    parser.add_argument('--log-format', type=str, default='standard',
                        choices=['standard', 'nginx', 'apache'],
                        help='Log format to parse')
    parser.add_argument('--verbose', action='store_true', 
                        help='Print verbose output')
    parser.add_argument('--web', action='store_true',
                    help='Start the web interface')
    parser.add_argument('--web-debug', action='store_true',
                    help='Run web interface in debug mode')
    
    args = parser.parse_args()
    
    # Convert to Path objects
    log_dir = Path(args.log_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Validate input directory
    if not log_dir.exists() or not log_dir.is_dir():
        print(f"Error: Log directory '{log_dir}' does not exist or is not a directory")
        sys.exit(1)
        
    print(f"Processing logs from {log_dir}...")
    start_time = time.time()

    if args.web:
        run_server(log_dir, args.log_format, args.web_debug)
    
    # Ingest data
    try:
        logs = list(load_multiple_logs(log_dir, args.log_format))
        if not logs:
            print(f"No log entries found in {log_dir}. Make sure the directory contains .log files.")
            sys.exit(1)
            
        print(f"Loaded {len(logs)} log entries from {log_dir}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading logs: {e}")
        sys.exit(1)
    
    # Process data
    try:
        print("Converting logs to DataFrame...")
        df = logs_to_dataframe(logs)
        
        print("Preprocessing data...")
        df = preprocess_dataframe(df)
        
        print("Enriching data...")
        df = enrich_data(df)
        
        print(f"Processing complete: {len(df)} valid log entries")
    except Exception as e:
        print(f"Error processing logs: {e}")
        sys.exit(1)
    
    # Generate basic statistics
    try:
        print("\n--- Basic Statistics ---")
        error_rate = get_error_rate(df)
        print(f"Overall error rate: {error_rate:.2f}%")
        
        busiest_hour, count = find_busiest_hour(df)
        print(f"Busiest hour: {busiest_hour}:00 with {count} entries")
        
        # Component analysis
        component_stats = get_component_stats(df)
        print("\n--- Top Components by Volume ---")
        print(component_stats.head().to_string())
        
        # Anomaly detection
        print("\n--- Anomaly Detection ---")
        anomalies = detect_anomalies(df, threshold=args.anomaly_threshold)
        if not anomalies.empty:
            print(f"Detected {len(anomalies)} anomalies")
            print(anomalies.head().to_string() if len(anomalies) > 5 else anomalies.to_string())
        else:
            print("No anomalies detected")
    except Exception as e:
        print(f"Error analyzing logs: {e}")
        sys.exit(1)
    
    # Save outputs
    try:
        print(f"\nSaving outputs to {output_dir}...")
        df.to_csv(output_dir / "processed_logs.csv", index=False)
        component_stats.to_csv(output_dir / "component_stats.csv")
        if not anomalies.empty:
            anomalies.to_csv(output_dir / "anomalies.csv")
        
        # Generate visualizations
        print("Creating visualizations...")
        create_log_level_distribution(df, output_dir)
        create_hourly_distribution(df, output_dir)
        create_component_error_chart(df, output_dir)
        create_time_series_plot(df, output_dir)
        
        processing_time = time.time() - start_time
        print(f"\nProcessing complete in {processing_time:.2f} seconds")
        print(f"Results saved to {output_dir}")
    except Exception as e:
        print(f"Error saving outputs: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
