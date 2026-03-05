from fastapi import FastAPI

from src.api.routes import router as api_router

app = FastAPI(title="SEO Audit Service")
app.include_router(api_router)
