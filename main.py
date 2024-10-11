from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def generate_terrain(size):
    terrain_types = ['plains', 'forest', 'mountain', 'water']
    return [[random.choice(terrain_types) for _ in range(size)] for _ in range(size)]

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    map_size = 25
    game_data = {
        "message": "Welcome to the Military Simulation Game!",
        "map_size": map_size,
        "terrain": generate_terrain(map_size),
    }
    return templates.TemplateResponse("index.html", {"request": request, **game_data})

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
