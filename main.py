from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def generate_terrain(size):
    terrain_types = ['plains', 'forest', 'mountain', 'water']
    
    # Initialize the map with random terrain
    terrain = [[random.choice(terrain_types) for _ in range(size)] for _ in range(size)]
    
    # Apply cellular automata rules to create more natural groupings
    for _ in range(5):  # Number of iterations
        new_terrain = [row[:] for row in terrain]
        for i in range(size):
            for j in range(size):
                neighbors = []
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < size and 0 <= nj < size:
                            neighbors.append(terrain[ni][nj])
                
                # Change the cell's terrain type if it's different from the majority of its neighbors
                if len(neighbors) > 0:
                    most_common = max(set(neighbors), key=neighbors.count)
                    if terrain[i][j] != most_common and random.random() < 0.5:
                        new_terrain[i][j] = most_common
        
        terrain = new_terrain
    
    return terrain

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    map_size = 35
    game_data = {
        "message": "Welcome to the Military Simulation Game!",
        "map_size": map_size,
        "terrain": generate_terrain(map_size),
    }
    return templates.TemplateResponse("index.html", {"request": request, **game_data})

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
