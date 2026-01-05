import pytest
import logging
import os
from pathlib import Path
from datetime import datetime

#utilizing logger feature instead of print statements-- to make sure terminal is cleaner
@pytest.fixture(scope="function", autouse=True)
def setup_logging():
    """Centralized logging for auditability and Root Cause Analysis."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"execution_{datetime.now().strftime('%H-%M-%S')}.log"
    
    logger = logging.getLogger()
    for handler in logger.handlers[:]: 
        logger.removeHandler(handler)
        
    logging.basicConfig(
        level=logging.INFO, 
        filename=str(log_file), 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    yield

@pytest.fixture(scope="session")
def context(playwright):
    
    
    #Uses environment detection to switch between Headed (Local) and Headless (CICD).
    
    # Detect if we are in GitHub Actions (CI=true is default in GH Actions)
    is_headless = os.getenv("CI") == "true" 
    
    # Persistent context helps maintain session state for dynamic sites
    user_data_path = "./user_data"
    
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_path,
        headless=is_headless,
        # Pacing for behavioral simulation: 50ms locally, 0ms for CI speed - to bypass bot
        slow_mo=50 if not is_headless else 0, 
        viewport={"width": 1280, "height": 720}, 
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox"
        ]
    )
    yield context
    context.close()

@pytest.fixture(scope="function")
def page(context):
    #Provides a fresh page for each test while sharing the session context.
    page = context.new_page()
    
    # Performance Optimization: Aborting media assets to prioritize data extraction
    page.route("**/*.{png,jpg,jpeg,gif}", lambda route: route.abort())
    
    yield page
    page.close()

@pytest.fixture(scope="function")
def resilient_page(context):
    
    #Page fixture configured for Resilience Testing.
    #Simulates a 503 Service Unavailable to verify error handling.
    
    page = context.new_page()
    
    # Intercepting Market Results requests to simulate an outage
    page.route("**/market-results**", lambda route: route.fulfill(
        status=503,
        content_type="text/plain",
        body="Service Unavailable: EPEX SPOT Server is Down"
    ))
    
    yield page
    page.close()

import shutil

def pytest_sessionstart(session):
    """
    Standard Engineering Practice: Clean up stale artifacts before execution.
    Ensures that the /logs and /reports directories only contain fresh data.
    """
    directories = ['logs', 'user_data'] # user_data holds Playwright persistent state
    for directory in directories:
        path = Path(directory)
        if path.exists():
            shutil.rmtree(path)
            logging.info(f"Cleaned up stale directory: {directory}")
        path.mkdir(parents=True, exist_ok=True)