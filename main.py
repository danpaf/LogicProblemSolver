import json
from pprint import pprint

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.responses import HTMLResponse

import funcs
from db.models import NodeDBModel, RibDBModel
from settings import init_db

init_db()
node = NodeDBModel.select()[0]
rib = RibDBModel.select().where(RibDBModel.from_node == node)

answers = funcs.getRoutes()
answers2 = funcs.remove_duplicates_from_json("answers.json")
if(answers == answers2):
    print("хуйня")



app = FastAPI()
# Модель для данных о пользователе
class User(BaseModel):
    username: str
    password: str

# Список зарегистрированных пользователей
users_db = []

# Маршрут для регистрации пользователя

@app.get("/js")
async def get_js():
    return FileResponse("script.js")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/auth", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})




@app.get('/cycles')
async def get_cycles_api():
    with open("answers.json") as f:
        data = json.load(f)
    return data

