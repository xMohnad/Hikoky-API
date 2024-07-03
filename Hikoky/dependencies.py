# hikoky-API/Hikoky/dependencies.py
from config import source_handlers, search_handlers
from typing import Dict, Any, Union, List

from fastapi import HTTPException
from scraper import pyparse, HttpClientError
from scraper import SearchError, SearchNotFoundError

from urllib.parse import urlparse
from bs4 import BeautifulSoup
import logging

# V1 handler 
async def get_handler(header_value: str):
    parsed_source_netloc = urlparse(header_value).netloc

    for handler in source_handlers:
        if parsed_source_netloc == urlparse(handler["base_url"]).netloc:
            return header_value, handler
        elif header_value.lower() == handler["name"].lower():
            return handler["base_url"], handler

    raise HTTPException(status_code=400, detail={"error": "Either a valid source name or a valid URl must be provided."})

# ============================================

# About search 
async def handle_search(keyword: str, source: str) -> Union[Dict[str, Any], BeautifulSoup, str]:
    for handler in search_handlers:
        if source == handler["name"]:
            url = handler["search_URL"]
            method = handler["method"]
            headers = handler["headers"]
            params = handler.get("params")(keyword) if handler.get("params") else None
            data = handler.get("data")(keyword) if handler.get("data") else None
            name = handler["name"]

            try:
                result = await pyparse(url, method, headers, params, data)
                search_result = await handler["search"](result, name)

                return search_result

            except SearchError as e:
                raise HTTPException(status_code=404, detail=e.detail)

            except HttpClientError as e:
                raise HTTPException(status_code=400, detail=f"Error: {e.message}")

    raise HTTPException(status_code=400, detail=f"Invalid source, No source found {source}")

async def handle_search_in_all_sources(keyword: str) -> List[Union[Dict[str, Any], BeautifulSoup, str]]:
    results = []

    for handler in search_handlers:
        url = handler["search_URL"]
        method = handler["method"]
        headers = handler["headers"]
        params = handler.get("params")(keyword) if handler.get("params") else None
        data = handler.get("data")(keyword) if handler.get("data") else None
        name = handler["name"]

        try:
            result = await pyparse(url, method, headers, params, data)
            search_result = await handler["search"](result, name)
            results.append(search_result)

        except SearchNotFoundError as e:
            results.append(e.detail)

        except SearchError as e:
            results.append(e.detail)

        except HttpClientError as e:
            error = {"Error": e.message}
            logging.error(f"Error searching in source {name}: {e.message}")
            results.append(error)

    if not results:
        raise HTTPException(status_code=404, detail={"Error": "No results found"})
    return results

# ==============================================================
# uesd in any Version
async def fetch_data(url: str, method="GET", headers=None, params=None, data=None):

    try:
        result = await pyparse(url, method, headers=headers, params=params, data=data)
        return result

    except HttpClientError as e:
        raise HTTPException(status_code=400, detail={"error": e.message})


# about V2
