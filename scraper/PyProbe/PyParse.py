from fastapi import HTTPException
import httpx
from fake_useragent import UserAgent
from httpx import (
    HTTPStatusError,
    RequestError,
    ConnectError,
    TimeoutException,
    NetworkError,
    InvalidURL,
    TooManyRedirects,
)
from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser
from typing import Union, Optional, Dict, Any
import logging
import random
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def parse_html(
    content: Union[str, httpx.Response], parser: str
) -> Union[BeautifulSoup, HTMLParser]:
    """
    Parses HTML content using the specified parser.

    Parameters:
    - content: HTML content as a string or httpx.Response object.
    - parser: Type of parser to use ("soup", "selectolax").

    Returns:
    - Parsed HTML content based on the specified parser.

    Raises:
    - ValueError: If the content type is unsupported or if the parser is invalid.
    """
    if hasattr(content, "text"):
        html_content = content.text
    elif isinstance(content, str):
        html_content = content
    else:
        raise ValueError(
            "Unsupported content type. Must be a string or httpx.Response."
        )

    if parser == "soup":
        return BeautifulSoup(html_content, "lxml")
    elif parser == "selectolax":
        return HTMLParser(html_content)
    else:
        raise ValueError("Unsupported parser type. Use 'soup' or 'selectolax'.")


def handle_errors(response: httpx.Response, http_err: HTTPStatusError) -> str:
    """Handle HTTP errors based on the response status code."""
    error_message = ""
    if response.status_code == 403:
        error_message = "The site is protected by Cloudflare or other restrictions. Please try again later."
    elif response.status_code == 404:
        error_message = "The page was not found. Please check the URL."
    else:
        error_message = (
            f"HTTP error occurred: {http_err} (Status code: {response.status_code})"
        )
    logging.error(error_message)
    return error_message


async def pyparse(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    max_retries: int = 3,
    delay: int = 1,
    timeout: int = 10,
    parser: str = "soup",
    proxy: Optional[str] = None,
) -> Union[BeautifulSoup, HTMLParser, httpx.Response, str]:
    """
    Makes a request to the specified URL using httpx async client and parses the response.

    Parameters:
    - url (str): The URL to request.
    - method (str): The HTTP method to use (default is "GET").
    - headers (Optional[Dict[str, str]]): Optional headers to include in the request.
    - params (Optional[Dict[str, str]]): Optional query parameters to include in the request.
    - data (Optional[Dict[str, Any]]): Optional data to include in the request (for POST requests).
    - max_retries (int): Maximum number of retries if the request fails (default is 3).
    - delay (int): Delay between retries in seconds (default is 1).
    - timeout (int): Timeout for the request in seconds (default is 10).
    - parser (str): Type of parser to use for HTML content ("soup" or "selectolax").
    - proxy (Optional[str]): Proxy URL to use for the requests.

    Returns:
    - Parsed content if the response is HTML.
    - JSON response if the content type is application/json.
    - Raw response if the content type is neither HTML nor JSON.

    Raises:
    - HTTPException: If the maximum number of retries is reached or if an error occurs.
    """
    async with httpx.AsyncClient(proxies=proxy) as client:
        for attempt in range(max_retries):
            headers = headers or {}
            headers["User-Agent"] = UserAgent().random
            try:
                response = await client.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    data=data,
                    timeout=timeout,
                )
                response.raise_for_status()

                content_type = response.headers.get("Content-Type", "").lower()
                if "application/json" in content_type:
                    return response.json()
                elif "text/html" in content_type:
                    return parse_html(response, parser)
                else:
                    return response

            except HTTPStatusError as http_err:
                if response.status_code in {403, 404}:
                    error_message = handle_errors(response, http_err)
                    logging.error(
                        f"Error {response.status_code} is not retryable: {error_message}"
                    )
                    break
                else:
                    error_message = handle_errors(response, http_err)

            except InvalidURL:
                error_message = (
                    "The URL provided is invalid. Please check the URL format."
                )
                logging.error(error_message)
                break

            except TooManyRedirects:
                error_message = (
                    "Too many redirects. Please check the URL or try again later."
                )
                logging.error(error_message)
                break

            except (ConnectError, NetworkError, TimeoutException) as temp_err:
                error_message = str(temp_err)
                logging.error(
                    f"Attempt {attempt + 1}/{max_retries} for {url}: {error_message}"
                )
                if attempt < max_retries - 1:
                    sleep_time = delay * (2**attempt) + random.uniform(0, 2)
                    logging.info(
                        f"Retrying after {sleep_time:.2f} seconds for {url}..."
                    )
                    await asyncio.sleep(sleep_time)
                    continue

            except RequestError as req_err:
                error_message = f"An error occurred: {req_err}"
                logging.error(
                    f"Attempt {attempt + 1}/{max_retries} for {url}: {error_message}"
                )

            except Exception as err:
                error_message = f"An unexpected error occurred: {err}"
                logging.error(
                    f"Attempt {attempt + 1}/{max_retries} for {url}: {error_message}"
                )

            break

        raise HTTPException(
            status_code=400, detail={"success": False, "error": error_message}
        )
