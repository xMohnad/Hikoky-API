# hikoky-API/Hikoky/dependencies.py

from config import source_handlers
from typing import Tuple, Dict, Any
from fastapi import HTTPException, Header
from scraper import pyparse
from urllib.parse import urlparse

async def get_handler(header_value: str):
    parsed_source_netloc = urlparse(header_value).netloc

    for handler in source_handlers:
        if parsed_source_netloc == urlparse(handler["base_url"]).netloc:
            return header_value, handler
        elif header_value == handler["name"]:
            return handler["base_url"], handler

    raise HTTPException(status_code=400, detail="Either a valid source name or a valid nextPageUrl must be provided.")

async def fetch_data(url: str, method="GET", headers=None, params=None, data=None, parse=True):
    result = await pyparse(url, method, headers=headers, params=params, data=data, parse=parse)
    if isinstance(result, dict) and 'error' in result:
        raise HTTPException(status_code=400, detail=result.get('error'))
    return result

