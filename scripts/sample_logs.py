#!/usr/bin/env python3
"""
Generate sample log files for testing a log analysis pipeline.
This script creates realistic server and application logs with various patterns.
"""

import random
import datetime
import os
from pathlib import Path

# Configuration
OUTPUT_DIR = Path("./data")
NUM_FILES = 3
ENTRIES_PER_FILE = 5000
START_DATE = datetime.datetime.now() - datetime.timedelta(days=7)

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# Log components
COMPONENTS = ["api", "database", "auth", "frontend", "worker", "cache", "scheduler"]
LOG_LEVELS = {
    "INFO": 0.7,      # 70% of logs
    "WARNING": 0.15,  # 15% of logs
    "ERROR": 0.1,     # 10% of logs
    "DEBUG": 0.03,    # 3% of logs
    "CRITICAL": 0.02  # 2% of logs
}

# Messages by component and level
MESSAGES = {
    "api": {
        "INFO": [
            "Request processed successfully in {0}ms",
            "API call to {0} endpoint completed",
            "User {0} accessed resource {1}",
            "Rate limit status: {0}/{1}"
        ],
        "WARNING": [
            "Slow API response: {0}ms",
            "Rate limit warning for IP {0}",
            "Deprecated endpoint {0} accessed by client {1}"
        ],
        "ERROR": [
            "API request failed: {0}",
            "Invalid parameters in request to {0}",
            "Authentication failed for API request from {0}"
        ],
        "DEBUG": [
            "API request details: {0}",
            "Headers received: {0}"
        ],
        "CRITICAL": [
            "API service unresponsive for {0} seconds",
            "Multiple API endpoints failing: {0}"
        ]
    },
    "database": {
        "INFO": [
            "Query executed in {0}ms",
            "Connection pool status: {0}/{1} active",
            "Database cleanup completed in {0}s",
            "Rows affected: {0}"
        ],
        "WARNING": [
            "Slow query detected: {0}ms",
            "Connection pool approaching limit: {0}/{1}",
            "Index fragmentation at {0}%"
        ],
        "ERROR": [
            "Query failed: {0}",
            "Database connection error: {0}",
            "Deadlock detected on table {0}"
        ],
        "DEBUG": [
            "Query plan: {0}",
            "Table locks acquired: {0}"
        ],
        "CRITICAL": [
            "Database server unresponsive",
            "Data corruption detected in table {0}"
        ]
    },
    "auth": {
        "INFO": [
            "User {0} logged in successfully",
            "Password changed for user {0}",
            "New account created: {0}",
            "Password reset requested for {0}"
        ],
        "WARNING": [
            "Multiple failed login attempts for user {0}",
            "Session expired for user {0}",
            "Unusual login location for user {0}: {1}"
        ],
        "ERROR": [
            "Login failed for user {0}: {1}",
            "Account locked for user {0}",
            "Invalid token presented by {0}"
        ],
        "DEBUG": [
            "Token generated for user {0}",
            "Auth flow initiated for {0}"
        ],
        "CRITICAL": [
            "Possible brute force attack from IP {0}",
            "Security breach detected for user {0}"
        ]
    },
    "frontend": {
        "INFO": [
            "Page {0} loaded in {1}ms",
            "User {0} viewed {1}",
            "Asset {0} cached successfully",
            "Form submission processed: {0}"
        ],
        "WARNING": [
            "Slow page load: {0} took {1}ms",
            "Asset {0} not found in cache",
            "Form validation warnings: {0}"
        ],
        "ERROR": [
            "JavaScript error: {0}",
            "CSS parsing failed for {0}",
            "Form submission failed: {0}"
        ],
        "DEBUG": [
            "DOM fully loaded: {0} elements",
            "Event listener attached to {0}"
        ],
        "CRITICAL": [
            "Frontend service crash: {0}",
            "Critical render path blocked by {0}"
        ]
    },
    "worker": {
        "INFO": [
            "Job {0} completed in {1}s",
            "Queue status: {0} pending jobs",
            "Worker {0} processed {1} jobs",
            "Job {0} started"
        ],
        "WARNING": [
            "Worker {0} approaching memory limit",
            "Job {0} running longer than expected: {1}s",
            "Queue backlog detected: {0} jobs"
        ],
        "ERROR": [
            "Job {0} failed: {1}",
            "Worker {0} crashed",
            "Queue connection lost"
        ],
        "DEBUG": [
            "Job {0} details: {1}",
            "Worker {0} memory usage: {1}MB"
        ],
        "CRITICAL": [
            "All workers offline",
            "Critical job {0} failed repeatedly"
        ]
    },
    "cache": {
        "INFO": [
            "Cache hit ratio: {0}%",
            "Item {0} added to cache",
            "Cache size: {0}MB",
            "Cache entry {0} refreshed"
        ],
        "WARNING": [
            "Cache miss rate high: {0}%",
            "Cache approaching size limit: {0}%",
            "Stale data detected for key {0}"
        ],
        "ERROR": [
            "Cache eviction error: {0}",
            "Failed to store item {0} in cache",
            "Cache corruption detected"
        ],
        "DEBUG": [
            "Cache lookup for key {0}",
            "Cache eviction policy triggered"
        ],
        "CRITICAL": [
            "Cache server unresponsive",
            "Cache data loss detected"
        ]
    },
    "scheduler": {
        "INFO": [
            "Task {0} scheduled for {1}",
            "Cron job {0} completed successfully",
            "Next maintenance window: {0}",
            "Scheduler status: {0} active tasks"
        ],
        "WARNING": [
            "Task {0} delayed by {1}s",
            "Scheduler approaching task limit",
            "Cron job {0} taking longer than expected"
        ],
        "ERROR": [
            "Task {0} failed to schedule: {1}",
            "Cron job {0} failed: {1}",
            "Scheduler missed {0} events"
        ],
        "DEBUG": [
            "Task {0} details: {1}",
            "Scheduler checking for due tasks"
        ],
        "CRITICAL": [
            "Scheduler service down",
            "Critical scheduled task {0} missed"
        ]
    }
}

