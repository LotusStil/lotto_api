from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import json
import glob
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

# 🔹 Funcție pentru a găsi cel mai nou fișier
def get_latest_file(prefix: str) -> str:
    files = glob.glob(f"{prefix}_*.json")
    print(f"Fișiere găsite pentru {prefix}:", files)
    if not files:
        raise FileNotFoundError(f"Nu există fișiere pentru {prefix}")
    files.sort(reverse=True)
    return files[0]

# 🔹 Funcție pentru citirea extragerii
def read_latest_draw(prefix: str):
    filename = get_latest_file(prefix)
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
    return read_latest_draw("Megamillions")

@app.get("/draws/powerball/latest", response_model=DrawWithSpecial)
def get_powerball_latest():
    return read_latest_draw("Powerball")

@app.get("/draws/megabucks/latest", response_model=DrawWithoutSpecial)
def get_megabucks_latest():
    return read_latest_draw("Megabucks")

# 🔹 Endpoint de test/debug
@app.get("/healthz")
def health_check():
    return {
        "status": "ok",
        "files_megamillions": glob.glob("Megamillions_*.json"),
        "files_powerball": glob.glob("Powerball_*.json"),
        "files_megabucks": glob.glob("Megabucks_*.json")
    }

# 🔹 Endpoint pentru listarea fișierelor din container
@app.get("/debug/files")
def list_files():
    root_files = os.listdir(".")
    return {
        "root_files": root_files
    }
