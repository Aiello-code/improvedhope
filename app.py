from flask import Flask, render_template
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Function to fetch data from the database
def fetch_data():
    conn = sqlite3.connect('trump_mentions.db')
    cursor = conn.cursor()
    cursor.execute("SELECT mention_count, timestamp FROM mentions ORDER BY timestamp DESC LIMIT 1")
    latest_data = cursor.fetchone()
    
    # Get mentions for the last 24 hours, last 7 days, and all-time
    cursor.execute("SELECT mention_count FROM mentions WHERE timestamp > ?", (datetime.now() - timedelta(days=1),))
    last_24_hours = cursor.fetchall()
    
    cursor.execute("SELECT mention_count FROM mentions WHERE timestamp > ?", (datetime.now() - timedelta(weeks=1),))
    last_7_days = cursor.fetchall()
    
    cursor.execute("SELECT MAX(mention_count), MIN(mention_count) FROM mentions")
    all_time_stats = cursor.fetchone()
    
    conn.close()

    return {
        "latest_data": latest_data,
        "last_24_hours": last_24_hours,
        "last_7_days": last_7_days,
        "all_time_stats": all_time_stats,
    }

@app.route("/")
def index():
    data = fetch_data()
    
    # Get statistics
    latest_mentions = data['latest_data'][0]
    last_24_hours = [row[0] for row in data['last_24_hours']]
    last_7_days = [row[0] for row in data['last_7_days']]
    highest_all_time, lowest_all_time = data['all_time_stats']
    
    # Calculate stats
    highest_24h = max(last_24_hours) if last_24_hours else 0
    lowest_24h = min(last_24_hours) if last_24_hours else 0
    highest_7d = max(last_7_days) if last_7_days else 0
    lowest_7d = min(last_7_days) if last_7_days else 0
    
    all_time_high = highest_all_time if highest_all_time else 0
    all_time_low = lowest_all_time if lowest_all_time else 0
    
    return render_template('index.html', 
                           latest_mentions=latest_mentions,
                           highest_24h=highest_24h,
                           lowest_24h=lowest_24h,
                           highest_7d=highest_7d,
                           lowest_7d=lowest_7d,
                           all_time_high=all_time_high,
                           all_time_low=all_time_low)

if __name__ == "__main__":
    app.run(debug=True)
