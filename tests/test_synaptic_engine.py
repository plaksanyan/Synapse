from app.synaptic_engine import (decay_weight, recalculate_lambda, update_weight_on_failure,
                                 update_weight_on_success, weight_to_next_interval)

def test_repeated_success_increases_weight_and_interval():
    w = 1.0
    for _ in range(8):
        w = update_weight_on_success(w, 4, 1500)
    assert w > 2.0
    assert weight_to_next_interval(w) > weight_to_next_interval(1.0)

def test_repeated_failures_reduce_weight_and_interval():
    w = 4.0
    for _ in range(4):
        w = update_weight_on_failure(w)
    assert w < 0.3
    assert weight_to_next_interval(w) < weight_to_next_interval(4.0)

def test_mixed_pattern_stays_bounded_and_adapts_forgetting():
    w = 1.0
    w = update_weight_on_success(w, 4, 1000)
    w = update_weight_on_failure(w)
    w = update_weight_on_success(w, 3, 4000)
    assert 0.05 <= w <= 10
    fast = recalculate_lambda([{"rating": 1, "days_since_review": 1}])
    slow = recalculate_lambda([{"rating": 4, "days_since_review": 30}])
    assert 0.01 <= fast <= 2.0
    assert slow < fast

def test_long_gap_decays_strength_and_clamps_interval():
    assert decay_weight(2.0, 0.15, 30) < decay_weight(2.0, 0.15, 1)
    assert decay_weight(2.0, 0.15, 10000) < 1e-5
    assert 0.25 <= weight_to_next_interval(10) <= 365
