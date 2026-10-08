import time
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict
from fastapi.responses import FileResponse


app = FastAPI()

# Vår musikaliska databas (Vänster ord -> Rätt höger ord)
MUSIC_PAIRS = {
    "Lennart": "Twist and Shout - Beatles",
    "Jennifer": "In Da Club - 50 cent",
    "Kenneth": "Locomotion - Little Eva",
    "Anci": "Sailing - Rod Stewart",
    "Rolf": "Paradise by the dashbord light - Meat Loaf",
    "Anders S": "Mr Vain - Culture Beast",
    "Elliot": "Eu Vou Vivenciar - Mr Collin & MUCK",
    "Dainel": "November Rain",
    "Teta": "Nookie - Limp Bizkit",
    "Kerstin": "Yes Sir, I Can Boogie - Baccara",
    "Jan": "Moonlight Serenade - Glen Miller",
    "Maggie": "Highway Man - Hoffmaestro",
    "Britta": "Oh Julie - Shakin' Stevens",
    "Morris": "The Motto - Ava Max & Tiesto",
    "Leo B": "Total Eclipse of my Heart - Bonnie Tyler",
    "Siri": "Lush Life - Zara Larsson",
    "Anders G": "Basket Case - Green Day",
    "Lena": "Dragostea Din Tei - O-Zone",
    "Chanelle": "As - Stevie Wonder",
    "Per": "Bad Boy - Cascada",
    "Alva": "All in för Sverige - Brandsta City Släckers",
    "Leo WK": "Hollow - Smash into Pieces",
    "Lars": "Alright - Supergrass"
}

# Håller koll på aktiva spelsessioner baserat på spelarnamn (för tidsmätning)
# active_sessions: Dict[str, float] = {}

# Databas i minnet för topplistan
leaderboard = [
    {"name": "Trum-Nisse", "score": 1},
    {"name": "Synth-Sofia", "score": 15.8}
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
    # active_sessions[name] = time.time()
    return {"status": "started"}

@app.post("/api/submit")
def submit_game(payload: SubmitRequest):
    name = payload.name.strip()
    
    # Kontrollera om svaren är rätt
    correct_count = 0
    for left_word, right_word in payload.answers.items():
        if MUSIC_PAIRS.get(left_word) == right_word:
            correct_count += 1
            

    # Spara till topplistan
    leaderboard.append({"name": name[:15], "score": correct_count})
    return {"success": True, "score": correct_count}

@app.get("/api/leaderboard")
def get_leaderboard():
    sorted_lb = sorted(leaderboard, key=lambda x: x["score"], reverse=True)
    return sorted_lb[:10]

@app.get("/leaderboard")
def get_leaderboard_page():
    # Returnerar den nya HTML-filen direkt till webbläsaren
    return FileResponse("public/leaderboard.html")


app.mount("/", StaticFiles(directory="public", html=True), name="public")

