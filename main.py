from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import random
import math

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def generate_terrain(size):
    map_types = ['archipelago', 'coastal', 'mountains', 'plains', 'swamp']
    selected_map_type = random.choice(map_types)
    
    terrain_types = ['plains', 'forest', 'mountain', 'water']
    
    # Adjust terrain probabilities based on map type
    if selected_map_type == 'archipelago':
        weights = [2, 1, 1, 6]  # More water with small islands
    elif selected_map_type == 'coastal':
        weights = [3, 2, 1, 4]  # Almost half land, half water
    elif selected_map_type == 'mountains':
        weights = [1, 2, 5, 1]  # More mountains
    elif selected_map_type == 'plains':
        weights = [5, 2, 1, 1]  # More plains
    elif selected_map_type == 'swamp':
        weights = [1, 3, 1, 4]  # More water and forest
    
    # Initialize the map with random terrain based on weights
    terrain = [[random.choices(terrain_types, weights=weights)[0] for _ in range(size)] for _ in range(size)]

    # For coastal type, create a more defined coastline
    if selected_map_type == 'coastal':
        direction = random.choice(['horizontal', 'vertical'])
        land_side = random.choice(['left', 'right']) if direction == 'horizontal' else random.choice(['top', 'bottom'])
        
        for i in range(size):
            for j in range(size):
                if direction == 'horizontal':
                    is_land = (j < size // 2) if land_side == 'left' else (j >= size // 2)
                else:  # vertical
                    is_land = (i < size // 2) if land_side == 'top' else (i >= size // 2)
                
                if is_land:
                    terrain[i][j] = random.choices(['plains', 'forest', 'mountain'], weights=[3, 2, 1])[0]
                else:
                    terrain[i][j] = 'water'
        
        # Add some curvature to the coastline
        curve_factor = random.randint(1, 3)
        for i in range(size):
            curve = int(curve_factor * math.sin(i * math.pi / (size // 2)))
            if direction == 'horizontal':
                split_point = size // 2 + curve
                for j in range(size):
                    if land_side == 'left':
                        if j < split_point:
                            terrain[i][j] = random.choices(['plains', 'forest', 'mountain'], weights=[3, 2, 1])[0]
                        else:
                            terrain[i][j] = 'water'
                    else:
                        if j >= split_point:
                            terrain[i][j] = random.choices(['plains', 'forest', 'mountain'], weights=[3, 2, 1])[0]
                        else:
                            terrain[i][j] = 'water'
            else:  # vertical
                split_point = size // 2 + curve
                for j in range(size):
                    if land_side == 'top':
                        if i < split_point:
                            terrain[i][j] = random.choices(['plains', 'forest', 'mountain'], weights=[3, 2, 1])[0]
                        else:
                            terrain[i][j] = 'water'
                    else:
                        if i >= split_point:
                            terrain[i][j] = random.choices(['plains', 'forest', 'mountain'], weights=[3, 2, 1])[0]
                        else:
                            terrain[i][j] = 'water'
    
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
    
    return terrain, selected_map_type

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    map_size = 36
    terrain, map_type = generate_terrain(map_size)
    game_data = {
        "message": f"Welcome to the Military Simulation Game! Map type: {map_type.capitalize()}",
        "map_size": map_size,
        "terrain": terrain,
        "map_type": map_type,
    }
    return templates.TemplateResponse("index.html", {"request": request, **game_data})

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
