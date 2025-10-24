#!/usr/bin/env python3
"""
SharePoint XLSX Scraper
Downloads XLSX file from SharePoint using Selenium web scraping
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# =============================================================================
# CONFIGURATION
# =============================================================================

SHAREPOINT_URL = "https://cfanice-my.sharepoint.com/:x:/g/personal/b_hunalp_rhreflex_com/EU3ys-Z0yutBt2ZsX2OtAIABRVINihppyXSB6hoDyH6WBw?rtime=TTMS5t0S3kg"
DOWNLOAD_DIR = Path("downloads")
TARGET_FILENAME = "NOUVEAU FAC PERSPECTIVIA.xlsx"
HEADLESS = os.environ.get("HEADLESS", "false").lower() == "true"

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'sharepoint_scraper_{datetime.now():%Y%m%d_%H%M%S}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def setup_chrome_driver():
    """Configure and return Chrome WebDriver with anti-detection options"""
    logger.info("Setting up Chrome WebDriver...")

    # Create download directory
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    download_path = str(DOWNLOAD_DIR.absolute())

    options = Options()

    # Headless mode (for GitHub Actions)
    if HEADLESS:
        logger.info("Running in HEADLESS mode")
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

    # Anti-detection options
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # Download preferences
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Specify chromium binary location for GitHub Actions
    options.binary_location = "/usr/bin/chromium-browser"

    driver = webdriver.Chrome(options=options)

    # Mask WebDriver
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
    })

    driver.set_page_load_timeout(90)

    logger.info("Chrome WebDriver configured successfully")
    return driver


def capture_screenshot(driver, step_name):
    """Capture screenshot for debugging"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'screenshot_{step_name}_{timestamp}.png'
        driver.save_screenshot(filename)
        logger.info(f"Screenshot saved: {filename}")
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}")


def wait_for_download(download_dir, timeout=120):
    """Wait for XLSX download to complete"""
    logger.info(f"Waiting for download to complete (timeout: {timeout}s)...")
    seconds = 0

    while seconds < timeout:
        files = list(download_dir.glob("*.xlsx"))
        temp_files = list(download_dir.glob("*.crdownload")) + list(download_dir.glob("*.tmp"))

        if files and not temp_files:
            logger.info(f"Download complete: {files[0].name}")
            return files[0]

        time.sleep(1)
        seconds += 1

        if seconds % 10 == 0:
            logger.info(f"Still waiting... ({seconds}s elapsed)")

    logger.error(f"Download timeout after {timeout}s")
    return None


def clean_old_downloads():
    """Remove old downloads to avoid conflicts"""
    if DOWNLOAD_DIR.exists():
        for file in DOWNLOAD_DIR.glob("*.xlsx"):
            try:
                file.unlink()
                logger.info(f"Removed old file: {file.name}")
            except Exception as e:
                logger.warning(f"Could not remove {file.name}: {e}")


# =============================================================================
# MAIN SCRAPING FUNCTION
# =============================================================================

