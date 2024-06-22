# hikoky-API/Hikoky/routers/home.py

from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from ..dependencies import get_handler, fetch_data

router = APIRouter(
    tags=["Manga"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/home", 
    summary="", 
    response_description="",
    description="Retrieve the home page data for a specified source or the next page. Either 'Source name' or 'Next page URl' must be provided."
)

async def home(
    manga_URl: str = Query(Header="", title="Manga page URL", description="URL for the manga page."),
    url: Dict[str], handler: Dict[str] = Depends(get_handler)
):
    result = await fetch_data(url)
    results = handler["home_page"](result)
    return {'success': True, "source": handler["name"], "data": results}
3