import os
import json
import random
from datetime import datetime
import pandas as pd

# Configuration Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "../dat/json/changes_log.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "../dat/json/dashboard_stats.json")

def get_mock_weather():
    """Generates mock weather data."""
    conditions = ["Sunny", "Cloudy", "Rainy", "Stormy", "Partly Cloudy"]
    return {
        "temperature_c": random.randint(20, 35),
        "humidity_percent": random.randint(40, 90),
        "condition": random.choice(conditions),
        "location": "Local Server"
    }

def analyze_logs():
    """Reads logs and calculates frequent file types."""
    stats = {}
    
    try:
        if not os.path.exists(LOG_FILE):
            print(f"Warning: Log file not found at {LOG_FILE}. Returning empty stats.")
            return {}

        # Read JSON Lines file
        df = pd.read_json(LOG_FILE, lines=True)

        if df.empty:
            return {}

        # Extract file extensions
        # Assuming 'file' column exists. Example: "data.txt" -> ".txt"
        df['extension'] = df['file'].apply(lambda x: os.path.splitext(x)[1].lower() if x else "unknown")
        
        # Count frequency of extensions
        type_counts = df['extension'].value_counts().to_dict()
        
        return type_counts

    except ValueError:
        print("Error: Log file format is invalid or empty.")
        return {}
    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        return {}

def main():
    print("Starting Analytics Module...")

    # 1. Analyze Data
    frequent_types = analyze_logs()
    
    # 2. Get Environment Data
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    weather_data = get_mock_weather()

    # 3. Construct Dashboard Data
    dashboard_data = {
        "frequent_analytics": frequent_types,
        "current_datetime": current_time,
        "weather": weather_data,
        "status": "active"
    }

    # 4. Save to JSON
    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(dashboard_data, f, indent=4)
        
        print(f"Dashboard stats successfully saved to: {OUTPUT_FILE}")
        print("Data Preview:", json.dumps(dashboard_data, indent=2))
        
    except IOError as e:
        print(f"Error saving dashboard stats: {e}")

if __name__ == "__main__":
    main()
