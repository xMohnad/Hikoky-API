from fastapi import APIRouter, Query, HTTPException
from ..dependencies.V1 import handle_manchap

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
    )
):
    """
    Retrieve the manga page data for the specified source.

    Parameters:
    - mangaURL (str): The URL for the manga page. This parameter is required to fetch the manga page data.

    Returns:
    - dict: A dictionary containing the success status, the source name, and the data from the manga page.
    """

    try:
        return await handle_manchap(mangaURL)
    except HTTPException as e:
        raise e
