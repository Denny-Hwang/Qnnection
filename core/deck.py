"""core/deck.py – 덱 생성 · 드로우 · 히스토리 · Undo."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

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
        random.shuffle(records)
    if deck_size and deck_size < len(records):
        records = records[:deck_size]
    return records


def pop_next(deck: List[Dict], shuffle: bool = True) -> Optional[Dict]:
    """덱에서 다음 카드 1장 pop. 비어 있으면 None.

    shuffle=True 면 랜덤 위치에서, False 면 앞쪽에서 뽑는다.
    덱을 in-place로 변경.
    """
    if not deck:
        return None
    if shuffle:
        idx = random.randint(0, len(deck) - 1)
        return deck.pop(idx)
    return deck.pop(0)


def draw_next(
    deck: List[Dict],
    history: List[Dict],
    cursor: int,
    shuffle: bool = True,
) -> tuple[Dict | None, List[Dict], int, List[Dict]]:
    """덱에서 질문 1개를 뽑아 히스토리에 추가.

    cursor가 히스토리 중간을 가리키면 단순히 다음 항목으로 이동한다.
    히스토리 끝에 있으면 deck에서 새 카드를 pop.
    """
    if cursor < len(history) - 1:
        cursor += 1
        return history[cursor], history, cursor, deck

    q = pop_next(deck, shuffle=shuffle)
    if q is None:
        return None, history, cursor, deck

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
