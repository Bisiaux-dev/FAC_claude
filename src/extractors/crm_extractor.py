#!/usr/bin/env python3
"""
CRM Data Extractor using Selenium
Extracts SVG charts from CRM web interface
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime, timedelta
from typing import List, Dict


class CRMExtractor:
    """Extract SVG data from CRM web interface"""

    def __init__(self, base_url: str, username: str, password: str,
                 http_auth_user: str = None, http_auth_password: str = None):
        """
        Initialize CRM extractor

        Args:
            base_url: CRM base URL
            username: CRM username
            password: CRM password
            http_auth_user: HTTP auth username (optional)
            http_auth_password: HTTP auth password (optional)
        """
        self.base_url = base_url
        self.username = username
        self.password = password
        self.http_auth_user = http_auth_user
        self.http_auth_password = http_auth_password
        self.driver = None

    def setup_driver(self, download_dir: str, headless: bool = True):
        """
        Setup Chrome WebDriver

        Args:
            download_dir: Directory for downloads
            headless: Run in headless mode
        """
        chrome_options = Options()

        # Download preferences
        abs_download_dir = os.path.abspath(download_dir)
        prefs = {
            'download.default_directory': abs_download_dir,
            'download.prompt_for_download': False,
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False
        }
        chrome_options.add_experimental_option('prefs', prefs)

        # Chrome arguments
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        if headless:
            chrome_options.add_argument('--headless=new')

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(3)

    def login(self):
        """Login to CRM"""
        # Build URL with HTTP auth if provided
        if self.http_auth_user and self.http_auth_password:
            url = f"https://{self.http_auth_user}:{self.http_auth_password}@{self.base_url}"
        else:
            url = f"https://{self.base_url}"

        self.driver.get(url)

        # Wait for login form
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "inputEmail"))
        )

        # Enter credentials
        self.driver.find_element(By.ID, "inputEmail").send_keys(self.username)
        self.driver.find_element(By.ID, "inputPassword").send_keys(self.password)
        self.driver.find_element(By.XPATH, "//a[contains(text(),'Login')]").click()

        # Wait for successful login
        WebDriverWait(self.driver, 5).until(
            lambda d: "index.php" in d.current_url
        )

        # Close notifications
        try:
            self.driver.find_element(By.ID, "close_all_notif").click()
        except:
            pass

        print("✅ Login successful")

    def navigate_to_stats(self, stats_type: str = "CF"):
        """
        Navigate to statistics page

        Args:
            stats_type: Type of stats (CF or CIP)
        """
        # Click Statistics menu
        stats_menu = self.driver.find_element(By.XPATH, "//a[@data-bs-target='#collapseStatistique']")
        stats_menu.click()
        time.sleep(0.5)

        # Click specific stats page
        stats_link = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@data-title='Stats {stats_type}']"))
        )
        stats_link.click()
        time.sleep(0.5)

        # Switch to iframe if exists
        try:
            if stats_type == "CF":
                iframe_xpath = "//iframe[contains(@src,'stats_cf.php')]"
            else:
                iframe_xpath = "//iframe[contains(@src,'stats_entretiens.php')]"

            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, iframe_xpath))
            )
            iframe = self.driver.find_element(By.XPATH, iframe_xpath)
            self.driver.switch_to.frame(iframe)
        except:
            pass

        # Scroll to top
        self.driver.execute_script("window.scrollTo(0, 0);")

        print(f"✅ Navigated to Stats {stats_type}")

    def configure_form(self, button_index: int, date_debut: str, date_fin: str = ""):
        """
        Configure search form

        Args:
            button_index: Button index to select
            date_debut: Start date (YYYY-MM-DD)
            date_fin: End date (YYYY-MM-DD, optional)
        """
        # Click on date fields to activate them
        self.driver.find_element(By.ID, "date_1").click()
        time.sleep(0.1)

        if date_fin:
            self.driver.find_element(By.ID, "date_2").click()
            time.sleep(0.1)

        # Configure via JavaScript
        js_script = f"""
        var buttonSelect = document.getElementById('button_index');
        var dateInput1 = document.getElementById('date_1');
        var dateInput2 = document.getElementById('date_2');

        if (buttonSelect) {{
            buttonSelect.focus();
            buttonSelect.value = '{button_index}';
            buttonSelect.dispatchEvent(new Event('change', {{ bubbles: true }}));
            buttonSelect.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }}

        if (dateInput1) {{
            dateInput1.focus();
            dateInput1.value = '{date_debut}';
            dateInput1.dispatchEvent(new Event('change', {{ bubbles: true }}));
            dateInput1.dispatchEvent(new Event('input', {{ bubbles: true }}));
            dateInput1.checkValidity();
        }}

        if (dateInput2 && '{date_fin}' !== '') {{
            dateInput2.focus();
            dateInput2.value = '{date_fin}';
            dateInput2.dispatchEvent(new Event('change', {{ bubbles: true }}));
            dateInput2.dispatchEvent(new Event('input', {{ bubbles: true }}));
            dateInput2.checkValidity();
        }}
        """

        self.driver.execute_script(js_script)
        time.sleep(0.3)

    def extract_svg(self, filename: str, button_index: int = 0):
        """
        Extract SVG from page

        Args:
            filename: Output filename
            button_index: Button index for matching
        """
        # Click search button
        self.driver.find_element(By.ID, "envoyer").click()
        time.sleep(1.5)

        # Clean menus
        self.driver.execute_script("""
        document.querySelectorAll('.highcharts-contextmenu, .highcharts-menu').forEach(function(menu) {
            if (menu && menu.style) {
                menu.style.display = 'none';
                menu.style.visibility = 'hidden';
            }
        });
        document.body.click();
        """)

        # Find SVG elements
        svg_elements = self.driver.find_elements(By.XPATH, "//*[name()='svg' and contains(@class,'highcharts-root')]")

        print(f"🔍 Found {len(svg_elements)} SVG elements")

        if svg_elements:
            # Extract target SVG based on button_index
            if button_index < len(svg_elements):
                svg_element = svg_elements[button_index]
            else:
                svg_element = svg_elements[0]

            svg_content = self.driver.execute_script(
                "return new XMLSerializer().serializeToString(arguments[0]);",
                svg_element
            )

            return svg_content
        else:
            print("❌ No SVG elements found")
            return None

    def save_svg(self, svg_content: str, output_path: str):
        """
        Save SVG content to file

        Args:
            svg_content: SVG content
            output_path: Output file path
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        print(f"✅ SVG saved: {os.path.basename(output_path)}")

    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            print("✅ Browser closed")


if __name__ == "__main__":
    print("CRM Extractor module loaded successfully")
