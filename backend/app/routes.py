from fastapi import FastAPI
from fastapi.responses import JSONResponse

def setup_routes(app: FastAPI):
    @app.get("/api/hello")
    async def hello():
        return JSONResponse(content={"message": "Hello from backend!"})