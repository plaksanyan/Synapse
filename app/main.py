from fastapi import FastAPI
from .database import Base, engine
from . import models
from .routers import auth, cards, decks, due, review, stats, sync

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Synapse API", version="0.1.0", description="Adaptive spaced repetition backend")
app.include_router(auth.router)
app.include_router(decks.router)
app.include_router(cards.router)
app.include_router(cards.card_router)
app.include_router(due.router)
app.include_router(review.router)
app.include_router(stats.router)
app.include_router(sync.router)

@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}
