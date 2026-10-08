import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

# Datamodell för att validera inkommande poäng
class ScoreItem(BaseModel):
    name: str = Field(..., max_length=15)
    time: float

# Temporär databas i serverns minne
leaderboard = [
    {"name": "Linnea", "time": 14.5},
    {"name": "Oscar", "time": 18.2},
    {"name": "Sofia", "time": 22.1}
]

# API: Hämta topplistan (sorterad på snabbast tid, max 10 st)
@app.get("/api/leaderboard", response_model=List[ScoreItem])
def get_leaderboard():
    sorted_leaderboard = sorted(leaderboard, key=lambda x: x["time"])
    return sorted_leaderboard[:10]

# API: Skicka in en ny tid
@app.post("/api/leaderboard")
def submit_score(item: ScoreItem):
    # Rensa namnet från extra mellanslag
    clean_name = item.name.strip()
    if not clean_name:
        clean_name = "Anonym"
        
    leaderboard.append({
        "name": clean_name[:15],
        "time": round(item.time, 2)
    })
    return {"success": True, "message": "Resultat sparat!"}

# Servera frontend-filer (viktigt att detta ligger EFTER API-routerna)
app.mount("/", StaticFiles(directory="public", html=True), name="public")

