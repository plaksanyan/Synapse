from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import Card, Deck, ReviewLog, SynapticWeight, User

router = APIRouter(tags=["sync"])
@router.get("/sync")
def sync(since: datetime = Query(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    deck_ids = select(Deck.id).where(Deck.user_id == user.id)
    cards = db.scalars(select(Card).where(Card.deck_id.in_(deck_ids), Card.updated_at >= since)).all()
    decks = db.scalars(select(Deck).where(Deck.user_id == user.id, Deck.updated_at >= since)).all()
    weights = db.scalars(select(SynapticWeight).where(SynapticWeight.user_id == user.id, SynapticWeight.updated_at >= since)).all()
    reviews = db.scalars(select(ReviewLog).where(ReviewLog.user_id == user.id, ReviewLog.reviewed_at >= since)).all()
    return {"since": since, "decks": decks, "cards": cards, "weights": [{"id": x.id, "card_id": x.card_id, "w": x.w, "lambda_forget": x.lambda_forget, "last_reviewed_at": x.last_reviewed_at, "next_review_at": x.next_review_at, "updated_at": x.updated_at} for x in weights], "reviews": [{"id": x.id, "card_id": x.card_id, "rating": x.rating, "response_time_ms": x.response_time_ms, "reviewed_at": x.reviewed_at} for x in reviews]}
