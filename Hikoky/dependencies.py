# hikoky-API/Hikoky/dependencies.py

from config import source_handlers, search_handlers
from typing import Dict, Any, Union
from fastapi import HTTPException
from scraper import pyparse, HttpClientError
from urllib.parse import urlparse
from bs4 import BeautifulSoup

async def get_handler(header_value: str):
    parsed_source_netloc = urlparse(header_value).netloc

    for handler in source_handlers:
        if parsed_source_netloc == urlparse(handler["base_url"]).netloc:
            return header_value, handler
        elif header_value == handler["name"]:
            return handler["base_url"], handler

    raise HTTPException(status_code=400, detail="Either a valid source name or a valid nextPageUrl must be provided.")

async def fetch_data(url: str, method="GET", headers=None, params=None, data=None):

    try:

        result = await pyparse(url, method, headers=headers, params=params, data=data)
        return result

    except HttpClientError as e:
        raise HTTPException(status_code=400, detail=f"Errort: {e.message}")




async def handle_search(keyword: str, source: str) -> Union[Dict[str, Any], BeautifulSoup, str]:
    for handler in search_handlers:
        if source == handler["name"]:

            url = handler["search_URL"]
            method = handler["method"]
            headers = handler["headers"]
            params = handler.get("params")(keyword) if handler.get("params") else None
            data = handler.get("data")(keyword) if handler.get("data") else None
            name =  handler["name"]

            try:

                result = await pyparse(url, method, headers, params, data)

                return await handler["search"](result, name)

            except HttpClientError as e:
                raise HTTPException(status_code=400, detail=f"Errort: {e.message}")

    raise HTTPException(status_code=400, detail=f"Invalid source, No source is not found: {source}")

