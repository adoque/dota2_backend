import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx
import google.generativeai as genai
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

load_dotenv()
app = FastAPI(title="Dota 2 Advisor API")

# Настройка Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Разрешаем CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Лучше указать конкретный домен фронтенда в продакшене
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Базовая инструкция для чат-бота
SYSTEM_PROMPT = """
Ты — профессиональный консультант и эксперт по игре Dota 2.

Твоя задача:
1. Давать подробные советы по игре за разных героев Dota 2
2. Объяснять механики игры и стратегии
3. Рассказывать о лучших предметах для героев
4. Помогать с вопросами по командной игре и мета-игре
5. Отвечать на вопросы о патчах и обновлениях

ВАЖНО: Если вопрос пользователя НЕ связан с Dota 2, вежливо ответь:
"Извините, я могу отвечать только на вопросы, связанные с Dota 2. Задайте мне вопрос о героях, стратегиях, предметах или игровой механике."

Если вопрос кажется подозрительным или неуместным, даже если он косвенно упоминает Dota 2, ответь:
"Пожалуйста, задайте вопрос, непосредственно связанный с игрой Dota 2."

Всегда отвечай на русском языке, кратко и по существу.
"""

# Внешний API OpenDota
EXTERNAL_API = "https://api.opendota.com/api"

# Модель Gemini
model = genai.GenerativeModel("gemini-1.5-flash")

# Хранилище диалогов
chat_sessions = {}

# Структура сообщения
class Message(BaseModel):
    message: str
    session_id: Optional[str] = "default"

# Структура создания сессии
class Session(BaseModel):
    session_id: str

# Структура ответа
class ChatResponse(BaseModel):
    reply: str
    is_dota_related: bool

@app.get("/")
def root():
    return {"message": "Dota 2 Advisor API работает ✅", "version": "1.0.0"}

@app.get("/api/heroes")
async def get_heroes():
    """Получить список всех героев Dota 2"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXTERNAL_API}/heroes")
            response.raise_for_status()
        return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка подключения к API: {str(e)}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=response.status_code, detail=f"Ошибка от API OpenDota: {str(e)}")

@app.get("/api/heroes/{hero_id}")
async def get_hero_by_id(hero_id: int):
    """Получить информацию о герое по ID"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXTERNAL_API}/heroes")
            response.raise_for_status()
            heroes = response.json()
            
            hero = next((h for h in heroes if h["id"] == hero_id), None)
            if not hero:
                raise HTTPException(status_code=404, detail="Герой не найден")
            
            return hero
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/heroes/name/{localized_name}")
async def get_hero_by_name(localized_name: str):
    """Получить информацию о герое по имени"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXTERNAL_API}/heroes")
            response.raise_for_status()
            heroes = response.json()
            
            hero = next((h for h in heroes if h["localized_name"].lower() == localized_name.lower()), None)
            if not hero:
                raise HTTPException(status_code=404, detail="Герой не найден")
            
            return hero
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/heroes/role/{role}")
async def get_heroes_by_role(role: str):
    """Получить список героев по роли"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXTERNAL_API}/heroes")
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

@app.post("/api/chat/create_session")
def create_chat_session(session_data: Session):
    """Создать новую сессию чата"""
    session_id = session_data.session_id
    
    if session_id in chat_sessions:
        return {"message": "Сессия уже существует", "session_id": session_id}
    
    chat_sessions[session_id] = [
        {"role": "user", "parts": [SYSTEM_PROMPT]}
    ]
    
    return {"message": "Сессия создана", "session_id": session_id}

def is_dota_related(message: str) -> bool:
    """Простая проверка на то, связан ли вопрос с Dota 2"""
    dota_keywords = [
        "dota", "дота", "дота2", "dota2", "герой", "hero", "предмет", "item", 
        "игра", "game", "мета", "meta", "стратегия", "strategy", "патч", "patch",
        "способность", "ability", "керри", "carry", "саппорт", "support", "мид", "mid",
        "лейн", "lane", "бой", "fight", "шмот", "артефакт", "artifact", "мап", "map",
        "карта", "турнир", "tournament", "чемпионат", "championship", "команда", "team"
    ]
    
    # Проверяем наличие ключевых слов
    msg_lower = message.lower()
    for keyword in dota_keywords:
        if keyword in msg_lower:
            return True
    
    # Если нет явных ключевых слов Dota 2, запрос может быть не связан с игрой
    return False

@app.post("/api/chat/message")
def chat_with_dota_expert(msg: Message) -> ChatResponse:
    """Обработка сообщения пользователя и получение ответа от Dota 2 эксперта"""
    session_id = msg.session_id
    user_message = msg.message
    
    # Проверяем существование сессии, если нет - создаем новую
    if session_id not in chat_sessions:
        chat_sessions[session_id] = [
            {"role": "user", "parts": [SYSTEM_PROMPT]}
        ]
    
    # Первичная проверка на то, связан ли вопрос с Dota 2
    dota_related = is_dota_related(user_message)
    
    if not dota_related:
        # Если вопрос не похож на связанный с Dota 2, предупреждаем пользователя
        return ChatResponse(
            reply="Извините, я могу отвечать только на вопросы, связанные с Dota 2. Задайте мне вопрос о героях, стратегиях, предметах или игровой механике.",
            is_dota_related=False
        )
    
    # Добавляем сообщение пользователя в историю
    chat_sessions[session_id].append({"role": "user", "parts": [user_message]})
    
    try:
        # Получаем ответ от модели Gemini
        chat = model.start_chat(history=chat_sessions[session_id])
        response = chat.send_message(user_message)
        
        # Добавляем ответ модели в историю
        chat_sessions[session_id].append({"role": "model", "parts": [response.text]})
        
        # Ограничиваем длину истории (чтобы избежать переполнения токенов)
        if len(chat_sessions[session_id]) > 20:
            # Оставляем системный промпт и последние 10 сообщений
            chat_sessions[session_id] = [chat_sessions[session_id][0]] + chat_sessions[session_id][-10:]
        
        return ChatResponse(reply=response.text, is_dota_related=True)
    except Exception as e:
        return ChatResponse(
            reply=f"Произошла ошибка при обработке вашего запроса: {str(e)}",
            is_dota_related=True
        )

@app.delete("/api/chat/session/{session_id}")
def delete_chat_session(session_id: str):
    """Удалить сессию чата"""
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        return {"message": "Сессия удалена"}
    else:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

# Расширенная информация о героях (можно добавить больше эндпоинтов с дополнительной информацией)
@app.get("/api/heroes/matches/{hero_id}")
async def get_hero_matches(hero_id: int):
    """Получить последние матчи с участием героя"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EXTERNAL_API}/heroes/{hero_id}/matches")
            response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)