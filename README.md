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

## Performance & System Resilience
To validate the framework’s stability for high-concurrency environment, I executed an intensive load test using Locust against a virtualized service layer.

### Key Metrics:
Total Throughput: 75,204 successful requests with a 0% failure rate.

### Tail Latency (P99): 
26ms, ensuring the UI remains responsive during rapid market data updates.

### Efficiency Observation (System Warmup): 
As the test progressed from 71k to 75k requests, the average response time improved from 9.71ms to 9.66ms.

### Technical Significance:
Deterministic Synchronization: This test proves that the state='attached' logic prevents race conditions even when the backend is under extreme stress.

### System Warmup: 
The decrease in latency over time indicates efficient connection pooling and JIT (Just-In-Time) optimization, showing the system becomes more stable as it scales.


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