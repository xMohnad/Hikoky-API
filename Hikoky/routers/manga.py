from fastapi import APIRouter, Query
from ..dependencies import get_handler, fetch_data

from Hikoky.models import Manga

router = APIRouter(
    tags=["Manga"],
    responses={404: {"description": "Not found"}}
)

@router.get(
    "/manga", 
    # response_model=Manga,
    summary="Get Manga Page", 
    response_description="Manga page data for the specified source."
)
async def manga(
    manga_URL: str = Query(
        None, 
        title="Manga Page URL", 
        description="The URL for the manga page. Provide this URL to fetch the manga page data."
    )
):
    """
    Retrieve the manga page data for the specified source.

    Parameters:
    - manga_URL (str, optional): The URL for the manga page. This parameter is required to fetch the manga page data.

    Returns:
    - dict: A dictionary containing the success status, the source name, and the data from the manga page.
    """

    url, handler = await get_handler(manga_URL)
    result = await fetch_data(url)
    results = handler["manga_page"](result)

    return {'success': True, "source": handler["name"], "data": results}
