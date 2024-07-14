from fastapi import HTTPException
import httpx
from bs4 import BeautifulSoup
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
import logging
import random
import asyncio
from typing import Union


def parse_html(content: Union[str, httpx.Response]) -> BeautifulSoup:
    return BeautifulSoup(
        content.text if hasattr(content, "text") else content, "html.parser"
    )


def handle_errors(response, http_err):
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
    url,
    method="GET",
    headers={},
    params=None,
    data=None,
    max_retries=3,
    delay=1,
    timeout=10,
):
    """Make a request to the specified URL using httpx async client."""
    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            headers = headers or {}
            headers["'User-Agent'"] = UserAgent().random
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
                    return parse_html(response)
                else:
                    return response.text

            except HTTPStatusError as http_err:
                error_message = handle_errors(response, http_err)

            except ConnectError:
                error_message = (
                    "Connection error. Please check your internet connection."
                )
                logging.error(
                    f"Attempt {attempt + 1}/{max_retries} for {url}: {error_message}"
                )

            except NetworkError:
                error_message = (
                    "A network error occurred. Please check your network settings."
                )
                logging.error(
                    f"Attempt {attempt + 1}/{max_retries} for {url}: {error_message}"
                )

            except TimeoutException:
                error_message = "The request timed out. Please try again later."
                logging.error(
                    f"Attempt {attempt + 1}/{max_retries} for {url}: {error_message}"
                )

            except TooManyRedirects:
                error_message = (
                    "Too many redirects. Please check the URL or try again later."
                )
                logging.error(
                    f"Attempt {attempt + 1}/{max_retries} for {url}: {error_message}"
                )

            except RequestError as req_err:
                error_message = f"An error occurred: {req_err}"
                logging.error(
                    f"Attempt {attempt + 1}/{max_retries} for {url}: {error_message}"
                )

            except InvalidURL:
                error_message = (
                    "The URL provided is invalid. Please check the URL format."
                )
                logging.error(
                    f"Attempt {attempt + 1}/{max_retries} for {url}: {error_message}"
                )

            except Exception as err:
                error_message = f"An unexpected error occurred: {err}"
                logging.error(
                    f"Attempt {attempt + 1}/{max_retries} for {url}: {error_message}"
                )

            if attempt < max_retries - 1:
                sleep_time = delay + random.uniform(0, 2)
                logging.info(f"Retrying after {sleep_time:.2f} seconds for {url}...")
                await asyncio.sleep(sleep_time)

        raise HTTPException(
            status_code=400, detail={"success": False, "error": error_message}
        )
