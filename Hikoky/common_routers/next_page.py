from fastapi import APIRouter, Query
from ..dependencies import more_data_home

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/home/next",
    tags=["Home"],
    summary="Retrieve Next Page Data",
    response_description=(
        "### **Successful Response with Next Page Data**\n\n"
        "## Returns:\n"
        "- **success (bool)**: Indicates whether the data retrieval was successful.\n"
        "- **source (str)**: The name of the source.\n"
        "- **data (dict)**: The next page data retrieved from the source."
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
        "GET /home/next?nextPageUrl=next-page-url\n"
        "```\n\n"
    ),
)
async def next_page_home(
    nextPageUrl: str = Query(
        ...,
        title="Next Page URL",
        description="The URL of the next page to fetch more data.",
        regex=r"^https?://",
        example="https://3asq.org/manga/page/2/",
    )
):
    """
    Retrieve the data for the next page of a specified source.

    Args:
    - nextPageUrl (str): The URL of the next page to fetch more data.

    Returns:
    - dict: A dictionary with the success status, the source name, and the next page data.
    """
    return await more_data_home(nextPageUrl)
