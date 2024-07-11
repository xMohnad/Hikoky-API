from fastapi import APIRouter, Query

from Hikoky.dependencies import get_module_by_url
from scraper.PyProbe.PyParse import pyparse


router = APIRouter(tags=["Chapter"], responses={404: {"description": "Not found"}})


@router.get(
    "/chapter",
    # response_model=ChapterModel,
    summary="Get Chapter Page",
    response_description="Chapter page data for the specified source.",
)
async def chapter(
    chapterURL: str = Query(
        ...,
        title="Chapter Page URL",
        description="URL for the chapter page. Provide this URL to fetch the chapter page data.",
        example="https://3asq.org/manga/jujutsu-kaisen/256/",
    )
):
    """
    Retrieve the chapter page data for the specified source.

    Parameters:
    - chapterURL (str): The URL for the chapter page. This parameter is required to fetch the chapter page data.

    Returns:
    - dict: A dictionary containing:
        - success (bool): Indicates if the operation was successful.
        - source (str): The name of the source.
        - data (dict): The data fetched from the chapter page.
    """

    source = await get_module_by_url(chapterURL)
    result = await pyparse(chapterURL)
    results = await source.chapter(result, chapterURL)

    return {"success": True, "source": source.source, "data": results}
