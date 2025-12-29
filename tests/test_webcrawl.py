from datetime import datetime, timedelta
from pages.market_results_page import MarketResultsPage
import pytest

def test_brady_assessment(page):
    # 1. Force Desktop Viewport for consistent table rendering
    page.set_viewport_size({"width": 1920, "height": 1080})
    
    # 2. Dynamic Date Calculation
    target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 3. Dynamic URL Construction
    direct_url = (
        f"https://www.epexspot.com/en/market-results?"
        f"modality=Continuous&product=30&market_area=GB&"
        f"delivery_date={target_date}&data_mode=table"
    )

    market_page = MarketResultsPage(page)
    
    try:
        # STEP 1: Session Warming
        # Visit base page to set cookies and initialize JS
        page.goto("https://www.epexspot.com/en/market-results", wait_until="domcontentloaded")
        market_page.handle_cookies()

        # STEP 2: Direct Navigation
        page.goto(direct_url, wait_until="networkidle")
        
        # STEP 3: Data-Centric Wait
        # We wait for the table rows directly, ignoring the flaky side menu
        page.wait_for_selector("table tbody tr", state="attached", timeout=30000)

        # STEP 4: Scrape & Validate
        # This will now return None (and fail the assert) if no rows are found
        filepath = market_page.scrape_to_csv()
        
        # 5. Professional Assertions
        assert filepath is not None, f"Scrape failed: No data extracted for {target_date}."
        print(f"File saved successfully at: {filepath}")
        
    except Exception as e:
        # Re-raise the error so Pytest (and GitHub Actions) records a Failure
        # This prevents the 'Silent Pass' you were experiencing
        print(f"Critical Scraper Failure: {e}")
        raise e 
    finally:
        page.close()