from fastapi import APIRouter, Query

from Hikoky.dependencies import get_module_by_url
from scraper import pyparse


router = APIRouter(tags=["Manga"], responses={404: {"description": "Not found"}})


@router.get(
    "/manga",
    # response_model=Manga,
    summary="Get Manga Page",
    response_description="Manga page data for the specified source.",
)
async def manga(
    mangaURL: str = Query(
        ...,
        title="Manga Page URL",
        description="The URL for the manga page. Provide this URL to fetch the manga page data.",
        example="https://3asq.org/manga/jujutsu-kaisen/",
    )
):
    """
    Retrieve the manga page data for the specified source.

    Parameters:
    - mangaURL (str): The URL for the manga page. This parameter is required to fetch the manga page data.

    Returns:
    - dict: A dictionary containing the success status, the source name, and the data from the manga page.
    """

    source = await get_module_by_url(mangaURL)
    result = await pyparse(mangaURL)
    results = await source.manga(result)

    return {"success": True, "data": results}
