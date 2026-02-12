"""core/deck.py – 덱 생성 · 드로우 · 히스토리 · Undo."""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd


def build_deck(
    pool: pd.DataFrame,
    deck_size: int = 0,
    shuffle: bool = True,
) -> List[Dict]:
    """pool DataFrame → 질문 리스트(dict). shuffle=True면 매번 새로 셔플."""
    if pool.empty:
        return []
    records = pool.to_dict("records")
    if shuffle:
        random.shuffle(records)  # 시스템 랜덤, 매번 다른 순서
    if deck_size and deck_size < len(records):
        records = records[:deck_size]
    return records


def draw_next(
    deck: List[Dict],
    history: List[Dict],
    cursor: int,
    shuffle: bool = True,
) -> tuple[Dict | None, List[Dict], int, List[Dict]]:
    """
    덱에서 질문 1개를 뽑아 히스토리에 추가.
    shuffle=True: 남은 덱에서 랜덤 위치로 뽑음 (매번 다른 순서).
    shuffle=False: 앞에서부터 순서대로 뽑음.
    """
    # 히스토리 앞쪽에 있으면 next로 이동만
    if cursor < len(history) - 1:
        cursor += 1
        return history[cursor], history, cursor, deck

    if not deck:
        return None, history, cursor, deck

    if shuffle:
        idx = random.randint(0, len(deck) - 1)
        q = deck.pop(idx)
    else:
        q = deck.pop(0)

    history.append(q)
    cursor = len(history) - 1
    return q, history, cursor, deck


# ── 히스토리 탐색 ────────────────────────────────────────
def history_prev(history: List[Dict], cursor: int) -> tuple[Dict | None, int]:
    if cursor > 0:
        cursor -= 1
        return history[cursor], cursor
    if history:
        return history[0], 0
    return None, cursor


def history_next(history: List[Dict], cursor: int) -> tuple[Dict | None, int]:
    if cursor < len(history) - 1:
        cursor += 1
        return history[cursor], cursor
    if history:
        return history[-1], len(history) - 1
    return None, cursor


# ── 스피드게임 이벤트 스택 ───────────────────────────────
@dataclass
class SpeedEvent:
    action: str  # "correct" | "pass"
    question: Dict = field(default_factory=dict)
    score_delta: int = 0


def push_event(stack: List[SpeedEvent], event: SpeedEvent) -> List[SpeedEvent]:
    stack.append(event)
    return stack


def undo_event(stack: List[SpeedEvent]) -> tuple[SpeedEvent | None, List[SpeedEvent]]:
    if not stack:
        return None, stack
    return stack.pop(), stack