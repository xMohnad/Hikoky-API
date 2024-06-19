import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
import time
import logging
import random
import re

def parse_content(content):
    """Parse content with BeautifulSoup, handling both raw HTML and HTTP response objects."""
    return BeautifulSoup(content.content if hasattr(content, 'content') else content, "html.parser")

def get_random_headers():
    """Generate random headers for the request."""
    return {'User-Agent': UserAgent().random}

def handle_errors(response, http_err):
    """Handle HTTP errors based on the response status code."""
    error_message = ""
    if response.status_code == 403:
        error_message = "The site is protected by Cloudflare or other restrictions. Please try again later."
    elif response.status_code == 404:
        error_message = "The page was not found. Please check the URL."
    else:
        error_message = f"HTTP error occurred: {http_err} (Status code: {response.status_code})"
    logging.error(error_message)
    return error_message

def check_for_captcha(soup):
    """Check if the parsed content contains indications of a CAPTCHA."""
    captcha_elements = [
        {"tag": "div", "class": "g-recaptcha"},
        {"tag": "div", "class": "h-captcha"},
        {"tag": "input", "type": "hidden", "name": "captcha"}
    ]
    
    for element in captcha_elements:
        if soup.find(element["tag"], {key: element[key] for key in element if key != "tag"}):
            return True
            
    captcha_keywords = re.compile(r'captcha|recaptcha|g-recaptcha|hcaptcha', re.IGNORECASE)
    if soup.find(text=captcha_keywords):
        return True

    return False

def pyparse(url, max_retries=3, delay=1, timeout=7):
    """Make a request to the specified URL using cookies."""
    session = requests.Session()
    
    for attempt in range(max_retries):
        try:
            headers = get_random_headers()
            response = session.get(url, headers=headers, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            soup = parse_content(response)
            
            # if check_for_captcha(soup):
#                 return {"error": f"The site contains a CAPTCHA at {url}."}
#             
            return soup
            
        except HTTPError as http_err:
            error_message = handle_errors(response, http_err)
            
        except ConnectionError:
            error_message = "Connection error. Please check your internet connection."
            logging.error(f"Attempt {attempt + 1}/{max_retries} for {url}: {error_message}")
        
        except Timeout:
            error_message = "The request timed out. Please try again later."
            logging.error(f"Attempt {attempt + 1}/{max_retries} for {url}: {error_message}")
        
        except RequestException as req_err:
            error_message = f"An error occurred: {req_err}"
            logging.error(f"Attempt {attempt + 1}/{max_retries} for {url}: {error_message}")
        
        except Exception as err:
            error_message = f"An unexpected error occurred: {err}"
            logging.error(f"Attempt {attempt + 1}/{max_retries} for {url}: {error_message}")
        
        if attempt < max_retries - 1:
            sleep_time = delay + random.uniform(0, 2)
            logging.info(f"Retrying after {sleep_time:.2f} seconds for {url}...")
            time.sleep(sleep_time)
    
    return {"error": error_message}
