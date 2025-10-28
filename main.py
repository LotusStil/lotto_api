from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List
import json
import glob
import os

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
print("Token din ENV:", ACCESS_TOKEN)
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

# 🔹 Funcție pentru a găsi cel mai nou fișier
def get_latest_file(prefix: str) -> str:
    files = glob.glob(f"{prefix}_*.json")
    if not files:
        raise FileNotFoundError(f"Nu există fișiere pentru {prefix}")
    files.sort(reverse=True)
    return files[0]

# 🔹 Funcție pentru citirea extragerii
def read_latest_draw(prefix: str):
    filename = get_latest_file(prefix)
    with open(filename, "r") as f:
        data = json.load(f)
    raw = data[0]

    if prefix == "Megabucks":
        return DrawWithoutSpecial(**raw)
    elif prefix in ["Megamillions", "Powerball"]:
        return DrawWithSpecial(**raw)
    else:
        raise ValueError("Joc necunoscut")

# 🔹 Endpoint-uri cu protecție prin token
@app.get("/draws/megamillions/latest", response_model=DrawWithSpecial)
def get_megamillions_latest(x_token: str = Header(...)):
    if x_token != ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail="Token invalid")
    return read_latest_draw("Megamillions")

@app.get("/draws/powerball/latest", response_model=DrawWithSpecial)
def get_powerball_latest(x_token: str = Header(...)):
    if x_token != ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail="Token invalid")
    return read_latest_draw("Powerball")

@app.get("/draws/megabucks/latest", response_model=DrawWithoutSpecial)
def get_megabucks_latest(x_token: str = Header(...)):
    if x_token != ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail="Token invalid")
    return read_latest_draw("Megabucks")
