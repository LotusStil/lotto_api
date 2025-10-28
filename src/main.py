from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI()

# 🔐 Token din variabile de mediu
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
print("Token din ENV:", ACCESS_TOKEN)

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

# 🔹 Funcție pentru citirea fișierului fix
def read_fixed_draw(prefix: str):
    filename = f"{prefix}.json"
    print(f"Încerc să citesc: {filename}")
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Fișierul {filename} nu există")
    with open(filename, "r") as f:
        data = json.load(f)
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError(f"Fișierul {filename} nu conține un array valid cu extrageri")
    raw = data[0]

    if prefix == "Megabucks":
        return DrawWithoutSpecial(**raw)
    elif prefix in ["Megamillions", "Powerball"]:
        return DrawWithSpecial(**raw)
    else:
        raise ValueError("Joc necunoscut")

# 🔹 Endpoint-uri protejate
@app.get("/draws/megamillions/latest", response_model=DrawWithSpecial)
def get_megamillions_latest(x_token: Optional[str] = Header(None)):
    validate_token(x_token)
    return read_fixed_draw("Megamillions")

@app.get("/draws/powerball/latest", response_model=DrawWithSpecial)
def get_powerball_latest(x_token: Optional[str] = Header(None)):
    validate_token(x_token)
    return read_fixed_draw("Powerball")

@app.get("/draws/megabucks/latest", response_model=DrawWithoutSpecial)
def get_megabucks_latest(x_token: Optional[str] = Header(None)):
    validate_token(x_token)
    return read_fixed_draw("Megabucks")

# 🔹 Endpoint de test/debug
@app.get("/healthz")
def health_check():
    return {
        "status": "ok",
        "token_loaded": bool(ACCESS_TOKEN),
        "files": os.listdir(".")
    }
