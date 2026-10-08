import time
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI()

# Vår musikaliska databas (Vänster ord -> Rätt höger ord)
MUSIC_PAIRS = {
    "Beatles": "Yesterday",
    "ABBA": "Mamma Mia",
    "Avicii": "Levels",
    "Queen": "Bohemian Rhapsody",
    "Zara Larsson": "Lush Life"
}

# Håller koll på aktiva spelsessioner baserat på spelarnamn (för tidsmätning)
active_sessions: Dict[str, float] = {}

# Databas i minnet för topplistan
leaderboard = [
    {"name": "Trum-Nisse", "time": 12.4},
    {"name": "Synth-Sofia", "time": 15.8}
]

class StartRequest(BaseModel):
    name: str

class SubmitRequest(BaseModel):
    name: str
    answers: Dict[str, str]  # Format: {"Beatles": "Yesterday", ...}

@app.get("/api/words")
def get_words():
    # Returnerar vänsterlistan intakt och högerlistan separat så frontend kan blanda den
    return {
        "left": list(MUSIC_PAIRS.keys()),
        "right": list(MUSIC_PAIRS.values())
    }

@app.post("/api/start")
def start_game(payload: StartRequest):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Namn kan inte vara tomt")
    
    # Spara starttiden för denna spelare
    active_sessions[name] = time.time()
    return {"status": "started"}

@app.post("/api/submit")
def submit_game(payload: SubmitRequest):
    name = payload.name.strip()
    if name not in active_sessions:
        raise HTTPException(status_code=400, detail="Ingen aktiv spelsession hittades för detta namn")
    
    end_time = time.time()
    start_time = active_sessions.pop(name)
    total_time = round(end_time - start_time, 2)
    
    # Kontrollera om svaren är rätt
    correct_count = 0
    for left_word, right_word in payload.answers.items():
        if MUSIC_PAIRS.get(left_word) == right_word:
            correct_count += 1
            
    if correct_count != len(MUSIC_PAIRS):
        raise HTTPException(status_code=400, detail=f"Alla par är inte korrekta! Du fick {correct_count} rätt.")

    # Spara till topplistan
    leaderboard.append({"name": name[:15], "time": total_time})
    return {"success": True, "time": total_time}

@app.get("/api/leaderboard")
def get_leaderboard():
    sorted_lb = sorted(leaderboard, key=lambda x: x["time"])
    return sorted_lb[:10]

app.mount("/", StaticFiles(directory="public", html=True), name="public")

