from datetime import datetime, timedelta
from pages.market_results_page import MarketResultsPage
import pytest

def test_brady_assessment(page):
    # 1. FORCE DESKTOP VIEWPORT (Solves the 'unrecognized arguments' error)
    # This ensures the menu structure is the same locally and in GitHub Actions
    page.set_viewport_size({"width": 1920, "height": 1080})

    # 2. Date Calculation
    target_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    # 3. Build URL
    direct_url = (
        f"https://www.epexspot.com/en/market-results?"
        f"modality=Continuous&product=30&market_area=GB&"
        f"delivery_date={target_date}&data_mode=table"
    )

    market_page = MarketResultsPage(page)
    
    try:
        # 4. Navigate
        market_page.navigate(direct_url)
        page.wait_for_load_state("networkidle")
        
        # 5. Handle Cookies
        market_page.handle_cookies()

        # 6. Revert to your original working selector
        # 'attached' is best for menus that might be hidden by hover states
        page.wait_for_selector("li.sub-child a", state="attached", timeout=30000)
        
        # 7. Extract Data
        filepath = market_page.scrape_to_csv()
        
        assert filepath is not None, f"Scrape failed for {target_date}."
        print(f"File saved successfully at: {filepath}")
        
    finally:
        page.close()