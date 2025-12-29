from datetime import datetime, timedelta
from pages.market_results_page import MarketResultsPage
import pytest

def test_brady_assessment(page):
    # 1. Calculate yesterday date dynamically
    target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    # 2. Construct URL- with all the filter selections
    direct_url = (
        f"https://www.epexspot.com/en/market-results?"
        f"modality=Continuous&product=30&market_area=GB&"
        f"delivery_date={target_date}&data_mode=table"
    )

    market_page = MarketResultsPage(page)
    
    try:
        # 3. Navigate and Wait for Hydration
        market_page.navigate(direct_url)
        page.wait_for_load_state("networkidle")
        
        # Handle cookies
        market_page.handle_cookies()

        # 4. Wait for the specific data element to be attached to the DOM
        page.wait_for_selector("li.sub-child a", state="attached", timeout=15000)
        
        # 5. Execute Data Extraction
        filepath = market_page.scrape_to_csv()
        
        # 6. Final Validation
        assert filepath is not None, f"Scrape failed for {target_date}."
        print(f"File saved successfully at: {filepath}")
        
    finally:
        # Ensure the page is closed even if the test fails
        page.close()