from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, budgets, categories, dashboard, export, transactions

app = FastAPI(
    title="CatatUang API",
    description="API manajemen keuangan untuk mahasiswa dan UMKM kecil Indonesia",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(dashboard.router)
app.include_router(export.router)


@app.get("/")
def root():
    return {"message": "CatatUang API v1.0 — /docs untuk dokumentasi interaktif"}
