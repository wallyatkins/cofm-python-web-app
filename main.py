from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "Hello from FastAPI!"})

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
