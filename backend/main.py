from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, dashboard, energy, carbon, system

app = FastAPI(title="数字化能碳管理系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(system.router, prefix="/api/system", tags=["系统管理"])
app.include_router(energy.router, prefix="/api/energy", tags=["能源管理"])
app.include_router(carbon.router, prefix="/api/carbon", tags=["碳管理"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["看板"])

@app.get("/api/health")
def health():
    return {"code": 200, "message": "ok", "data": None}
