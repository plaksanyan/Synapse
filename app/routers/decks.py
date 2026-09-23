from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import Deck, User
from ..schemas import DeckCreate, DeckOut

router = APIRouter(prefix="/decks", tags=["decks"])
def owned_deck(db: Session, deck_id: int, user_id: int) -> Deck:
    deck = db.scalar(select(Deck).where(Deck.id == deck_id, Deck.user_id == user_id))
    if not deck:
        raise HTTPException(404, "Deck not found")
    return deck
@router.get("", response_model=list[DeckOut])
def list_decks(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(select(Deck).where(Deck.user_id == user.id).order_by(Deck.id)).all()
@router.post("", response_model=DeckOut, status_code=201)
def create_deck(data: DeckCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    deck = Deck(user_id=user.id, name=data.name.strip())
    if not deck.name:
        raise HTTPException(422, "Deck name cannot be blank")
    db.add(deck); db.commit(); db.refresh(deck)
    return deck
