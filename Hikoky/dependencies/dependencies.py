# hikoky-API/Hikoky/dependencies/dependencies.py
from difflib import get_close_matches
from config import source_handlers

from fastapi import HTTPException
from scraper import pyparse

from urllib.parse import urlparse


err = {"success": False}


# uesd in any Version
async def fetch_data(url: str, method="GET", headers=None, params=None, data=None):

    result = await pyparse(
        url, method, headers=headers, max_retries=1, params=params, data=data
    )
    return result


async def get_handler_url(header_value: str):
    source_netloc = urlparse(header_value).netloc

    handler = next(
        (h for h in source_handlers if urlparse(h["base_url"]).netloc == source_netloc),
        None,
    )
    if not handler:
        raise HTTPException(
            status_code=404, detail={**err, "error": "A valid URL must be provided."}
        )

    return handler


async def get_handler_source(header_value: str):

    handler = next(
        (h for h in source_handlers if h["name"].lower() == header_value.lower()),
        None,
    )

    if not handler:
        similar_names = get_close_matches(
            header_value, [sources["name"] for sources in source_handlers]
        )
        if similar_names:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Either a valid source name. Did you mean: {similar_names[0]}"
                },
            )

        raise HTTPException(
            status_code=404,
            detail={**err, "error": "A valid source name must be provided."},
        )
    return handler


async def home_data(source: str):
    handler = await get_handler_source(source)
    result = await fetch_data(handler["base_url"])

    results = handler["home_page"](result, handler["name"])
    return {"success": True, "source": handler["name"], "data": results}


async def more_data_home(next_page_url: str):
    handler = await get_handler_url(next_page_url)
    result = await fetch_data(next_page_url)

    results = handler["home_page"](result, handler["name"])
    return {"success": True, "source": handler["name"], "data": results}
