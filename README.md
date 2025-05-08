# Python Log Analyzer

A powerful log analysis tool with both command-line and web interface capabilities for processing, analyzing, and visualizing log files.

## Features

- **Log Processing**
  - Ingest log files from multiple sources
  - Process and transform log data
  - Support for various log formats
  - Efficient parsing and data extraction

- **Analysis Capabilities**
  - Pattern detection and anomaly identification
  - Component-wise error analysis
  - Time-based log distribution analysis
  - Statistical analysis of log patterns

- **Web Dashboard**
  - Interactive real-time statistics
  - Visual log pattern analysis
  - Component-wise error visualization
  - Time-based distribution charts
  - Anomaly detection display
  - Filterable log entries

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/python-log-analyzer.git
cd python-log-analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Analyze log files and generate reports:
```bash
python main.py --log-dir ./data --output-dir ./output
```

#### Command Line Arguments

- `--log-dir`: Directory containing log files (default: ./data)
- `--output-dir`: Directory to save output files (default: ./output)
- `--anomaly-threshold`: Threshold for anomaly detection in standard deviations (default: 3.0)
- `--verbose`: Enable verbose output
- `--log-format`: Format of the log files (default: standard)

### Web Interface

Launch the interactive web dashboard:
```bash
python main.py --web --log-dir ./data --log-format standard
```

Then open your browser to `http://localhost:5000`

## Output

### Command Line Output

- `processed_logs.csv`: All processed log entries
- `component_stats.csv`: Statistics for each log component
- `anomalies.csv`: Detected anomalies in log patterns
- Various visualization charts

### Web Dashboard Features

- Real-time statistics display
- Interactive charts and graphs
- Filterable log entry table
- Component-wise analysis
- Time-based distribution views
- Anomaly detection visualization

## Supported Log Formats

- Standard format: `YYYY-MM-DD HH:MM:SS [LEVEL] component: message`
- Custom formats can be added by extending the parser

## Development

### Project Structure

```bash
python-log-analyzer/
├── data/               # Log files directory
├── src/               # Source code
│   ├── analysis.py    # Log analysis logic
│   ├── parser.py      # Log parsing logic
│   └── web/          # Web interface
└── tests/            # Test files
```

### Running Tests

```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Flask for the web interface
- Uses Chart.js for data visualization
- Pandas for data analysis

## Sample Data Generation

To generate sample log files for testing:

```bash
python scripts/sample_logs.py
```

This will create 15,000 sample log entries across 3 files in the `data` directory, simulating various log patterns and anomalies.
