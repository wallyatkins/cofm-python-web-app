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
    
    terrain_types = ['plains', 'forest', 'mountain', 'water', 'desert']
    
    # Adjust terrain probabilities based on map type
    if selected_map_type == 'archipelago':
        weights = [2, 1, 1, 6, 1]  # More water with small islands
    elif selected_map_type == 'coastal':
        weights = [3, 2, 1, 4, 1]  # Almost half land, half water
    elif selected_map_type == 'mountains':
        weights = [1, 2, 5, 1, 1]  # More mountains
    elif selected_map_type == 'plains':
        weights = [5, 2, 1, 1, 2]  # More plains and some desert
    elif selected_map_type == 'swamp':
        weights = [1, 3, 1, 4, 0]  # More water and forest, no desert
    
    # Initialize the map with random terrain based on weights
    terrain = [[{'type': random.choices(terrain_types, weights=weights)[0], 'height': 1, 'moisture': random.random()} for _ in range(size)] for _ in range(size)]

    # Set initial heights and adjust based on terrain type
    for i in range(size):
        for j in range(size):
            if terrain[i][j]['type'] == 'mountain':
                terrain[i][j]['height'] = random.randint(8, 10)
            elif terrain[i][j]['type'] == 'water':
                terrain[i][j]['height'] = 1
            elif terrain[i][j]['type'] == 'desert':
                terrain[i][j]['height'] = random.randint(2, 5)
                terrain[i][j]['moisture'] = random.uniform(0, 0.3)
            elif terrain[i][j]['type'] == 'plains':
                terrain[i][j]['height'] = random.randint(2, 4)
                terrain[i][j]['moisture'] = random.uniform(0.3, 0.6)
            else:  # forest
                terrain[i][j]['height'] = random.randint(3, 6)
                terrain[i][j]['moisture'] = random.uniform(0.6, 1.0)

    # Adjust heights based on neighboring terrain types
    for _ in range(5):  # Increase the number of iterations for smoother transitions
        new_terrain = [[cell.copy() for cell in row] for row in terrain]
        for i in range(size):
            for j in range(size):
                if terrain[i][j]['type'] != 'mountain' and terrain[i][j]['type'] != 'water':
                    neighbors = []
                    water_count = 0
                    mountain_count = 0
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            ni, nj = i + di, j + dj
                            if 0 <= ni < size and 0 <= nj < size:
                                neighbors.append(terrain[ni][nj]['height'])
                                if terrain[ni][nj]['type'] == 'water':
                                    water_count += 1
                                elif terrain[ni][nj]['type'] == 'mountain':
                                    mountain_count += 1
                    
                    avg_neighbor_height = sum(neighbors) / len(neighbors)
                    height_adjustment = 0
                    
                    # Lower height near water
                    if water_count > 0:
                        height_adjustment -= water_count * 0.3
                    
                    # Increase height near mountains
                    if mountain_count > 0:
                        height_adjustment += mountain_count * 0.3
                    
                    new_height = (terrain[i][j]['height'] * 0.7 + avg_neighbor_height * 0.3 + height_adjustment)
                    new_terrain[i][j]['height'] = max(1, min(new_height, 10))  # Clamp between 1 and 10
        
        terrain = new_terrain

    # Normalize heights to be between 1 and 10
    min_height = min(cell['height'] for row in terrain for cell in row)
    max_height = max(cell['height'] for row in terrain for cell in row)
    for i in range(size):
        for j in range(size):
            if terrain[i][j]['type'] != 'water' and terrain[i][j]['type'] != 'mountain':
                terrain[i][j]['height'] = 1 + (terrain[i][j]['height'] - min_height) * 9 / (max_height - min_height)

    # For coastal type, create a more defined coastline
    if selected_map_type == 'coastal':
        # Generate a random angle for the coastline
        angle = random.uniform(0, 2 * math.pi)
        
        # Calculate the normal vector to the coastline
        normal_x = math.cos(angle)
        normal_y = math.sin(angle)
        
        # Determine the center point of the map
        center_x = center_y = size / 2
        
        # Offset to move the coastline
        offset = random.uniform(-size/4, size/4)
        
        for i in range(size):
            for j in range(size):
                # Calculate the position relative to the center
                rel_x = j - center_x
                rel_y = i - center_y
                
                # Project the point onto the normal vector
                projection = rel_x * normal_x + rel_y * normal_y
                
                # Determine if the point is land or water
                is_land = projection > offset
                
                if is_land:
                    terrain[i][j]['type'] = random.choices(['plains', 'forest', 'mountain'], weights=[3, 2, 1])[0]
                else:
                    terrain[i][j]['type'] = 'water'
        
        # Add some noise to the coastline
        noise_factor = random.uniform(0.1, 0.3)
        for i in range(size):
            for j in range(size):
                if random.random() < noise_factor:
                    terrain[i][j]['type'] = random.choice(['plains', 'forest', 'mountain', 'water'])
    
    # Apply cellular automata rules to create more natural groupings
    for _ in range(5):  # Number of iterations
        new_terrain = [[cell.copy() for cell in row] for row in terrain]
        for i in range(size):
            for j in range(size):
                neighbors = []
                for di in [-1, 0, 1]:
                    for dj in [-1, 0, 1]:
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < size and 0 <= nj < size:
                            neighbors.append(terrain[ni][nj]['type'])
                
                # Change the cell's terrain type if it's different from the majority of its neighbors
                if len(neighbors) > 0:
                    most_common = max(set(neighbors), key=neighbors.count)
                    if terrain[i][j]['type'] != most_common and random.random() < 0.5:
                        new_terrain[i][j]['type'] = most_common
        
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
