from locust import HttpUser, task, between
import logging

class BradyPerformanceTest(HttpUser):
    # Pacing: 1-2 seconds between tasks mimics human-like behavior 
    wait_time = between(1, 2)

    @task
    def test_dynamic_market_data(self):
        #Validates API Contract and Data Integrity for 30-min market results.
        with self.client.get("/api/market-results", catch_response=True, name="GET_Market_Results") as response:
            try:
                if response.status_code == 200:
                    data = response.json()
                    
                    # 1. Row Count Validation (Standard)
                    if len(data) != 48:
                        return response.failure(f"Contract Violation: Expected 48 rows, got {len(data)}")

                    # 2. Schema & Type Validation (Senior Level) 
                    # Check the first row to ensure the schema hasn't changed
                    first_row = data[0]
                    required_keys = ["Hours", "Low", "High", "Last", "Weight Avg."]
                    
                    if not all(key in first_row for key in required_keys):
                        return response.failure("Schema Mismatch: Missing required keys in JSON response")

                    # 3. Logical Data Integrity Check 
                    # Ensure numeric fields are actually floats and logically sound
                    if not isinstance(first_row["Weight Avg."], (int, float)):
                        return response.failure("Data Type Error: 'Weight Avg.' must be a number")

                    response.success()
                else:
                    response.failure(f"HTTP Error: {response.status_code}")
            
            except Exception as e:
                response.failure(f"Parsing Failure: {str(e)}")