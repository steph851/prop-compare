#!/usr/bin/env python3
"""
Prop Firm Intelligence System - FastAPI Server
"""
import os
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

ROOT = Path(__file__).parent

app = FastAPI(title="PropIntel API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
LOGS_DIR = ROOT / "logs"


@app.get("/")
async def root():
    index_path = OUTPUT_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding="utf-8"))
    return {"message": "PropIntel API - Run /api/firms to see data"}


@app.get("/api/firms")
async def list_firms():
    firms = []
    for f in DATA_DIR.glob("*-futures.json"):
        firms.append(f.stem.replace("-futures", ""))
    return {"firms": firms, "count": len(firms)}


@app.get("/api/firm/{firm_id}")
async def get_firm(firm_id: str):
    data_file = DATA_DIR / f"{firm_id}-futures.json"
    if not data_file.exists():
        raise HTTPException(status_code=404, detail="Firm not found")
    return JSONResponse(json.loads(data_file.read_text(encoding="utf-8")))


@app.get("/api/comparison")
async def get_comparison():
    latest = OUTPUT_DIR / "categorized-master-latest.json"
    if not latest.exists():
        raise HTTPException(status_code=404, detail="No comparison data")
    return JSONResponse(json.loads(latest.read_text(encoding="utf-8")))


@app.get("/api/decisions")
async def get_decisions():
    decisions_file = LOGS_DIR / "decisions.log"
    if not decisions_file.exists():
        return {"decisions": []}
    lines = decisions_file.read_text(encoding="utf-8").strip().split("\n")
    return {"decisions": [l for l in lines if l], "count": len(lines)}


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "2.0"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)