def download_sharepoint_file():
    """Main function to download file from SharePoint"""
    driver = None

    try:
        # Clean old downloads
        clean_old_downloads()

        # Setup driver
        driver = setup_chrome_driver()

        # Try direct download approach first - modify URL to trigger download
        logger.info("Attempting direct download approach...")
        download_url = SHAREPOINT_URL.replace("?rtime=", "?download=1&rtime=")

        logger.info(f"Navigating to SharePoint download URL...")
        driver.get(download_url)

        # Wait for download to initiate
        time.sleep(10)
        capture_screenshot(driver, "01_download_initiated")

        # Check if download started
        downloaded_file = wait_for_download(DOWNLOAD_DIR, timeout=60)

        if downloaded_file:
            # Rename file to target filename (only if not already named correctly)
            target_path = DOWNLOAD_DIR / TARGET_FILENAME

            if downloaded_file.name != TARGET_FILENAME:
                if target_path.exists():
                    target_path.unlink()
                downloaded_file.rename(target_path)
                logger.info(f"File renamed to: {TARGET_FILENAME}")
            else:
                logger.info(f"File already has correct name: {TARGET_FILENAME}")

            # Verify file exists and has content (use downloaded_file if not renamed)
            final_file = target_path if target_path.exists() else downloaded_file
            file_size = final_file.stat().st_size
            logger.info(f"Download successful! File size: {file_size:,} bytes")

            if file_size < 1000:
                raise Exception(f"Downloaded file seems too small ({file_size} bytes)")

            return True

        # If direct download failed, try the navigation approach
        logger.info("Direct download failed, trying navigation approach...")
        driver.get(SHAREPOINT_URL)
        time.sleep(5)
        capture_screenshot(driver, "02_initial_load")

        # Wait for and click "Fichier" button
        logger.info("Looking for 'Fichier' button...")
        wait = WebDriverWait(driver, 30)

        # Try multiple selectors for "Fichier" button
        fichier_button = None
        selectors = [
            (By.CSS_SELECTOR, "#FileMenuFlyoutLauncher > span"),
            (By.XPATH, "//*[@id='FileMenuFlyoutLauncher']/span"),
            (By.XPATH, "//span[contains(text(), 'Fichier')]"),
            (By.XPATH, "//button[contains(@id, 'FileMenu')]")
        ]

        for by, selector in selectors:
            try:
                fichier_button = wait.until(EC.element_to_be_clickable((by, selector)))
                logger.info(f"Found 'Fichier' button using: {selector}")
                break
            except TimeoutException:
                logger.warning(f"Selector failed: {selector}")
                continue

        if not fichier_button:
            raise Exception("Could not find 'Fichier' button with any selector")

        fichier_button.click()
        logger.info("Clicked 'Fichier' button")
        time.sleep(3)
        capture_screenshot(driver, "02_fichier_menu_opened")

        # Look for download option - try multiple approaches
        logger.info("Looking for download option...")

        # Approach 1: Direct download link
        download_selectors = [
            (By.XPATH, "//span[contains(text(), 'Télécharger')]"),
            (By.XPATH, "//button[contains(text(), 'Télécharger')]"),
            (By.XPATH, "//div[contains(text(), 'Télécharger')]"),
            (By.CSS_SELECTOR, "span.fui-MenuItem__content:contains('Télécharger')")
        ]

        download_clicked = False
        for by, selector in download_selectors:
            try:
                download_button = wait.until(EC.element_to_be_clickable((by, selector)))
                download_button.click()
                logger.info(f"Clicked download option using: {selector}")
                download_clicked = True
                break
            except:
                continue

        if not download_clicked:
            logger.warning("Direct download not found, trying submenu approach...")

            # Approach 2: Navigate through "Créer une copie" or similar submenu
            try:
                submenu = driver.find_element(By.XPATH, "//span[contains(text(), 'Créer une copie') or contains(text(), 'Enregistrer une copie')]")
                submenu.click()
                logger.info("Opened submenu")
                time.sleep(2)
                capture_screenshot(driver, "03_submenu_opened")

                # Now try to click download
                download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Télécharger')]")))
                download_button.click()
                logger.info("Clicked download from submenu")
            except Exception as e:
                logger.error(f"Submenu approach failed: {e}")
                capture_screenshot(driver, "04_download_error")
                raise

        time.sleep(3)
        capture_screenshot(driver, "05_download_initiated")

        # Wait for download to complete
        downloaded_file = wait_for_download(DOWNLOAD_DIR, timeout=120)

        if not downloaded_file:
            raise Exception("Download did not complete within timeout")

        # Rename file to target filename
        target_path = DOWNLOAD_DIR / TARGET_FILENAME
        if target_path.exists():
            target_path.unlink()

        downloaded_file.rename(target_path)
        logger.info(f"File renamed to: {TARGET_FILENAME}")

        # Verify file exists and has content
        file_size = target_path.stat().st_size
        logger.info(f"Download successful! File size: {file_size:,} bytes")

        if file_size < 1000:
            raise Exception(f"Downloaded file seems too small ({file_size} bytes)")

        return True

    except Exception as e:
        logger.error(f"Error during download: {e}")
        if driver:
            capture_screenshot(driver, "error_final")
        raise

    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("SHAREPOINT XLSX SCRAPER - STARTING")
    logger.info("=" * 70)
    logger.info(f"Target URL: {SHAREPOINT_URL}")
    logger.info(f"Download directory: {DOWNLOAD_DIR.absolute()}")
    logger.info(f"Target filename: {TARGET_FILENAME}")
    logger.info(f"Headless mode: {HEADLESS}")
    logger.info("=" * 70)

    try:
        success = download_sharepoint_file()

        if success:
            logger.info("=" * 70)
            logger.info("✅ SCRAPER COMPLETED SUCCESSFULLY")
            logger.info("=" * 70)
            sys.exit(0)
        else:
            logger.error("=" * 70)
            logger.error("❌ SCRAPER FAILED")
            logger.error("=" * 70)
            sys.exit(1)

    except Exception as e:
        logger.error("=" * 70)
        logger.error(f"❌ FATAL ERROR: {e}")
        logger.error("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)
