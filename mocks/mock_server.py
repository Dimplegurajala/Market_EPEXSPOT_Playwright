from flask import Flask, jsonify
import random

app = Flask(__name__)

def generate_30min_intervals():
    #Generates 48 intervals for a 24-hour period.
    intervals = []
    for hour in range(24):
        for minute in ["00", "30"]:
            next_hour = hour if minute == "00" else (hour + 1) % 24
            next_min = "30" if minute == "00" else "00"
            intervals.append(f"{hour:02d}:{minute} - {next_hour:02d}:{next_min}")
    return intervals

@app.route('/api/market-results', methods=['GET'])
def get_market_results():
    intervals = generate_30min_intervals()
    dynamic_data = []
    
    for interval in intervals:
        # Generate random but realistic price data based on yesterdays screenshot
        low = round(random.uniform(40.0, 60.0), 2)
        high = round(random.uniform(70.0, 90.0), 2)
        last = round(random.uniform(60.0, 80.0), 2)
        weight_avg = round((low + high + last) / 3, 2)
        
        dynamic_data.append({
            "Hours": interval,
            "Low": low,
            "High": high,
            "Last": last,
            "Weight Avg.": weight_avg
        })
    
    return jsonify(dynamic_data)

if __name__ == '__main__':
    # Running on port 5000 as requested for standard mock services - and using it in Locust host too
    app.run(port=5000, debug=True)