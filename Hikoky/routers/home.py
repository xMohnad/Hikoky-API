from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from ..dependencies import get_handler, fetch_data

router = APIRouter(
    tags=["Manga"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/home", 
    summary="Retrieve Home Page Data",
    response_description="Successful Response with Home Page Data",
    # description="Retrieve the home page data for a specified source or the next page. Either 'Source name' or 'Next page URL' must be provided."
)
async def home(
    source_or_next_page: str = Query(
        ..., 
        title="Source or Next Page URL", 
        description="Specify either the source name to get the initial home page data or the next page URL for pagination."
    )
):
    """
    Retrieve the home page data for a specified source or the next page.

    Args:
    - source_or_next_page (str): Either the name of the source to retrieve the initial home page data, or the URL of the next page to fetch more data.

    Returns:
    - dict: A dictionary with the success status, the source name, and the home page data.
    """
    url, handler = await get_handler(source_or_next_page)

    result = await fetch_data(url)
    results = handler["home_page"](result)
    return {'success': True, "source": handler["name"], "data": results}
