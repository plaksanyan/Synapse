from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import Card, Deck, SynapticWeight, User
from ..schemas import CardCreate, CardOut, ImportRequest
from .decks import owned_deck
from ..importers.txt_importer import parse_txt
from ..importers.cloze_parser import parse_cloze
from ..importers.anki_importer import parse_anki_text

router = APIRouter(prefix="/decks/{deck_id}", tags=["cards"])
@router.get("/cards", response_model=list[CardOut])
def list_cards(deck_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    owned_deck(db, deck_id, user.id)
    return db.scalars(select(Card).where(Card.deck_id == deck_id).order_by(Card.id)).all()
@router.post("/cards", response_model=CardOut, status_code=201)
def create_card(deck_id: int, data: CardCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    owned_deck(db, deck_id, user.id)
    if data.format not in {"text", "markdown", "cloze"}:
        raise HTTPException(422, "format must be text, markdown or cloze")
    card = Card(deck_id=deck_id, front=data.front, back=data.back, format=data.format)
    db.add(card); db.flush(); db.add(SynapticWeight(user_id=user.id, card_id=card.id))
    db.commit(); db.refresh(card)
    return card
@router.post("/import", response_model=list[CardOut], status_code=201)
def import_cards(deck_id: int, data: ImportRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    owned_deck(db, deck_id, user.id)
    fmt = data.format
    if fmt is None:
        fmt = "cloze" if "{{c" in data.text else "txt"
    try:
        cards = {"txt": parse_txt, "cloze": parse_cloze, "anki": parse_anki_text}[fmt](data.text)
    except KeyError:
        raise HTTPException(422, "format must be txt, cloze or anki")
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    created = []
    for item in cards:
        card = Card(deck_id=deck_id, **item)
        db.add(card); db.flush(); db.add(SynapticWeight(user_id=user.id, card_id=card.id)); created.append(card)
    db.commit()
    for card in created:
        db.refresh(card)
    return created
