import logging
from playwright.sync_api import Page

logger = logging.getLogger(__name__)

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str):
        self.page.goto(url, wait_until="load")
        logger.info(f"Navigated to: {url}")

    def handle_cookies(self):
        try:
            self.page.get_by_role("button", name="Allow all cookies").click(timeout=5000)
            logger.info("Cookie banner dismissed.")
        except:
            logger.warning("Cookie banner not found.")