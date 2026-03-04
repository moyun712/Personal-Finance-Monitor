"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.auth import router as auth_router

app = FastAPI(
    title="智能个人财务管理系统 API",
    version="0.1.0",
    description="AI-driven personal finance management system API",
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────
app.include_router(auth_router)


# ── Health check ──────────────────────────────────────────────
@app.get("/api/v1/health", tags=["health"])
async def health_check():
    """Return service health status."""
    return {"status": "ok"}