# User IDs and endpoints for realistic logs
USER_IDS = [f"user_{i}" for i in range(1, 50)]
API_ENDPOINTS = ["/api/v1/users", "/api/v1/products", "/api/v1/orders", "/api/v1/auth", "/api/v1/search"]
IP_ADDRESSES = [f"192.168.1.{i}" for i in range(1, 100)] + [f"10.0.0.{i}" for i in range(1, 50)]
RESOURCES = ["profile", "settings", "dashboard", "report", "admin", "billing"]
PAGE_NAMES = ["/home", "/products", "/about", "/contact", "/dashboard", "/login", "/profile"]
JOB_TYPES = ["email_delivery", "report_generation", "data_import", "cleanup", "backup", "sync"]
CACHE_KEYS = ["user_profile", "product_list", "settings", "preferences", "recent_items"]

def random_endpoint():
    """Return a random API endpoint."""
    return random.choice(API_ENDPOINTS)

def random_user_id():
    """Return a random user ID."""
    return random.choice(USER_IDS)

def random_ip():
    """Return a random IP address."""
    return random.choice(IP_ADDRESSES)

def random_resource():
    """Return a random resource name."""
    return random.choice(RESOURCES)

def random_page():
    """Return a random page name."""
    return random.choice(PAGE_NAMES)

def random_job():
    """Return a random job type."""
    return random.choice(JOB_TYPES)

def random_cache_key():
    """Return a random cache key."""
    return random.choice(CACHE_KEYS)

