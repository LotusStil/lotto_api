from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json
import os

app = FastAPI()

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

# 🔹 Endpoint-uri publice
@app.get("/draws/megamillions/latest", response_model=DrawWithSpecial)
def get_megamillions_latest():
    return read_fixed_draw("Megamillions")

@app.get("/draws/powerball/latest", response_model=DrawWithSpecial)
def get_powerball_latest():
    return read_fixed_draw("Powerball")

@app.get("/draws/megabucks/latest", response_model=DrawWithoutSpecial)
def get_megabucks_latest():
    return read_fixed_draw("Megabucks")

# 🔹 Endpoint de test/debug
@app.get("/healthz")
def health_check():
    return {
        "status": "ok",
        "files": os.listdir(".")
    }
