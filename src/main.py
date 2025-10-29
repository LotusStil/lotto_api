from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os

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

# 🔹 Endpointuri pentru fiecare joc
@app.get("/draws/megamillions/all", response_model=List[DrawWithSpecial])
def get_megamillions_all(x_token: Optional[str] = Header(None)):
    validate_token(x_token)
    data = read_all_draws("Megamillions")
    return [DrawWithSpecial(**d) for d in data]

@app.get("/draws/powerball/all", response_model=List[DrawWithSpecial])
def get_powerball_all(x_token: Optional[str] = Header(None)):
    validate_token(x_token)
    data = read_all_draws("Powerball")
    return [DrawWithSpecial(**d) for d in data]

@app.get("/draws/megabucks/all", response_model=List[DrawWithoutSpecial])
def get_megabucks_all(x_token: Optional[str] = Header(None)):
    validate_token(x_token)
    data = read_all_draws("Megabucks")
    return [DrawWithoutSpecial(**d) for d in data]

# 🔹 Health check
@app.get("/healthz")
def health_check():
    return {
        "status": "ok",
        "token_loaded": bool(ACCESS_TOKEN),
        "files": os.listdir(".")
    }
