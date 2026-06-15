from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.auth import router as auth_router
from api.chat import router as chat_router
from api.collections import router as collections_router

load_dotenv()

app = FastAPI(
    title="Medibot RAG API",
    description="Medical document processing using Docling",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(collections_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return JSONResponse(
        status_code=200,
        content={"status": "healthy", "service": "medibot-rag"},
    )


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return JSONResponse(
        status_code=200,
        content={
            "message": "Medibot RAG API",
            "version": "0.1.0",
            "docs": "/docs",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
