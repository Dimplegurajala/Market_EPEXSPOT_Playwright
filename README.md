# Market Results Automation Suite (EPEX SPOT)

## Overview
A production-grade automation ecosystem developed for Brady Technologies to scrape, validate, and performance-test GB 30-minute market data. This framework demonstrates a **Shift-Left** strategy, prioritizing data integrity and system reliability in high-compliance financial environments.

## Tech Stack
- **Automation:** Playwright (Python)
- **Performance:** Locust
- **Mocking:** Flask (API Contract Testing)
- **Validation:** JSON Schema
- **CI/CD:** GitHub Actions (Automated Workflow)
- **Standards:** Page Object Model (POM), Pathlib, PEP 8

## Performance & Load Results (Locust)
To validate the robustness of the data ingestion layer and numeric parsing logic, I executed a sustained stress test against a localized API:
- **Total Requests Executed:** 9,411
- **Concurrent Users:** 10
- **Success Rate:** 100.0% (Zero Failures)
- **Average Latency:** 7.98ms
- **99th Percentile:** 20ms

## Key Engineering Decisions
- **Environment Detection:** Implemented dynamic headless toggling (`os.getenv("CI")`) to ensure the framework is "CI-Ready" while maintaining local visibility for exploratory testing.
- **Direct URL Construction:** Bypassed reactive DOM race conditions by injecting ISO-calculated query parameters directly into the navigation layer.
- **Data Integrity Guardrails:** Integrated JSON Schema validation within the extraction loop to ensure 100% adherence to financial data contracts before CSV persistence.
- **Behavioral Pacing:** Replaced aggressive stealth plugins with `slow_mo` pacing and standardized viewports to improve reliability against anti-bot challenges on the EPEX SPOT site.

## Project Structure
- `/pages`: Page Object Model implementation.
- `/tests`: Functional test suites including dynamic date calculation.
- `/data`: CSV extraction outputs (Git ignored).
- `mock_server.py`: Flask-based Mock Service for hermetic testing.
- `locustfile.py`: Performance benchmark definitions.
- `.github/workflows/brady.yml`: Automated CI/CD pipeline.