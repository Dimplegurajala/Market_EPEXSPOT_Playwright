import requests
import pytest

# The local endpoint for your Hermetic Mock Service
BASE_URL = "http://127.0.0.1:5000/api/market-results"

def test_market_data_contract():
    #Validates the API Contract and Data Integrity for financial results."""
    response = requests.get(BASE_URL)
    
    # Assert successful communication witht he server
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}"
    
    data = response.json()
    
    # 1. Validate Interval Count (48 Data-Entires for a 24-hour GB market)
    assert len(data) == 48, f"Expected 48 intervals for a full market day, but found {len(data)}"
    
    # 2.Validating Data Types 
    first_record = data[0]
    required_keys = ["Hours", "Low", "High", "Last", "Weight Avg."]
    
    for key in required_keys:
        assert key in first_record, f"Missing required financial key: {key}"
        
    # 3.Validate Financial Logic (High should never be lower than Low)
    assert first_record["High"] >= first_record["Low"], "Financial Data Inconsistency: High price is lower than Low price"
    
    # 4.Validating Weight Avg. Calculation - (Low+High+Last)/3
    calculated_avg = round((first_record["Low"] + first_record["High"] + first_record["Last"]) / 3, 2)
    assert first_record["Weight Avg."] == calculated_avg, "Weight Avg calculation mismatch"

def test_api_latency_threshold():
    # p99 Threshold 
    response = requests.get(BASE_URL)
    # Ensuring the 'Time to First Byte' is acceptable for financial ingestion
    assert response.elapsed.total_seconds() < 0.05, "API Latency exceeded 50ms threshold"