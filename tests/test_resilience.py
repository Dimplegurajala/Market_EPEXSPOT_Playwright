import logging
import pytest

def test_503_error_handling(resilient_page):
    
    #Validates that the framework detects a 503 error and 
    #handles it with a clear error message instead of crashing.
    
    try:
        # This will hit the 503 route we defined in conftest.py
        response = resilient_page.goto("https://www.epexspot.com/en/market-results")
        
        # Validate that we successfully captured the failure
        assert response.status == 503
        logging.info("Resilience Check Passed: System successfully identified 503 Outage.")
        
    except Exception as e:
        logging.error(f"System crashed during 503 simulation: {e}")
        pytest.fail("Framework did not handle 503 error gracefully.")