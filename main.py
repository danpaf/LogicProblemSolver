import json
from pprint import pprint

import uuid as uuid
from urllib import request

import bcrypt
import jsonify as jsonify
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from peewee import IntegrityError
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import requests
import funcs
from db.models import NodeDBModel, RibDBModel, RouteDBModel, UserDBModel
from settings import init_db

init_db()
node = NodeDBModel.select()[0]
rib = RibDBModel.select().where(RibDBModel.from_node == node)

answers = funcs.getRoutes()
answers2 = funcs.remove_duplicates_from_json_test("answers.json")

app = FastAPI()

class UserCreate(BaseModel):
    username: str
    password: str
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


@app.post('/register', response_model=dict)
def register_user(user: dict):
    username = user.get('username')
    hashed_password = bcrypt.hashpw(user.get('password').encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        UserDBModel.create(login=username, password_hash=hashed_password)
        return {'message': 'User registered successfully!'}
    except IntegrityError:
        raise HTTPException(status_code=400, detail='Username already exists')


@app.get("/sign-in", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@app.get('/api/oldcycles')
async def get_oldcycles_api():
    with open("answers.json") as f:
        data = json.load(f)
    return data


def serialize_route(route):
    return {
        'uuid': str(route.uuid),
        'weight': route.weight,
        'length': route.length,
        'edge_type': route.edge_type,
        'cycle': route.cycle,
        'start_date': route.start_date.strftime('%Y-%m-%d'),
        'end_date': route.end_date.strftime('%Y-%m-%d'),
        'cityfrom': route.cityfrom,
        'cityto': route.cityto,
    }


@app.get('/api/cycles')
async def get_cycles_api(uuid: uuid.UUID = None):
    routes = RouteDBModel.select()
    if uuid:
        routes = [route for route in routes if route.uuid == uuid]
    data = [serialize_route(route) for route in routes]

    return data
