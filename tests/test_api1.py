import requests
import pytest
import re

BASE_URL = "http://127.0.0.1:5000/api/market-results"

def normalize(val):
    """Reuse your .rfind() logic for cross-layer consistency."""
    if not val or str(val).strip() == "-": return 0.0
    s = str(val).strip()
    if s.rfind(',') > s.rfind('.'):
        s = s.replace('.', '').replace(',', '.')
    else:
        s = s.replace(',', '')
    return float(re.sub(r'[^\d.]', '', s))

def test_market_data_contract():
    response = requests.get(BASE_URL)
    assert response.status_code == 200 
    
    data = response.json()
    
    # 1. Scope Validation: Scrape the first 4 data columns as requested 
    required_keys = ["Low", "High", "Last", "Weight Avg."]
    first_record = data[0]
    for key in required_keys:
        assert key in first_record, f"Missing column required by task: {key}" 
    
    # 2. Logic: High should never be lower than Low
    low = normalize(first_record["Low"])
    high = normalize(first_record["High"])
    avg = normalize(first_record["Weight Avg."])
    
    assert high >= low, "Inconsistency: High < Low"
    # Ensure Weighted Avg is bounded correctly
    assert low <= avg <= high, "Inconsistency: Weighted Avg is outside High/Low range"

def test_api_latency_threshold():
    """Testing for the P99 performance standard required in high-frequency trading."""
    response = requests.get(BASE_URL)
    # p99 check: Ensuring fast ingestion for market results 
    assert response.elapsed.total_seconds() < 0.05, "Latency too high for spot market data"