def format_message(component, level):
    """Get a random message template for the component and level, and format it."""
    if component not in MESSAGES or level not in MESSAGES[component]:
        return "Generic log message"
    
    template = random.choice(MESSAGES[component][level])
    
    # Check for both {0} and {1} placeholders
    has_second_placeholder = "{1}" in template
    
    # Format with appropriate values based on the placeholders
    if "{0}" in template:
        if component == "api":
            if "endpoint" in template:
                if has_second_placeholder:
                    return template.format(random_endpoint(), random_resource())
                return template.format(random_endpoint())
            elif "User" in template:
                return template.format(random_user_id(), random_resource())
            elif "Rate limit" in template:
                return template.format(random.randint(1, 100), 100)
            elif "ms" in template:
                return template.format(random.randint(10, 500))
            elif "IP" in template:
                if has_second_placeholder:
                    return template.format(random_ip(), random_resource())
                return template.format(random_ip())
            elif "failed" in template:
                if has_second_placeholder:
                    return template.format("Timeout error" if random.random() < 0.5 else "Invalid parameters", random_resource())
                return template.format("Timeout error" if random.random() < 0.5 else "Invalid parameters")
            elif "unresponsive" in template:
                if has_second_placeholder:
                    return template.format(random.randint(10, 60), random_resource())
                return template.format(random.randint(10, 60))
            elif "failing" in template:
                if has_second_placeholder:
                    return template.format(", ".join(random.sample(API_ENDPOINTS, random.randint(1, 3))), random_resource())
                return template.format(", ".join(random.sample(API_ENDPOINTS, random.randint(1, 3))))
            else:
                if has_second_placeholder:
                    return template.format(random_endpoint(), random_resource())
                return template.format(random_endpoint())
        
        elif component == "database":
            if "ms" in template:
                return template.format(random.randint(5, 2000))
            elif "pool" in template:
                return template.format(random.randint(10, 45), 50)
            elif "cleanup" in template:
                return template.format(random.randint(1, 30))
            elif "Rows" in template:
                return template.format(random.randint(1, 1000))
            elif "fragmentation" in template:
                return template.format(random.randint(5, 95))
            elif "failed" in template or "error" in template:
                return template.format("Connection timeout" if random.random() < 0.5 else "Constraint violation")
            elif "Deadlock" in template or "table" in template:
                return template.format("users" if random.random() < 0.5 else "transactions")
            elif "plan" in template or "locks" in template:
                return template.format("(details omitted for brevity)")
            else:
                return template.format(random.randint(1, 100))
                
        elif component == "auth":
            if "logged in" in template or "Password" in template or "account" in template:
                return template.format(random_user_id())
            elif "failed login" in template or "expired" in template:
                return template.format(random_user_id())
            elif "location" in template:
                return template.format(random_user_id(), "New York" if random.random() < 0.5 else "Tokyo")
            elif "Login failed" in template:
                return template.format(random_user_id(), "Invalid password" if random.random() < 0.5 else "Account disabled")
            elif "locked" in template or "Invalid token" in template:
                return template.format(random_user_id())
            elif "Token" in template or "Auth flow" in template:
                return template.format(random_user_id())
            elif "brute force" in template:
                return template.format(random_ip())
            elif "breach" in template:
                return template.format(random_user_id())
            else:
                return template.format(random_user_id())
                
        elif component == "frontend":
            if "Page" in template and "loaded" in template:
                return template.format(random_page(), random.randint(50, 5000))
            elif "User" in template and "viewed" in template:
                return template.format(random_user_id(), random_page())
            elif "Asset" in template:
                return template.format(f"styles-{random.randint(1, 10)}.css" if random.random() < 0.5 else f"script-{random.randint(1, 10)}.js")
            elif "Form" in template:
                return template.format("contact" if random.random() < 0.5 else "signup")
            elif "Slow page" in template:
                return template.format(random_page(), random.randint(2000, 10000))
            elif "error" in template:
                return template.format("Uncaught TypeError" if random.random() < 0.5 else "Failed to fetch")
            elif "parsing" in template:
                return template.format(f"styles-{random.randint(1, 10)}.css")
            elif "DOM" in template:
                return template.format(random.randint(50, 500))
            elif "Event" in template:
                return template.format("#submit-button" if random.random() < 0.5 else ".nav-item")
            elif "crash" in template:
                return template.format("OutOfMemoryError" if random.random() < 0.5 else "JS exception")
            elif "blocked" in template:
                return template.format("large-script.js" if random.random() < 0.5 else "render-blocking-css.css")
            else:
                return template.format(random_page())
                
        elif component == "worker":
            if "Job" in template and ("completed" in template or "running" in template):
                return template.format(f"{random_job()}-{random.randint(1000, 9999)}", random.randint(1, 600))
            elif "Queue status" in template:
                return template.format(random.randint(0, 100))
            elif "Worker" in template and "processed" in template:
                return template.format(f"worker-{random.randint(1, 10)}", random.randint(10, 200))
            elif "Job" in template and "started" in template:
                return template.format(f"{random_job()}-{random.randint(1000, 9999)}")
            elif "approaching memory" in template:
                return template.format(f"worker-{random.randint(1, 10)}")
            elif "backlog" in template:
                return template.format(random.randint(50, 500))
            elif "Job" in template and "failed" in template:
                return template.format(f"{random_job()}-{random.randint(1000, 9999)}", "Timeout" if random.random() < 0.5 else "Resource exhaustion")
            elif "Worker" in template and "crashed" in template:
                return template.format(f"worker-{random.randint(1, 10)}")
            elif "Job" in template and "details" in template:
                return template.format(f"{random_job()}-{random.randint(1000, 9999)}", "params={input: 'data.csv', output: 'results.json'}")
            elif "memory usage" in template:
                return template.format(f"worker-{random.randint(1, 10)}", random.randint(100, 2000))
            elif "Critical job" in template:
                return template.format(f"{random_job()}-{random.randint(1000, 9999)}")
            else:
                return template.format(f"{random_job()}-{random.randint(1000, 9999)}")
                
        elif component == "cache":
            if "ratio" in template:
                return template.format(random.randint(50, 99))
            elif "Item" in template and "added" in template:
                return template.format(f"{random_cache_key()}:{random_user_id()}")
            elif "size" in template:
                return template.format(random.randint(100, 8000))
            elif "refreshed" in template:
                return template.format(f"{random_cache_key()}:{random_user_id()}")
            elif "miss rate" in template:
                return template.format(random.randint(5, 50))
            elif "approaching size limit" in template:
                return template.format(random.randint(80, 95))
            elif "Stale data" in template:
                return template.format(f"{random_cache_key()}:{random_user_id()}")
            elif "eviction error" in template:
                return template.format("Out of memory" if random.random() < 0.5 else "Lock timeout")
            elif "Failed to store" in template:
                return template.format(f"{random_cache_key()}:{random_user_id()}")
            elif "lookup" in template:
                return template.format(f"{random_cache_key()}:{random_user_id()}")
            else:
                return template.format(random_cache_key())
                
        elif component == "scheduler":
            if "Task" in template and "scheduled" in template:
                return template.format(f"{random_job()}_task", (datetime.datetime.now() + datetime.timedelta(minutes=random.randint(5, 60))).strftime("%Y-%m-%d %H:%M:%S"))
            elif "Cron job" in template and "completed" in template:
                return template.format(f"cron_{random_job()}")
            elif "Next maintenance" in template:
                return template.format((datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d %H:%M:%S"))
            elif "Scheduler status" in template:
                return template.format(random.randint(5, 50))
            elif "Task" in template and "delayed" in template:
                return template.format(f"{random_job()}_task", random.randint(10, 300))
            elif "taking longer" in template:
                return template.format(f"cron_{random_job()}")
            elif "failed to schedule" in template:
                return template.format(f"{random_job()}_task", "Resource conflict" if random.random() < 0.5 else "Invalid timing")
            elif "Cron job" in template and "failed" in template:
                return template.format(f"cron_{random_job()}", "Timeout" if random.random() < 0.5 else "Dependency error")
            elif "missed" in template:
                return template.format(random.randint(1, 10))
            elif "Task" in template and "details" in template:
                return template.format(f"{random_job()}_task", "priority=high, retry=3")
            elif "Critical scheduled task" in template:
                return template.format(f"critical_{random_job()}")
            else:
                return template.format(f"{random_job()}_task")
    
    return template

def generate_log_entry(timestamp):
    """Generate a single log entry at the given timestamp."""
    # Select component and level based on weights
    component = random.choice(COMPONENTS)
    level = random.choices(
        list(LOG_LEVELS.keys()),
        weights=list(LOG_LEVELS.values())
    )[0]
    
    # Format the log entry
    message = format_message(component, level)
    return f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')} [{level}] {component}: {message}"

def generate_log_file(filename, num_entries, start_date):
    """Generate a log file with the specified number of entries."""
    with open(filename, 'w') as f:
        # Create a current timestamp that will be incremented
        current_time = start_date
        
        # Generate log entries with increasing timestamps
        for _ in range(num_entries):
            # Add some randomness to the time increments
            time_increment = datetime.timedelta(
                seconds=random.randint(1, 10),
                microseconds=random.randint(0, 999999)
            )
            current_time += time_increment
            
            # Generate and write the log entry
            log_entry = generate_log_entry(current_time)
            f.write(log_entry + '\n')
            
        # Add some anomalies (bursts of errors)
        if random.random() < 0.7:  # 70% chance to include anomalies
            # Jump forward in time a bit
            current_time += datetime.timedelta(minutes=random.randint(5, 30))
            
            # Generate a burst of errors
            burst_size = random.randint(5, 15)
            for _ in range(burst_size):
                # Small time increments between errors in a burst
                current_time += datetime.timedelta(
                    seconds=random.randint(0, 2),
                    microseconds=random.randint(0, 999999)
                )
                
                # Select component for this error burst
                burst_component = random.choice(COMPONENTS)
                
                # Higher chance of ERROR or CRITICAL
                level = random.choices(
                    ["ERROR", "CRITICAL", "WARNING"],
                    weights=[0.6, 0.3, 0.1]
                )[0]
                
                log_entry = f"{current_time.strftime('%Y-%m-%d %H:%M:%S')} [{level}] {burst_component}: {format_message(burst_component, level)}"
                f.write(log_entry + '\n')

def main():
    """Generate sample log files."""
    print(f"Generating {NUM_FILES} log files with {ENTRIES_PER_FILE} entries each...")
    
    for i in range(1, NUM_FILES + 1):
        # Stagger start dates slightly for different files
        file_start_date = START_DATE + datetime.timedelta(days=i-1)
        
        # Generate the log file
        filename = OUTPUT_DIR / f"server_{i}.log"
        generate_log_file(filename, ENTRIES_PER_FILE, file_start_date)
        print(f"Created {filename}")
        
    print(f"Log files successfully generated in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
