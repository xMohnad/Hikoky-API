from difflib import get_close_matches
from fastapi import HTTPException
from scraper import pyparse

from bs4 import BeautifulSoup
from config import search_handlers

from typing import Dict, Any, Union, List
from .dependencies import err


async def fetch_search_results(handler, keyword):
    url = handler["search_URL"]
    method = handler["method"]
    headers = handler["headers"]
    params = handler.get("params")(keyword) if handler.get("params") else None
    data = handler.get("data")(keyword) if handler.get("data") else None
    name = handler["name"]

    result = await pyparse(url, method, headers, params, data)
    search_result = await handler["search"](result, name)
    return search_result


async def handle_search(
    keyword: str, source: str
) -> Union[Dict[str, Any], BeautifulSoup, str]:
    for handler in search_handlers:
        if source == handler["name"]:
            return await fetch_search_results(handler, keyword)

    similar_names = get_close_matches(
        source, [sources["name"] for sources in search_handlers]
    )

    if similar_names:
        raise HTTPException(
            status_code=404,
            detail={"error": f"Invalid source name. Did you mean: {similar_names[0]}"},
        )

    raise HTTPException(
        status_code=400,
        detail={**err, "error": f"Invalid source, No source found {source}"},
    )


async def handle_search_in_all_sources(
    keyword: str,
) -> List[Dict[str, Any]]:
    results = []

    for handler in search_handlers:
        try:
            search_result = await fetch_search_results(handler, keyword)
            results.append({"source": handler["name"], "data": search_result})

        except HTTPException as e:
            results.append(e.detail)

    if not results:
        raise HTTPException(status_code=404, detail=results)
    return results
