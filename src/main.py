from fastapi import FastAPI
from uvicorn import run

from contextlib import asynccontextmanager

from .api import router_api_keys, router_users, router_chats
from .database import db
from .config import API_DOMAIN, API_PORT

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    print(0)
    yield
    if db.conn:
        await db.conn.close()
        print(0)

app = FastAPI(lifespan=lifespan)
app.include_router(router_api_keys)
app.include_router(router_users)
app.include_router(router_chats)

if __name__ == "__main__":
    try:
        run("main:app", host=API_DOMAIN, port=API_PORT, reload=True)
    except Exception as e:
        print(e)
