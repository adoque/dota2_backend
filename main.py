import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx
import google.generativeai as genai

load_dotenv()
app = FastAPI()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Разрешаем CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Лучше указать домен фронта
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Внешний API OpenDota
EXTERNAL_API = "https://api.opendota.com/api/heroes"

print("API_KEY = ", os.getenv("GEMINI_API_KEY"))

@app.get("/")
def root():
    return {"message": "Dota 2 Heroes API Proxy работает ✅"}

@app.get("/api/heroes")
async def get_heroes():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(EXTERNAL_API)
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка подключения к API: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=response.status_code, detail=f"Ошибка от API OpenDota: {str(e)}")

@app.get("/api/heroes/{localized_name}")
async def get_hero_by_name(localized_name: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(EXTERNAL_API)
            response.raise_for_status()
            heroes = response.json()
            match = [hero for hero in heroes if hero["localized_name"].lower() == localized_name.lower()]
            if not match:
                raise HTTPException(status_code=404, detail="Герой не найден")
            return match[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/heroes/role/{role}")
async def get_heroes_by_role(role: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(EXTERNAL_API)
            response.raise_for_status()
            heroes = response.json()
            matched = [
                hero for hero in heroes
                if any(r.lower() == role.lower() for r in hero.get("roles", []))
            ]
            if not matched:
                raise HTTPException(status_code=404, detail="Нет героев с такой ролью")
            return matched
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/gemini/advice")
async def get_gemini_dota_advice(request: Request):
    data = await request.json()
    hero = data.get("hero")
    role = data.get("role")

    prompt = f"""
Ты профессиональный игрок в Dota 2. Объясни, как играть на герое {hero} в роли {role}.
Дай советы по способностям, закупу, позиционированию и сильным/слабым сторонам.
"""

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return {"advice": response.text}
    except Exception as e:
        return {"error": str(e)}
