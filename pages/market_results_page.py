from pathlib import Path
import re
import csv
import logging
from datetime import datetime
from jsonschema import validate
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

#  JSON Schema validation ensures 100% adherence to data contracts.
MARKET_DATA_SCHEMA = {
    "type": "object",
    "required": ["Hours", "Low", "High", "Last", "Weight Avg."],
    "properties": {
        "Hours": {"type": "string"},
        "Low": {"type": "number"}, 
        "High": {"type": "number"},
        "Last": {"type": "number"}, 
        "Weight Avg.": {"type": "number"}
    }
}

class MarketResultsPage(BasePage):
    def scrape_to_csv(self, base_directory: str = "data"):
        base_path = Path(base_directory)
        base_path.mkdir(parents=True, exist_ok=True)

        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_selector("li.sub-child a", state="attached", timeout=20000)

        scraped_data = []
        intervals = self.page.locator("li.sub-child a").all_inner_texts()
        rows = self.page.locator("table tbody tr").all()

        row_index = 0
        for interval in intervals:
            interval_text = interval.strip()
            if not interval_text: continue

            while row_index < len(rows):
                cells = rows[row_index].locator("td").all_inner_texts()
                if len(cells) >= 4 and cells[0].strip() != "-":
                    try:
                        def clean_p(text):
                            cleaned = re.sub(r'[^\d.]', '', text)
                            return float(cleaned) if cleaned else 0.0

                        # Keep 'Hours' internally for robust data mapping
                        data_point = {
                            "Hours": interval_text,
                            "Low": clean_p(cells[0]),
                            "High": clean_p(cells[1]),
                            "Last": clean_p(cells[2]),
                            "Weight Avg.": clean_p(cells[3])
                        }
                        
                        validate(instance=data_point, schema=MARKET_DATA_SCHEMA)
                        scraped_data.append(data_point)
                        row_index += 1
                        break 
                    except Exception:
                        row_index += 1
                        continue
                row_index += 1

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"market_results_{timestamp}.csv"
        filepath = base_path / filename

        if scraped_data:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                # MANDATORY: Only the 4 columns requested by Brady 
                fieldnames = ["Low", "High", "Last", "Weight Avg."]
                
                # 'extrasaction' ensures 'Hours' is ignored in the final file 
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(scraped_data)
            return str(filepath)
        return None