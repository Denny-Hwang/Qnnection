"""core/state.py – st.session_state 초기화 · 모드 전환 리셋."""

from __future__ import annotations
import streamlit as st

# ── 기본값 정의 ─────────────────────────────────────────
# 위젯 key와 겹치는 값(mode, display_mode, selected_sets, deck_size 등)은
# 위젯이 직접 관리하므로 여기서 제외한다.
_COMMON_DEFAULTS = {
    "pool_df": None,
}

_ICEBREAKER_DEFAULTS = {
    "ib_deck": [],
    "ib_history": [],
    "ib_cursor": -1,
    "ib_current": None,
    "ib_show_overlay": False,
    "ib_deck_built": False,
}

_SPEED_DEFAULTS = {
    "sp_deck": [],
    "sp_timer_seconds": 60,
    "sp_running": False,
    "sp_paused": False,
    "sp_start_ts": None,
    "sp_pause_elapsed": 0.0,
    "sp_score": 0,
    "sp_correct": 0,
    "sp_pass": 0,
    "sp_event_stack": [],
    "sp_current": None,
    "sp_finished": False,
    "sp_deck_built": False,
    "sp_round_history": [],
}


def init_state():
    """앱 시작 시 세션 state 초기화 (이미 있는 키는 건너뜀)."""
    for defaults in (_COMMON_DEFAULTS, _ICEBREAKER_DEFAULTS, _SPEED_DEFAULTS):
        for k, v in defaults.items():
            if k not in st.session_state:
                st.session_state[k] = v


def reset_icebreaker():
    """아이스브레이킹 관련 상태 초기화."""
    for k, v in _ICEBREAKER_DEFAULTS.items():
        st.session_state[k] = v


def reset_speed():
    """스피드게임 관련 상태 초기화."""
    for k, v in _SPEED_DEFAULTS.items():
        st.session_state[k] = v


def reset_all():
    """전체 세션 초기화."""
    reset_icebreaker()
    reset_speed()
    for k, v in _COMMON_DEFAULTS.items():
        st.session_state[k] = v