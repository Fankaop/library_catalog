from fastapi import FastAPI

app = FastAPI(
    title='Library Catalog API',
    description='REST API',
    version='1.0.0',
)

@app.get("/")
async def root():
    return {"message": "Welcome to Library Catalog API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
