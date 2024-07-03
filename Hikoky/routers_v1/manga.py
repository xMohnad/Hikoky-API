from fastapi import APIRouter, Query, HTTPException
from ..dependencies import get_handler, fetch_data

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
    mangaURL: str = Query(
        ..., 
        title="Manga Page URL", 
        description="The URL for the manga page. Provide this URL to fetch the manga page data."
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
        url, handler = await get_handler(mangaURL)
        result = await fetch_data(url)
        results = handler["manga_page"](result)

        return {'success': True, "source": handler["name"], "data": results}

    except HTTPException as e:
        return {"success": False, **e.detail}

    except Exception as e:
        return {"success": False, "error": str(e)}
