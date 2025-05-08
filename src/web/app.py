# src/web/app.py
from flask import Flask, render_template, jsonify, request
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
import json
import logging

from ..ingestion import load_multiple_logs
from ..processing import logs_to_dataframe, preprocess_dataframe, enrich_data
from ..analysis import get_error_rate, find_busiest_hour, get_component_stats, detect_anomalies

app = Flask(__name__)

# Global variable to store the DataFrame
df = None

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_data(log_dir: Path, log_format: str = "standard"):
    """Load and process log data."""
    global df
    logger.debug(f"Loading data from {log_dir} with format {log_format}")
    logs = list(load_multiple_logs(log_dir, log_format))
    logger.debug(f"Loaded {len(logs)} log entries")
    df = logs_to_dataframe(logs)
    df = preprocess_dataframe(df)
    df = enrich_data(df)
    logger.debug(f"Processed DataFrame shape: {df.shape}")
    return df

@app.route('/')
def index():
    """Render the main dashboard."""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """Get overall statistics."""
    logger.debug("Received request for stats")
    if df is None:
        logger.error("No data loaded")
        return jsonify({"error": "No data loaded"}), 400
    
    try:
        # Calculate total logs
        total_logs = len(df)
        
        # Calculate error rate
        error_logs = len(df[df['level'].isin(['ERROR', 'CRITICAL'])])
        error_rate = (error_logs / total_logs * 100) if total_logs > 0 else 0
        
        # Calculate busiest hour
        hourly_counts = df.groupby(df['timestamp'].dt.hour).size()
        busiest_hour = (hourly_counts.idxmax(), int(hourly_counts.max()))
        
        # Calculate component stats
        component_stats = []
        for component in df['component'].unique():
            component_df = df[df['component'] == component]
            component_total = len(component_df)
            component_errors = len(component_df[component_df['level'].isin(['ERROR', 'CRITICAL'])])
            component_error_rate = (component_errors / component_total * 100) if component_total > 0 else 0
            
            component_stats.append({
                'component': str(component),
                'total_logs': int(component_total),
                'error_logs': int(component_errors),
                'error_rate': float(component_error_rate)
            })
        
        stats = {
            'total_logs': int(total_logs),
            'error_rate': float(error_rate),
            'busiest_hour': (int(busiest_hour[0]), int(busiest_hour[1])),
            'components': component_stats
        }
        
        logger.debug(f"Returning stats: {stats}")
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/logs')
def get_logs():
    """Get paginated log entries with filtering."""
    logger.debug("Received request for logs")
    if df is None:
        logger.error("No data loaded")
        return jsonify({"error": "No data loaded"}), 400
    
    try:
        # Get filter parameters
        level = request.args.get('level')
        component = request.args.get('component')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        logger.debug(f"Filter params: level={level}, component={component}, page={page}")
        logger.debug(f"Date params: start={start_date}, end={end_date}")
        
        # Apply filters
        filtered_df = df.copy()
        if level:
            filtered_df = filtered_df[filtered_df['level'] == level]
        if component:
            filtered_df = filtered_df[filtered_df['component'] == component]
        if start_date:
            try:
                start_date = pd.to_datetime(start_date)
                filtered_df = filtered_df[filtered_df['timestamp'] >= start_date]
            except Exception as e:
                logger.error(f"Error parsing start_date: {e}")
        if end_date:
            try:
                end_date = pd.to_datetime(end_date)
                filtered_df = filtered_df[filtered_df['timestamp'] <= end_date]
            except Exception as e:
                logger.error(f"Error parsing end_date: {e}")
        
        # Paginate
        total = len(filtered_df)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # Convert to records and ensure all values are JSON serializable
        logs = []
        for _, row in filtered_df.iloc[start_idx:end_idx].iterrows():
            try:
                log_entry = {
                    'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'level': str(row['level']),
                    'component': str(row['component']),
                    'message': str(row['message'])
                }
                logs.append(log_entry)
            except Exception as e:
                logger.error(f"Error processing log entry: {e}")
                continue
        
        logger.debug(f"Returning {len(logs)} logs out of {total} total")
        if logs:
            logger.debug(f"First log entry: {logs[0]}")
        
        response_data = {
            "logs": logs,
            "total": int(total),  # Convert to Python int
            "page": int(page),
            "per_page": int(per_page),
            "total_pages": int((total + per_page - 1) // per_page)
        }
        
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/anomalies')
def get_anomalies():
    """Get detected anomalies."""
    if df is None:
        return jsonify({"error": "No data loaded"}), 400
    
    threshold = float(request.args.get('threshold', 3.0))
    anomalies = detect_anomalies(df, threshold)
    return jsonify(anomalies.to_dict('records'))

@app.route('/api/time-series')
def get_time_series():
    """Get error rate time series data."""
    if df is None:
        return jsonify({"error": "No data loaded"}), 400
    
    try:
        # Get error rate time series
        time_series = df[df['level'].isin(['ERROR', 'CRITICAL'])].resample('5T', on='timestamp').size()
        time_series = time_series.fillna(0)
        
        # Convert to list of [timestamp, count] pairs
        data = [
            {
                'timestamp': ts.strftime('%Y-%m-%d %H:%M:%S'),
                'count': int(count)
            }
            for ts, count in time_series.items()
        ]
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting time series: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/hourly-distribution')
def get_hourly_distribution():
    """Get hourly log distribution."""
    if df is None:
        return jsonify({"error": "No data loaded"}), 400
    
    try:
        # Get hourly distribution
        hourly_counts = df.groupby(df['timestamp'].dt.hour).size()
        
        # Convert to list of [hour, count] pairs
        data = [
            {
                'hour': int(hour),
                'count': int(count)
            }
            for hour, count in hourly_counts.items()
        ]
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting hourly distribution: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/component-stats')
def get_component_stats():
    """Get component-wise statistics."""
    if df is None:
        return jsonify({"error": "No data loaded"}), 400
    
    try:
        # Get component stats
        component_stats = df.groupby('component').agg({
            'level': lambda x: (x.isin(['ERROR', 'CRITICAL'])).sum(),
            'timestamp': 'count'
        }).rename(columns={'level': 'error_count', 'timestamp': 'total_count'})
        
        component_stats['error_rate'] = (component_stats['error_count'] / component_stats['total_count'] * 100).round(2)
        
        # Convert to list of component stats
        data = [
            {
                'component': component,
                'error_count': int(stats['error_count']),
                'total_count': int(stats['total_count']),
                'error_rate': float(stats['error_rate'])
            }
            for component, stats in component_stats.iterrows()
        ]
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting component stats: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/level-distribution')
def get_level_distribution():
    """Get log level distribution."""
    if df is None:
        return jsonify({"error": "No data loaded"}), 400
    
    try:
        # Get level distribution
        level_counts = df['level'].value_counts()
        
        # Convert to list of [level, count] pairs
        data = [
            {
                'level': level,
                'count': int(count)
            }
            for level, count in level_counts.items()
        ]
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting level distribution: {str(e)}")
        return jsonify({"error": str(e)}), 500

def run_server(log_dir: Path, log_format: str = "standard", debug: bool = False):
    """Run the Flask server."""
    # Load data before starting the server
    load_data(log_dir, log_format)
    
    # Run the Flask app
    app.run(debug=debug)