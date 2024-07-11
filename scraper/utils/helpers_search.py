from fastapi import HTTPException


async def notfound(source):
    return HTTPException(
        status_code=404,
        detail={
            "success": False,
            "Error": f"not found in {source}",
            "message": "لا توجد مانجا",
        },
    )


async def Failed_retrieve(source):
    return HTTPException(
        status_code=500,
        detail={"success": False, "error": f"Failed to retrieve data in {source}"},
    )
