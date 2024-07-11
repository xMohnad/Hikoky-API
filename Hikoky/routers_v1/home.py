from fastapi import APIRouter, Query

from ..dependencies import home_data, more_data_home

router = APIRouter(responses={404: {"description": "Not found"}})


@router.get(
    "/home",
    tags=["Home"],
    summary="Retrieve Home Page Data",
    response_description="Successful Response with Home Page Data",
    description=(
        "**Retrieve the home page data for a specified source.**\n\n"
        "This endpoint allows you to fetch the initial set of data from the home page of a specified source. The data includes various metadata and content provided by the source.\n\n"
        "### Features:\n"
        "- Fetch initial home page data.\n"
    ),
)
async def home_source(
    source: str = Query(
        ...,
        title="Source name",
        description="Specify either the source name to get the initial home page data.",
        example="3asq",
    )
):

    return await home_data(source)


@router.get(
    "/home/next",
    tags=["Home"],
    summary="Retrieve naxt Page Data",
    response_description="**Successful Response with Next Page Data**",
    description=(
        "**Retrieve the data for the next page of a specified source.**\n\n"
        "This endpoint allows you to fetch the subsequent set of data from the next page URL provided by the source. It helps in paginating through the data provided by the source.\n\n"
        "### Features:\n"
        "Fetch data from the next page URL."
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

    return await more_data_home(nextPageUrl)
