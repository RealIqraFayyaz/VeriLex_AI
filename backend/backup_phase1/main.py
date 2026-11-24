from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.core.config import settings
from app.api.routes import router
@asynccontextmanager
async def lifespan(app):
    await init_db()
    yield
app=FastAPI(title="VeriLex AI API",version="0.1.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.allowed_origins,allow_credentials=True,allow_methods=["GET","POST","PATCH","DELETE","OPTIONS"],allow_headers=["Authorization","Content-Type"])
app.include_router(router)
@app.get("/")
async def root(): return {"name":"VeriLex AI","docs":"/docs","health":"/health"}
@app.get("/health")
async def health(): return {"status":"ok","service":"verilex-api"}
