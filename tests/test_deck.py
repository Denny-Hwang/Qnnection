"""덱 빌드/드로우/Undo 단위 테스트."""

from __future__ import annotations

import random

import pandas as pd

from core.deck import (
    SpeedEvent,
    build_deck,
    draw_next,
    history_next,
    history_prev,
    pop_next,
    push_event,
    undo_event,
)


def _make_pool(n: int = 10) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [f"q{i:02d}" for i in range(n)],
            "ko": [f"한글{i}" for i in range(n)],
            "en": [f"EN{i}" for i in range(n)],
            "category": ["fun"] * n,
            "depth": [1] * n,
            "difficulty": [1] * n,
            "tags": [""] * n,
            "enabled": [1] * n,
        }
    )


def test_build_deck_empty_pool_returns_empty():
    df = pd.DataFrame()
    assert build_deck(df) == []


def test_build_deck_respects_deck_size():
    pool = _make_pool(20)
    deck = build_deck(pool, deck_size=5, shuffle=False)
    assert len(deck) == 5
    # shuffle=False면 앞에서부터
    assert [d["id"] for d in deck] == [f"q{i:02d}" for i in range(5)]


def test_build_deck_zero_means_all():
    pool = _make_pool(7)
    deck = build_deck(pool, deck_size=0, shuffle=False)
    assert len(deck) == 7


def test_build_deck_shuffle_changes_order():
    random.seed(42)
    pool = _make_pool(30)
    a = build_deck(pool, shuffle=True)
    random.seed(99)
    b = build_deck(pool, shuffle=True)
    assert a != b


def test_pop_next_returns_none_when_empty():
    assert pop_next([]) is None


def test_pop_next_no_shuffle_pops_front():
    deck = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    q = pop_next(deck, shuffle=False)
    assert q == {"id": "a"}
    assert deck == [{"id": "b"}, {"id": "c"}]


def test_pop_next_shuffle_removes_one():
    deck = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    q = pop_next(deck, shuffle=True)
    assert q is not None
    assert len(deck) == 2
    assert q not in deck


def test_draw_next_appends_to_history():
    deck = [{"id": "a"}, {"id": "b"}]
    history = []
    q, history, cursor, deck = draw_next(deck, history, -1, shuffle=False)
    assert q == {"id": "a"}
    assert history == [{"id": "a"}]
    assert cursor == 0
    assert deck == [{"id": "b"}]


def test_draw_next_in_history_middle_moves_cursor():
    history = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    deck = [{"id": "d"}]
    q, history, cursor, deck = draw_next(deck, history, cursor=0, shuffle=False)
    # cursor 0 → 1, history/deck 변동 없음
    assert q == {"id": "b"}
    assert cursor == 1
    assert deck == [{"id": "d"}]
    assert len(history) == 3


def test_draw_next_returns_none_when_at_end_and_deck_empty():
    history = [{"id": "a"}]
    deck = []
    q, history, cursor, deck = draw_next(deck, history, cursor=0, shuffle=False)
    assert q is None
    assert deck == []


def test_history_prev_clamps_to_start():
    history = [{"id": "a"}, {"id": "b"}]
    q, c = history_prev(history, 0)
    assert q == {"id": "a"}
    assert c == 0


def test_history_next_clamps_to_end():
    history = [{"id": "a"}, {"id": "b"}]
    q, c = history_next(history, 1)
    assert q == {"id": "b"}
    assert c == 1


def test_undo_event_returns_none_for_empty_stack():
    popped, stack = undo_event([])
    assert popped is None
    assert stack == []


def test_push_and_undo_event():
    e1 = SpeedEvent(action="correct", question={"id": "a"}, score_delta=1)
    e2 = SpeedEvent(action="pass", question={"id": "b"}, score_delta=0)
    stack = push_event([], e1)
    stack = push_event(stack, e2)
    assert stack == [e1, e2]
    popped, stack = undo_event(stack)
    assert popped == e2
    assert stack == [e1]
