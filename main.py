# Import the main webdriver module to control the browser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# Import Keys to simulate keyboard actions like pressing the 'ENTER' key
from selenium.webdriver.common.keys import Keys
# Import By to specify how we want to locate elements on the page (e.g., by Name, XPath, CSS Selector)
from selenium.webdriver.common.by import By
# Import a specific exception to handle cases where an element we want to click is blocked or hidden
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Import the time module to pause the script, giving the browser time to load pages and elements
import time
import os

# --- CONSTANTS ---
SIMILAR_ACCOUNT = "chefsteps"    
USERNAME = "sumankumarmehta82@gmail.com"          
PASSWORD = "0iMlWJGUcr4uz5Ia"             

BASE_URL = "https://app.100daysofpython.dev/services/share-a-naan" 
LOGIN_URL = f"{BASE_URL}/login"


class InstaFollower:

    def __init__(self, headless=None):
        chrome_options = webdriver.ChromeOptions()
        
        # Check if headless mode is specified or running on Linux/Docker
        if headless or (headless is None and os.name != 'nt'):
            if os.path.exists("/usr/bin/chromium"):
                chrome_options.binary_location = "/usr/bin/chromium"
            elif os.path.exists("/usr/bin/chromium-browser"):
                chrome_options.binary_location = "/usr/bin/chromium-browser"

            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        else:
            chrome_options.add_experimental_option("detach", True)  

        service = None
        if os.name != 'nt':
            if os.path.exists("/usr/bin/chromedriver"):
                service = Service("/usr/bin/chromedriver")

        if service:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            self.driver = webdriver.Chrome(options=chrome_options)

        self.driver.set_page_load_timeout(60)
        self.driver.implicitly_wait(10)

    def login(self):
        self.driver.get(LOGIN_URL)
        time.sleep(3)

        decline = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Decline')]")
        if decline:
            decline[0].click()

        username = self.driver.find_element(By.NAME, "username")
        password = self.driver.find_element(By.NAME, "password")
        
        username.send_keys(USERNAME)
        password.send_keys(PASSWORD)
        
        time.sleep(1)
        password.send_keys(Keys.ENTER)
        time.sleep(4)

        save_info = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Not now')]")
        if save_info:
            save_info[0].click()
        time.sleep(1)

        notifications = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Not Now')]")
        if notifications:
            notifications[0].click()

    def find_followers(self, target_account=None):
        account = target_account.strip() if target_account else SIMILAR_ACCOUNT
        self.driver.get(f"{BASE_URL}/u/{account}/followers")
        time.sleep(3)

        # Wait explicitly for the followers modal to appear (up to 15s)
        modal = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".followers-scroll"))
        )
        time.sleep(1)
        
        # Scroll 5 times for efficient cloud execution
        for _ in range(5):
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
            time.sleep(1)

    def follow(self):
        all_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".followers-scroll button")
        followed_count = 0
        
        for button in all_buttons:
            try:
                button.click()
                followed_count += 1
                time.sleep(1)
            except ElementClickInterceptedException:
                cancel = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
                cancel.click()
        return followed_count

    def close(self):
        try:
            self.driver.quit()
        except Exception:
            pass


def run_bot(headless=True, target_account=None, log_callback=None):
    account = target_account.strip() if target_account else SIMILAR_ACCOUNT
    def log(msg):
        if log_callback:
            log_callback(msg)

    bot = None
    try:
        log("Initializing Chromium browser...")
        bot = InstaFollower(headless=headless)
        
        log("Logging into application...")
        bot.login()
        
        log(f"Fetching followers for '@{account}'...")
        bot.find_followers(target_account=account)
        
        log("Following users...")
        count = bot.follow()
        
        success_msg = f"Successfully completed! Followed {count} users on target account '@{account}'."
        log(success_msg)
        return True, success_msg
    except Exception as e:
        err_msg = f"Error during execution: {str(e)}"
        log(err_msg)
        return False, err_msg
    finally:
        if bot:
            bot.close()


if __name__ == "__main__":
    import sys

    # Accept target from command-line arg or prompt the user
    if len(sys.argv) > 1:
        target = sys.argv[1].strip().lstrip("@")
    else:
        target = input(f"Enter target account (default: {SIMILAR_ACCOUNT}): @").strip()
        if not target:
            target = SIMILAR_ACCOUNT

    print(f"\n🎯 Target account: @{target}\n")

    bot = InstaFollower()
    bot.login()
    bot.find_followers(target_account=target)
    bot.follow()