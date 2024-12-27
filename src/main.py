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
    driver = None
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

        # Extract the title of the first result
        first_result = driver.find_element(By.CSS_SELECTOR, "h3")
        result_title = first_result.text

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

    finally:
        if driver:
            driver.quit()

# Main function
def main(context):
    # Initialize Appwrite Client
    client = (
        Client()
        .set_endpoint(os.environ.get("APPWRITE_FUNCTION_API_ENDPOINT", "http://localhost/v1"))
        .set_project(os.environ.get("APPWRITE_FUNCTION_PROJECT_ID", "project_id"))
        .set_key(os.environ.get("APPWRITE_FUNCTION_API_KEY", "api_key"))
    )
    users = Users(client)

    # Log total users (optional)
    try:
        response = users.list()
        context.log("Total users: " + str(response["total"]))
    except AppwriteException as err:
        context.error("Could not list users: " + repr(err))

    # Handle request
    try:
        path = context.req.path
        method = context.req.method

        if path == "/ping":
            # Respond to ping requests
            return context.res.text("Pong")

        elif path == "/search":
            # Handle search requests
            body = json.loads(context.req.body)  # FIXED JSON Parsing
            search_query = body.get("query", "Appwrite integration with Selenium")

            # Perform Google search
            search_result = perform_google_search(search_query)

            if search_result["status"] == "success":
                return context.res.json(search_result, code=200)  # FIXED Response Code
            else:
                return context.res.json(search_result, code=500)

        else:
            # Default response
            return context.res.json(
                {
                    "motto": "Build like a team of hundreds.",
                    "learn": "https://appwrite.io/docs",
                    "connect": "https://appwrite.io/discord",
                    "getInspired": "https://builtwith.appwrite.io",
                },
                code=200
            )

    except Exception as e:
        context.error("Search Error: " + str(e))
        return context.res.json({"status": "error", "message": str(e)}, code=500)  # FIXED Response Code
