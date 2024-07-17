from fastapi import APIRouter, Query
from ..dependencies import get_module_by_url


async def more_data_manga(next_page_url: str):
    source = await get_module_by_url(next_page_url)

    results = await source.manga(next_page_url)
    return {"success": True, "data": results}


router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/manga/next",
    tags=["Manga"],
    summary="Retrieve Next Page Data",
    response_description=(
        "### **Successful Response with Next Page Data**\n\n"
        "## Returns:\n"
        "- **success (bool)**: Indicates whether the data retrieval was successful.\n"
        "- **source (str)**: The name of the source.\n"
        "- **data (dict)**: The next page data retrieved from the source."
        "- **nextPageUrl (str))**: The URL of the next page to fetch more data."
    ),
    description=(
        "**Retrieve the data for the next page of a specified source.**\n\n"
        "This endpoint allows you to fetch the subsequent set of data from the next page URL provided by the source. It helps in paginating through the data provided by the source.\n\n"
        "### Features:\n"
        "- Fetch data from the next page URL.\n"
        "- Continues data retrieval from where the previous request left off.\n\n"
        "### Usage:\n"
        "- **nextPageUrl (str)**: The URL of the next page to fetch more data.\n\n"
        "### Examples:\n"
        "```\n"
        "GET /manga/next?nextPageUrl=next-page-url\n"
        "```\n\n"
    ),
)
async def next_page_manga(
    nextPageUrl: str = Query(
        ...,
        title="Next Page URL",
        description="The URL of the next page to fetch more data.",
        regex=r"^https?://",
        example="https://teamoney.site/series/yu-ling-shi?page=2",
    )
):
    """
    Retrieve the data for the next page of a specified source.

    Args:
    - nextPageUrl (str): The URL of the next page to fetch more data.

    Returns:
    - dict: A dictionary with the success status, the source name, and the next page data.
    """
    return await more_data_manga(nextPageUrl)
