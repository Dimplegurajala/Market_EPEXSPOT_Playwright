import re
import logging
from locust import HttpUser, task, between

class BradyPerformanceTest(HttpUser):
    wait_time = between(1, 2)

    def _normalize_price(self, text: str) -> float:
        """Heuristic Locale Detection - identical to UI logic for consistency."""
        if not text or str(text).strip() == "-":
            return 0.0
        val = str(text).strip()
        # Handle EU vs UK locale detected by last separator position
        if val.rfind(',') > val.rfind('.'):
            val = val.replace('.', '').replace(',', '.')
        else:
            val = val.replace(',', '')
        val = re.sub(r'[^\d.]', '', val)
        return float(val) if val else 0.0

    @task
    def test_dynamic_market_data(self):
        with self.client.get("/api/market-results", catch_response=True, name="GET_Market_Results") as response:
            try:
                if response.status_code == 200:
                    data = response.json()
                    
                    # 1. Contract Validation: Ensure the 4 columns requested are present 
                    required_keys = ["Low", "High", "Last", "Weight Avg."]
                    first_row = data[0]
                    
                    if not all(k in first_row for k in required_keys):
                        return response.failure("Schema Mismatch: Missing required keys")

                    # 2. Logic Check: Financial Invariants across the dataset
                    for entry in data:
                        low = self._normalize_price(entry.get("Low"))
                        high = self._normalize_price(entry.get("High"))
                        avg = self._normalize_price(entry.get("Weight Avg."))

                        # Validation: Low must be floor, High must be ceiling
                        if not (low <= avg <= high):
                            return response.failure(f"Financial Invariant Violation at {entry.get('Hours')}: L:{low} H:{high} Avg:{avg}")

                    response.success()
                else:
                    response.failure(f"HTTP Error: {response.status_code}")
            except Exception as e:
                response.failure(f"Post-Processing Failure: {str(e)}")