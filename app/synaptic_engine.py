"""Pure functions implementing a deliberately transparent adaptive memory model."""
from math import exp, isfinite
from statistics import mean
from typing import Iterable

MIN_WEIGHT, MAX_WEIGHT = 0.05, 10.0
MIN_LAMBDA, MAX_LAMBDA = 0.01, 2.0

def update_weight_on_success(w: float, rating: int, response_time: int) -> float:
    """Strengthens a successful trace: w' = min(10, w + (0.15 + 0.12(r-1)) * speed).

    Higher recall quality (ratings 1–4) potentiates the trace more. Fast responses
    modestly increase gain; speed is bounded to avoid making latency dominate recall.
    """
    if not 1 <= rating <= 4 or response_time < 0:
        raise ValueError("rating must be 1..4 and response_time non-negative")
    speed = max(0.5, min(1.5, 12000 / max(response_time, 1000)))
    return min(MAX_WEIGHT, max(MIN_WEIGHT, w) + (0.15 + 0.12 * (rating - 1)) * speed)

def update_weight_on_failure(w: float) -> float:
    """Applies long-term depression: w' = max(0.05, 0.5w).

    Forgetting halves the trace to cause a near-term retry while retaining a small
    positive baseline, so the exponential model remains well-defined.
    """
    return max(MIN_WEIGHT, max(0.0, w) * 0.5)

def decay_weight(w: float, lambda_forget: float, days_since_review: float) -> float:
    """Returns w(t) = w₀·e^(−λt); λ is per day and elapsed days cannot be negative.

    Exponential decay is a simple continuous-time approximation to passive loss of
    a memory trace between active retrieval events.
    """
    if lambda_forget <= 0 or days_since_review < 0:
        raise ValueError("lambda_forget must be positive and elapsed days non-negative")
    return max(0.0, w) * exp(-lambda_forget * days_since_review)

def recalculate_lambda(review_history: Iterable) -> float:
    """Estimates λ = clamp(−ln(p̄)/d̄, 0.01, 2.0) from successful recall fractions.

    Each history item may be a mapping or object with rating and days_since_review.
    High success implies slower forgetting; short gaps and poor recall imply faster
    forgetting. The bounds prevent pathological intervals for sparse histories.
    """
    estimates = []
    for item in review_history:
        get = item.get if isinstance(item, dict) else lambda key, default=None: getattr(item, key, default)
        rating, days = get("rating"), get("days_since_review", get("elapsed_days", 1.0))
        if rating is None or days is None or days < 0:
            continue
        p = max(0.05, min(0.99, rating / 4.0))
        estimates.append(-__import__("math").log(p) / max(float(days), 0.25))
    if not estimates:
        return 0.15
    return max(MIN_LAMBDA, min(MAX_LAMBDA, mean(estimates)))

def weight_to_next_interval(w: float) -> float:
    """Maps strength to days: interval = clamp(0.25·exp(0.55w), 0.25, 365).

    Increasing trace strength yields longer but bounded spacing; the quarter-day
    floor allows prompt retries and the one-year ceiling avoids excessive jumps.
    """
    if not isfinite(w):
        raise ValueError("weight must be finite")
    return max(0.25, min(365.0, 0.25 * exp(0.55 * max(0.0, w))))
