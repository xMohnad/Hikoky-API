from fastapi import APIRouter, Query
from ..dependencies import get_handler, fetch_data

router = APIRouter(
    responses={404: {"description": "Not found"}},
)

router = APIRouter()

async def fetch_and_process_data(identifier: str):
    url, handler = await get_handler(identifier)
    result = await fetch_data(url)
    results = handler["home_page"](result)
    return {'success': True, "source": handler["name"], "data": results}

@router.get(
    "/{source}", 
    tags=["Home"],
    summary="Retrieve Home Page Data",
    response_description=(
        "### **Successful Response with Home Page Data**\n\n"
        "## Returns:\n"
        "- **success (bool)**: Indicates whether the data retrieval was successful.\n"
        "- **source (str)**: The name of the source.\n"
        "- **data (dict)**: The home page data retrieved from the source.\n\n\n\n"

    ),
    description=(
        "**Retrieve the home page data for a specified source.**\n\n"
        "This endpoint allows you to fetch the initial set of data from the home page of a specified source. The data includes various metadata and content provided by the source.\n\n"
        "### Features:\n"
        "- Fetch initial home page data.\n"
        "- Provides metadata and content from the specified source.\n"
        "- Can be used to initialize the dataset for further processing or display.\n\n"
        "### Usage:\n"
        "- **source (str)**: The name of the source from which you want to retrieve the home page data.\n\n"
        "### Examples:\n"
        "```\n"
        "GET /source/my-source\n"
        "```\n\n"
    )
)
async def home_source(
    source: str
):
    """
    Retrieve the home page data for a specified source.

    Args:
    - source (str): The name of the source to retrieve the initial home page data.

    Returns:
    - dict: A dictionary with the success status, the source name, and the home page data.
    """
    return await fetch_and_process_data(source)


@router.get(
    "/nextPage/", 
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
        "- Supports pagination for large datasets.\n"
        "- Continues data retrieval from where the previous request left off.\n\n"
        "### Usage:\n"
        "- **nextPageUrl (str)**: The URL of the next page to fetch more data.\n\n"
        "### Examples:\n"
        "```\n"
        "GET /nextPage/?nextPageUrl=next-page-url\n"
        "```\n\n"
    )
)
async def home_next_page(
        nextPageUrl: str = Query(
        ..., 
        title="Next Page URL",
        description="The URL of the next page to fetch more data.",
        min_length=1,
        max_length=2083,
        regex=r'^https?://',
        example="https://3asq.org/manga/page/2/"
    )
):
    """
    Retrieve the data for the next page of a specified source.

    Args:
    - nextPageUrl (str): The URL of the next page to fetch more data.

    Returns:
    - dict: A dictionary with the success status, the source name, and the next page data.
    """
    return await fetch_and_process_data(nextPageUrl)
