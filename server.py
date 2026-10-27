
import sqlite3
import hashlib
import os

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


DB_PATH = "app.db"


def get_db():
    return sqlite3.connect(DB_PATH)


@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginData(BaseModel):
    username: str
    password: str  


@app.post("/login")
def login(data: LoginData):
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (data.username, data.password),
        )

    print("Demo username saved:", data.username)

    return {
        "message": "Demo record saved",
        "username": data.username,
    }


@app.get("/users")
def get_users():
    with get_db() as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT id, username, created_at
            FROM users
            ORDER BY id DESC
        """).fetchall()

    return [dict(row) for row in rows]
