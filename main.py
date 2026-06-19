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
    def __init__(self):
        # Create an object to configure the Chrome browser's settings
        chrome_options = webdriver.ChromeOptions()
        # Add a special option to keep the browser open even after the script finishes executing
        chrome_options.add_experimental_option("detach", True)  
        # Initialize the Chrome webdriver with the options we just configured, opening the browser window
        self.driver = webdriver.Chrome(options=chrome_options)

    # Method to handle the login process
    def login(self):
        # Tell the browser to navigate to the login URL
        self.driver.get(LOGIN_URL)
        # Pause the script for 2 seconds to allow the page to fully load
        time.sleep(2)

        # Look for any buttons on the page containing the text 'Decline' (usually a cookie consent banner)
        # We use find_elements (plural) so it returns an empty list instead of crashing if it's not found
        decline = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Decline')]")
        # If the list is not empty (meaning the button was found)...
        if decline:
            # ...click the first (and likely only) 'Decline' button in the list
            decline[0].click()

        # Find the input field where the username goes by looking for the HTML attribute name="username"
        username = self.driver.find_element(By.NAME, "username")
        # Find the input field where the password goes by looking for the HTML attribute name="password"
        password = self.driver.find_element(By.NAME, "password")
        
        # Type the USERNAME string into the username input field
        username.send_keys(USERNAME)
        # Type the PASSWORD string into the password input field
        password.send_keys(PASSWORD)
        
        # Pause for 1 second to mimic human typing behavior and ensure the fields register the input
        time.sleep(1)
        # Simulate pressing the 'ENTER' key on the keyboard while focused on the password field to submit the form
        password.send_keys(Keys.ENTER)
        # Pause for 2 seconds to allow the dashboard/homepage to load after logging in
        time.sleep(2)

        # Look for a popup dialog asking to save login info by searching for the text 'Not now'
        save_info = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Not now')]")
        # If the 'Not now' element exists...
        if save_info:
            # ...click it to dismiss the prompt
            save_info[0].click()
        # Pause for 1 second to let the popup close
        time.sleep(1)

        # Look for a notification permission prompt by searching for a button containing 'Not Now'
        notifications = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Not Now')]")
        # If the notification prompt exists...
        if notifications:
            # ...click it to dismiss it
            notifications[0].click()

    # Method to navigate to the target profile and load their followers
    def find_followers(self):
        # Tell the browser to navigate directly to the followers page of the target account
        self.driver.get(f"{BASE_URL}/u/{SIMILAR_ACCOUNT}/followers")
        # Pause for 2 seconds to let the followers modal/list load
        time.sleep(2)

        # Find the specific HTML element that contains the scrollable list of followers using its CSS class
        modal = self.driver.find_element(By.CSS_SELECTOR, ".followers-scroll")
        
        # Loop 10 times to scroll down the list and load more followers into the page
        for _ in range(10):
            # Execute JavaScript directly in the browser to scroll the 'modal' element down to its maximum height
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
            # Pause for 1 second after each scroll to allow the web app to fetch and load the next batch of users
            time.sleep(1)

    # Method to click the "Follow" buttons on the loaded list
    def follow(self):
        # Find all button elements that are inside the scrollable followers list
        all_buttons = self.driver.find_elements(By.CSS_SELECTOR, ".followers-scroll button")
        
        # Iterate through every button found in that list
        for button in all_buttons:
            # Try to execute the following block of code
            try:
                # Click the "Follow" button
                button.click()
                # Pause for 1 second to avoid clicking too fast (which can trigger spam blocks)
                time.sleep(1)
            # If clicking the button throws an ElementClickInterceptedException (usually because a popup blocked it)...
            except ElementClickInterceptedException:
                # ...this implies we clicked a button that said "Following", triggering an "Unfollow?" confirmation popup.
                # Find the 'Cancel' button on that new popup dialog
                cancel = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cancel')]")
                # Click 'Cancel' to close the popup and remain following the user
                cancel.click()


# --- EXECUTION ---
# Create a new instance of the bot
bot = InstaFollower()
# Call the login method to authenticate
bot.login()
# Call the method to load the followers of the target account
bot.find_followers()
# Call the method to iterate through the list and click follow
bot.follow()