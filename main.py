from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api import auth, cloth
from app.core.database import get_db

app = FastAPI()
app.include_router(cloth.router)
app.include_router(auth.router)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Annotated[Session, Depends(get_db)]):
    """Proves the database connection works."""

    db.execute(text("SELECT 1"))
    return {"database": "ok"}
