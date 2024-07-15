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
