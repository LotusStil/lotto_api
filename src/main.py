from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime

app = FastAPI()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# 🔹 Structuri de date
class DrawWithSpecial(BaseModel):
    drawDate: str
    numbers: List[int]
    specialNumber: int
    nextDraw: str
    estimatedJackpot: int

class DrawWithoutSpecial(BaseModel):
    drawDate: str
    numbers: List[int]
    nextDraw: str
    estimatedJackpot: int

# 🔹 Validare token
def validate_token(x_token: Optional[str]):
    if not x_token or x_token != ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail="Token invalid")

# 🔹 Citire fișier complet
def read_all_draws(prefix: str):
    filename = f"{prefix}.json"
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Fișierul {filename} nu există")
    with open(filename, "r") as f:
        data = json.load(f)
    return data

# 🔹 Filtrare după dată
def filter_draws_since(data: List[dict], date_str: str):
    try:
        cutoff = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Format dată invalid. Folosește YYYY-MM-DD.")
    return [d for d in data if datetime.strptime(d["drawDate"], "%Y-%m-%d") > cutoff]

# 🔹 Endpointuri existente
@app.get("/draws/{game}/latest")
def get_latest_draw(game: str, x_token: Optional[str] = Header(None)):
    validate_token(x_token)
    data = read_all_draws(game.capitalize())
    if not data:
        raise HTTPException(status_code=404, detail="Nicio extragere disponibilă")
    raw = data[0]
    if game.lower() == "megabucks":
        return DrawWithoutSpecial(**raw)
    else:
        return DrawWithSpecial(**raw)

# 🔹 Endpoint nou: toate extragerile
@app.get("/draws/{game}/all")
def get_all_draws(game: str, x_token: Optional[str] = Header(None)):
    validate_token(x_token)
    return read_all_draws(game.capitalize())

# 🔹 Endpoint nou: extrageri după o dată
@app.get("/draws/{game}/since/{date}")
def get_draws_since(game: str, date: str, x_token: Optional[str] = Header(None)):
    validate_token(x_token)
    data = read_all_draws(game.capitalize())
    filtered = filter_draws_since(data, date)
    return filtered

# 🔹 Health check
@app.get("/healthz")
def health_check():
    return {
        "status": "ok",
        "token_loaded": bool(ACCESS_TOKEN),
        "files": os.listdir(".")
    }
