import random
import time
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict
from fastapi.responses import FileResponse


app = FastAPI()

# Vår musikaliska databas (Vänster ord -> Rätt höger ord)
MUSIC_PAIRS = {
    "Caroline": "I Gotta Feeling - Black Eyed Peas",
    "Lennart": "Twist and Shout - Beatles",
    "Britta": "Oh Julie - Shakin' Stevens",
    "Kerstin": "Yes Sir, I Can Boogie - Baccara",
    # "Jan": "Moonlight Serenade - Glen Miller",
    "Henrik": "Freight Train - Alan Jackson",
    "Teta": "Nookie - Limp Bizkit",
    "Anders G": "Basket Case - Green Day",
    "Morris": "The Motto - Ava Max & Tiesto",
    "Elton": "Hand up (Bass Boosted) - Dj Usman Bhatti",
    "Anders S": "Mr Vain - Culture Beast",
    "Maggie": "Highway Man - Hoffmaestro",
    "Kenneth": "Locomotion - Little Eva",
    "Anci": "Sailing - Rod Stewart",
    "Jennifer": "In Da Club - 50 cent",
    "Daniel": "November Rain - XXXXX",
    "Leo B": "Total Eclipse of my Heart - Bonnie Tyler",
    "Chanelle": "As - Stevie Wonder",
    "Elliot": "Eu Vou Vivenciar - Mr Collin & MUCK",
    "Rolf": "Paradise by the Dashbord Light - Meat Loaf",
    "Siri": "How It's Done - Huntrix",
    "Alwin": "Cymatics - Nigel Stanford",
    "Lena": "Dragostea Din Tei - O-Zone",
    "Lars": "Alright - Supergrass",
    "Per": "Bad Boy - Cascada",
    "Moa": "Home - Edward Sharpe & The Magnetic Zone",
    "Alva": "All in för Sverige - Brandsta City Släckers",
    "Leo WK": "Hollow - Smash into Pieces",
    "Emma": "XXXXX - XXXXX",
    "Johanna": "What is Love - Haddaway",
    "Gustaf": "It's a Rainy Day - Ice Mc"
}

# Håller koll på aktiva spelsessioner baserat på spelarnamn (för tidsmätning)
# active_sessions: Dict[str, float] = {}

# Databas i minnet för topplistan
leaderboard = [
]

class StartRequest(BaseModel):
    name: str

# class SubmitRequest(BaseModel):
#     name: str
#     answers: Dict[str, str]  # Format: {"Beatles": "Yesterday", ...}

class SubmitRequest(BaseModel):
    name: str
    score: int

# @app.get("/api/words")
# def get_words():
#     # Returnerar vänsterlistan intakt och högerlistan separat så frontend kan blanda den
#     return {
#         "left": list(MUSIC_PAIRS.keys()),
#         "right": list(MUSIC_PAIRS.values())
#     }

@app.get("/api/words")
def get_words():
    all_pairs = list(MUSIC_PAIRS.items())
    
    # Hur många frågor vill du ha i en spelrunda? 
    # Eftersom det är snabbt på mobilen kan vi ta tigen t.ex. 10 frågor av dina 30 totalt.
    num_questions = len(all_pairs)
    # num_questions = min(10, len(all_pairs))
    sampled_pairs = random.sample(all_pairs, num_questions)
    
    questions = []
    all_artists = list(MUSIC_PAIRS.keys())

    for artist, song in sampled_pairs:
        # Skapa poolen med felaktiga svar (distraktorer)
        other_artists = [a for a in all_artists if a != artist]
        
        # Välj ut 7 slumpmässiga FELAKTIGA artister
        # (Använd min utifall att du har färre än 8 artister totalt i databasen just nu)
        num_distractors = min(7, len(other_artists))
        sampled_distractors = random.sample(other_artists, num_distractors)
        
        # Sätt ihop till 8 alternativ totalt och blanda dem
        options = sampled_distractors + [artist]
        random.shuffle(options)
        
        questions.append({
            "song": song,
            "correct_artist": artist,
            "options": options
        })

    random.shuffle(questions) 
    return {
        "questions": questions
    }


@app.post("/api/submit")
def submit_game(payload: SubmitRequest):
    name = payload.name.strip()
    if not name: 
        raise HTTPException(status_code=400, detail="Namn saknas")
    leaderboard.append({"name": name[:15], "score": payload.score})
    return {"success": True}

@app.post("/api/start")
def start_game(payload: StartRequest):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Namn kan inte vara tomt")
    
    # Spara starttiden för denna spelare
    # active_sessions[name] = time.time()
    return {"status": "started"}

# @app.post("/api/submit")
# def submit_game(payload: SubmitRequest):
#     name = payload.name.strip()
#     
#     # Kontrollera om svaren är rätt
#     correct_count = 0
#     for left_word, right_word in payload.answers.items():
#         if MUSIC_PAIRS.get(left_word) == right_word:
#             correct_count += 1
#             
# 
#     # Spara till topplistan
#     leaderboard.append({"name": name[:15], "score": correct_count})
#     return {"success": True, "score": correct_count}

@app.get("/api/leaderboard")
def get_leaderboard():
    sorted_lb = sorted(leaderboard, key=lambda x: x["score"], reverse=True)
    return sorted_lb[:10]

@app.get("/leaderboard")
def get_leaderboard_page():
    # Returnerar den nya HTML-filen direkt till webbläsaren
    return FileResponse("public/leaderboard.html")


app.mount("/", StaticFiles(directory="public", html=True), name="public")

