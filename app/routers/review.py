from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..database import get_db
from ..models import Card, Deck, ReviewLog, SynapticWeight, User
from ..schemas import ReviewCreate, ReviewOut
from ..synaptic_engine import decay_weight, update_weight_on_success, update_weight_on_failure, weight_to_next_interval, recalculate_lambda

router = APIRouter(tags=["review"])
@router.post("/review", response_model=ReviewOut)
def review(data: ReviewCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    card = db.get(Card, data.card_id)
    if not card or not db.scalar(select(Deck.id).where(Deck.id == card.deck_id, Deck.user_id == user.id)):
        raise HTTPException(404, "Card not found")
    now = datetime.now(timezone.utc)
    weight = db.scalar(select(SynapticWeight).where(SynapticWeight.card_id == card.id, SynapticWeight.user_id == user.id))
    if weight is None:
        weight = SynapticWeight(card_id=card.id, user_id=user.id); db.add(weight)
    if data.rating >= 3:
        weight.w = update_weight_on_success(weight.w, data.rating, data.response_time_ms)
    else:
        weight.w = update_weight_on_failure(weight.w)
    if weight.last_reviewed_at is not None:
        last = weight.last_reviewed_at
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        elapsed = max(0.0, (now - last).total_seconds() / 86400)
        weight.w = decay_weight(weight.w, weight.lambda_forget, elapsed)
    old_reviews = db.scalars(select(ReviewLog).where(ReviewLog.user_id == user.id, ReviewLog.card_id == card.id).order_by(ReviewLog.reviewed_at)).all()
    history = []
    previous = None
    for entry in old_reviews:
        reviewed_at = entry.reviewed_at
        if reviewed_at.tzinfo is None:
            reviewed_at = reviewed_at.replace(tzinfo=timezone.utc)
        gap = max(0.25, (reviewed_at - previous).total_seconds() / 86400) if previous else 1.0
        history.append({"rating": entry.rating, "days_since_review": gap})
        previous = reviewed_at
    weight.lambda_forget = recalculate_lambda(history)
    weight.last_reviewed_at = now
    interval = weight_to_next_interval(weight.w)
    if data.rating < 3:
        interval = min(interval, 0.25)
    weight.next_review_at = now + timedelta(days=interval)
    db.add(ReviewLog(user_id=user.id, card_id=card.id, rating=data.rating, response_time_ms=data.response_time_ms, reviewed_at=now))
    db.commit(); db.refresh(weight)
    return ReviewOut(card_id=card.id, w=weight.w, lambda_forget=weight.lambda_forget, last_reviewed_at=weight.last_reviewed_at, next_review_at=weight.next_review_at, interval_days=interval)
