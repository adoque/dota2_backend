**Dota 2 AI Assistant**

**Описание**

Проект представляет собой умного чат‑бота для помощи новичкам и опытным игрокам Dota 2. Бот подсказывает, какого героя выбрать, дает советы по стратегии и отвечает на любые вопросы, связанные с игрой.
Сервис состоит из двух частей: бэкенда на FastAPI и фронтенда на React.

---

## Особенности

* Интеллектуальный чат‑бот на базе модели Google Gemini
* Системный промпт, задающий роль ИИ как эксперта по Dota 2
* Минимальный MVP без БД и авторизации для быстрой итерации

---

## Технологический стек

| Компонент      | Технология               |
| -------------- | ------------------------ |
| **Бэкенд**     | Python, FastAPI, Uvicorn |
| **Модель ИИ**  | Google Gemini API        |
| **Фронтенд**   | Next                     |
| **Управление** | dotenv (.env)            |

---

##  Установка и запуск

### 1. Подготовка виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
### 2. Настройка переменных окружения

Создайте файл .env в корне проекта:

GEMINI_API_KEY=ваш_API_ключ
---

### 3. Бэкенд

git clone 
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
### 4. Фронтенд

cd my-app/
npm install
npm run dev
---

## Запуск сервера

В корне папки backend:

uvicorn main:app --reload
```
---

## Полезные ссылки
* [Swagger](https://dota2backend-production.up.railway.app/docs#/) 
* Демо-ролик: [Loom](https://www.loom.com/share/0e77c44affee46c2ab30d17f60a0a5a2)
* Репозиторий фронтенда: [github.com/adoque/dota\_front](https://github.com/adoque/dota_front)
* Деплой фронтенда: [dota-front.vercel.app](https://dota-front.vercel.app)

---

##Что планирую сделать в будущем
* Добавить базу данных для хранения пользователей и статистики
* Реализовать аутентификацию и ограничения на историю диалога
* Оптимизация расхода токенов и управление контекстом
* Расширение модели советов: собственные сборы, мидеры, керри и т.д.
