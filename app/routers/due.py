from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import Card, Deck, SynapticWeight, User
from ..schemas import CardOut

router = APIRouter(prefix="/decks", tags=["review"])
@router.get("/{deck_id}/due", response_model=list[CardOut])
def due_cards(deck_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    deck = db.scalar(select(Deck).where(Deck.id == deck_id, Deck.user_id == user.id))
    if not deck:
        raise HTTPException(404, "Deck not found")
    now = datetime.now(timezone.utc)
    return db.scalars(select(Card).join(SynapticWeight, SynapticWeight.card_id == Card.id).where(Card.deck_id == deck_id, SynapticWeight.user_id == user.id, SynapticWeight.next_review_at <= now).order_by(SynapticWeight.next_review_at)).all()
