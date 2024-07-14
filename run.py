import uvicorn

if __name__ == "__main__":
    uvicorn.run("Hikoky.main:app", port=8000, reload=True)
