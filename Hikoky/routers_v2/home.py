from fastapi import APIRouter
from ..dependencies import home_data

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/source/{source}",
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
    ),
)
async def home_source(source: str):
    """
    Retrieve the home page data for a specified source.

    Args:
    - source (str): The name of the source to retrieve the initial home page data.

    Returns:
    - dict: A dictionary with the success status, the source name, and the home page data.
    """
    return await home_data(source)
