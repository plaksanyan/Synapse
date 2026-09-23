from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import Card, Deck, ReviewLog, SynapticWeight, User

router = APIRouter(prefix="/stats", tags=["stats"])
@router.get("/{deck_id}")
def deck_stats(deck_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    deck = db.scalar(select(Deck).where(Deck.id == deck_id, Deck.user_id == user.id))
    if not deck:
        raise HTTPException(404, "Deck not found")
    cards = db.execute(select(func.count(SynapticWeight.id), func.avg(SynapticWeight.w), func.avg(SynapticWeight.lambda_forget)).join(Card, Card.id == SynapticWeight.card_id).where(Card.deck_id == deck_id, SynapticWeight.user_id == user.id)).one()
    logs = db.scalars(select(ReviewLog).join(Card, Card.id == ReviewLog.card_id).where(Card.deck_id == deck_id, ReviewLog.user_id == user.id).order_by(ReviewLog.reviewed_at)).all()
    return {"deck_id": deck_id, "card_count": cards[0] or 0, "average_weight": cards[1], "average_lambda": cards[2], "review_count": len(logs), "history": [{"card_id": x.card_id, "rating": x.rating, "response_time_ms": x.response_time_ms, "reviewed_at": x.reviewed_at} for x in logs]}
