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
# Set Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Explicitly set binary locations for Chromium and ChromeDriver
chrome_options.binary_location = "/usr/bin/chromium"
service = Service("/usr/bin/chromedriver")

# Initialize the driver
driver = webdriver.Chrome(service=service, options=chrome_options)

def perform_google_search(query):
    driver = None
    try:
        # Set up headless Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Perform Google Search
        driver.get("https://www.google.com")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(query)
        search_box.submit()

        # Extract the first result title
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

    

    # Handle Request
    try:
        path = context.req.path
        method = context.req.method

        if path == "/ping":
            # Respond to ping requests
            return context.res.text("Pong", 200)  # Added status code as positional argument

        elif path == "/search":
            if not context.req.body:
                raise ValueError("Empty request body")

            try:
                body = json.loads(context.req.body)  # Correct JSON parsing
            except json.JSONDecodeError as json_err:
                raise ValueError(f"Invalid JSON format: {str(json_err)}")

            search_query = body.get("query", "Appwrite integration with Selenium")

            # Perform Google search
            search_result = perform_google_search(search_query)

            if search_result["status"] == "success":
                return context.res.json(search_result, 200)  # Positional status code
            else:
                return context.res.json(search_result, 500)  # Positional status code

        else:
            # Default response
            return context.res.json(
                {
                    "motto": "Build like a team of hundreds.",
                    "learn": "https://appwrite.io/docs",
                    "connect": "https://appwrite.io/discord",
                    "getInspired": "https://builtwith.appwrite.io",
                },
                200  # Positional status code
            )

    except Exception as e:
        context.error("Search Error: " + str(e))
        return context.res.json({"status": "error", "message": str(e)}, 500)  # Positional status code
