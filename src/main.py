from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.exception import AppwriteException
import os
import json
import sys
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()

def perform_google_search(query):
    try:
        # Set up headless Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--proxy-server='direct://'")
        chrome_options.add_argument("--proxy-bypass-list=*")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-dev-tools")
        chrome_options.add_argument("--log-level=3")

        # Initialize WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        # Navigate to Google
        driver.get("https://www.google.com")

        # Locate the search box, enter query, and submit
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.submit()

        # Wait for results to load
        driver.implicitly_wait(5)

        # Extract the title of the first result
        first_result = driver.find_element(By.CSS_SELECTOR, "h3")
        result_title = first_result.text

        # Close the browser
        driver.quit()

        return {
            "status": "success",
            "search_query": query,
            "first_result_title": result_title
        }

    except Exception as e:
        logger.error(f"Selenium Error: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

# This Appwrite function will be executed every time your function is triggered
def main(context):
    # Initialize Appwrite Client
    client = (
        Client()
        .set_endpoint(os.environ.get("APPWRITE_FUNCTION_API_ENDPOINT", "http://localhost/v1"))
        .set_project(os.environ.get("APPWRITE_FUNCTION_PROJECT_ID", "project_id"))
        .set_key(os.environ.get("APPWRITE_FUNCTION_API_KEY", "api_key"))
    )
    users = Users(client)

    try:
        response = users.list()
        # Log messages to the Appwrite Console
        context.log("Total users: " + str(response["total"]))
    except AppwriteException as err:
        context.error("Could not list users: " + repr(err))

    # The req object contains the request data
    if context.req.path == "/ping":
        # Respond with "Pong" for ping requests
        return context.res.text("Pong")

    elif context.req.path == "/search":
        # Handle search requests
        try:
            # Extract search query from request body or query parameters
            if context.req.method == "POST":
                body = context.req.json
                search_query = body.get("query", "Appwrite integration with Selenium")
            else:
                search_query = context.req.get("query", "Appwrite integration with Selenium")

            # Perform Google search using Selenium
            search_result = perform_google_search(search_query)

            if search_result["status"] == "success":
                return context.res.json(search_result)
            else:
                return context.res.json(search_result, status=500)

        except Exception as e:
            context.error("Search Error: " + str(e))
            return context.res.json({"status": "error", "message": str(e)}, status=500)

    else:
        # Default response for other paths
        return context.res.json(
            {
                "motto": "Build like a team of hundreds.",
                "learn": "https://appwrite.io/docs",
                "connect": "https://appwrite.io/discord",
                "getInspired": "https://builtwith.appwrite.io",
            }
        )
