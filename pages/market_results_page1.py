from pathlib import Path
import re
import csv
import logging
from datetime import datetime
from jsonschema import validate
from pages.base_page import BasePage

logger = logging.getLogger(__name__)

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
    
    def _normalize_price(self, text: str) -> float:
      
    # Handle empty or null values immediately
      if not text or text.strip() == "-":
        return 0.0
    
      val = text.strip()
    
    # If comma is found after the dot, it's European (1.234,56)
      if val.rfind(',') > val.rfind('.'):
        val = val.replace('.', '').replace(',', '.')
      else:
        # Standard/UK format: just strip the thousands-separator comma
        val = val.replace(',', '')
        
    # Remove any remaining non-numeric characters (except the decimal dot)
      val = re.sub(r'[^\d.]', '', val)
      return float(val) if val else 0.0

    def _validate_financial_invariants(self, data: dict):
        
        low = data["Low"]
        high = data["High"]
        w_avg = data["Weight Avg."]

        if not (low <= w_avg <= high):
            logger.warning(f"Invariant Violation at {data['Hours']}: Low({low}) > W.Avg({w_avg}) or W.Avg > High({high})")
            # You can choose to raise an error or just log it for auditability
            # raise ValueError("Financial Invariant Violation")

    def scrape_to_csv(self, base_directory: str = "data"):
        base_path = Path(base_directory)
        base_path.mkdir(parents=True, exist_ok=True)

        self.page.wait_for_load_state("networkidle")
        
        scraped_data = []
        # [cite_start]Target the specific EPEX SPOT table structure [cite: 11, 16]
        intervals = self.page.locator("li.sub-child a").all_inner_texts()
        rows = self.page.locator("table tbody tr").all()

        row_index = 0
        for interval in intervals:
            interval_text = interval.strip()
            if not interval_text: continue

            while row_index < len(rows):
                cells = rows[row_index].locator("td").all_inner_texts()
                
                # [cite_start]Check for the 4 required columns [cite: 11]
                if len(cells) >= 4 and cells[0].strip() != "-":
                    try:
                        data_point = {
                            "Hours": interval_text,
                            "Low": self._normalize_price(cells[0]),
                            "High": self._normalize_price(cells[1]),
                            "Last": self._normalize_price(cells[2]),
                            "Weight Avg.": self._normalize_price(cells[3])
                        }
                        
                        # Step 1: Schema Validation (Data Types)
                        validate(instance=data_point, schema=MARKET_DATA_SCHEMA)
                        
                        # Step 2: Financial Invariant Validation (Business Logic)
                        self._validate_financial_invariants(data_point)
                        
                        scraped_data.append(data_point)
                        row_index += 1
                        break 
                    except Exception as e:
                        logger.error(f"Validation failed for row {row_index}: {e}")
                        row_index += 1
                        continue
                row_index += 1

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"market_results_{timestamp}.csv"
        filepath = base_path / filename

        if scraped_data:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                # [cite_start]Requirement: Only Low, High, Last, Weight Avg [cite: 11, 12]
                fieldnames = ["Low", "High", "Last", "Weight Avg."]
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(scraped_data)
            return str(filepath)
        return None