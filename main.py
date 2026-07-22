# Import the main webdriver module to control the browser
from selenium import webdriver
# Import Keys to simulate keyboard actions like pressing the 'ENTER' key
from selenium.webdriver.common.keys import Keys
# Import By to specify how we want to locate elements on the page (e.g., by Name, XPath, CSS Selector)
from selenium.webdriver.common.by import By
# Import a specific exception to handle cases where an element we want to click is blocked or hidden
from selenium.common.exceptions import ElementClickInterceptedException
# Import the time module to pause the script, giving the browser time to load pages and elements
import time
import os

# --- CONSTANTS ---
# The target account name whose followers we want to automatically follow
SIMILAR_ACCOUNT = "chefsteps"    
# Your login username (email) for the web application
USERNAME = "sumankumarmehta82@gmail.com"          
# Your login password for the web application
PASSWORD = "0iMlWJGUcr4uz5Ia"             

# The main URL of the application we are automating
BASE_URL = "https://app.100daysofpython.dev/services/share-a-naan" 
# The specific URL used for logging into the application
LOGIN_URL = f"{BASE_URL}/login"


# Define a class to encapsulate all the logic for our bot
class InstaFollower:

    # The __init__ method is called automatically when we create a new instance of the bot
    def __init__(self, headless=None):
        # Create an object to configure the Chrome browser's settings
        chrome_options = webdriver.ChromeOptions()
        
        # Check if headless mode is specified or running on Linux/Docker
        if headless or (headless is None and os.name != 'nt'):
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        else:
            # Add a special option to keep the browser open even after the script finishes executing
            chrome_options.add_experimental_option("detach", True)  

        # Initialize the Chrome webdriver with the options we just configured
        self.driver = webdriver.Chrome(options=chrome_options)

    # Method to handle the login process
    def login(self):
        # Tell the browser to navigate to the login URL
        self.driver.get(LOGIN_URL)
        # Pause the script for 2 seconds to allow the page to fully load
        time.sleep(2)

        # Look for any buttons on the page containing the text 'Decline' (usually a cookie consent banner)
        decline = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Decline')]")
        # If the list is not empty (meaning the button was found)...
        if decline:
            # ...click the first 'Decline' button
            decline[0].click()

        # Find the input field where the username goes by looking for the HTML attribute name="username"
        username = self.driver.find_element(By.NAME, "username")
        # Find the input field where the password goes by looking for the HTML attribute name="password"
        password = self.driver.find_element(By.NAME, "password")
        
        # Type the USERNAME string into the username input field
        username.send_keys(USERNAME)
        # Type the PASSWORD string into the password input field
        password.send_keys(PASSWORD)
        
        # Pause for 1 second to mimic human typing behavior
        time.sleep(1)
        # Simulate pressing the 'ENTER' key on the keyboard while focused on the password field
        password.send_keys(Keys.ENTER)
        # Pause for 2 seconds to allow the dashboard/homepage to load after logging in
        time.sleep(2)

        # Look for a popup dialog asking to save login info by searching for the text 'Not now'
        save_info = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Not now')]")
        if save_info:
            save_info[0].click()
        time.sleep(1)

        # Look for a notification permission prompt by searching for a button containing 'Not Now'
        notifications = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Not Now')]")
        if notifications:
            notifications[0].click()

    # Method to navigate to the target profile and load their followers
    def find_followers(self):
        # Tell the browser to navigate directly to the followers page of the target account
        self.driver.get(f"{BASE_URL}/u/{SIMILAR_ACCOUNT}/followers")
        # Pause for 2 seconds to let the followers modal/list load
        time.sleep(2)

        # Find the specific HTML element that contains the scrollable list of followers
        modal = self.driver.find_element(By.CSS_SELECTOR, ".followers-scroll")
        
        # Loop 10 times to scroll down the list and load more followers into the page
        for _ in range(10):
            # Execute JavaScript directly in the browser to scroll the 'modal' element down
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
            # Pause for 1 second after each scroll
            time.sleep(1)

    # Method to click the "Follow" buttons on the loaded list
    def follow(self):
        # Find all button elements that are inside the scrollable followers list
        all_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".followers-scroll button")
        followed_count = 0
        
        # Iterate through every button found in that list
        for button in all_buttons:
            try:
                # Click the "Follow" button
                button.click()
                followed_count += 1
                # Pause for 1 second to avoid clicking too fast
                time.sleep(1)
            except ElementClickInterceptedException:
                # Find the 'Cancel' button on confirmation popup
                cancel = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
                cancel.click()
        return followed_count

    def close(self):
        try:
            self.driver.quit()
        except Exception:
            pass


def run_bot(headless=True):
    bot = None
    try:
        bot = InstaFollower(headless=headless)
        bot.login()
        bot.find_followers()
        count = bot.follow()
        return True, f"Successfully executed bot. Target account: '{SIMILAR_ACCOUNT}'. Followed users: {count}"
    except Exception as e:
        return False, f"Error executing bot: {str(e)}"
    finally:
        if bot:
            bot.close()


# --- EXECUTION ---
if __name__ == "__main__":
    bot = InstaFollower()
    bot.login()
    bot.find_followers()
    bot.follow()