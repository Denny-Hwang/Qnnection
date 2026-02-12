"""
Qnnection – Question + Connection
교회 모임 아이스브레이킹 & 스피드게임 TV 앱
"""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import streamlit as st

from core.loader import scan_sets, load_and_prepare
from core.filtering import Filters, apply_filters, get_unique_categories, get_unique_tags
from core.deck import build_deck, draw_next, history_prev, history_next, SpeedEvent, push_event, undo_event
from core.ui_styles import GLOBAL_CSS, format_question, question_card_html
from core.state import init_state, reset_icebreaker, reset_speed
from core.i18n import t

# ── 경로 ────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DECK_DIRS = {
    "icebreaker": BASE_DIR / "decks" / "icebreaker",
    "speedgame": BASE_DIR / "decks" / "speedgame",
}

# ── 페이지 설정 ─────────────────────────────────────────
st.set_page_config(
    page_title="Qnnection",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
init_state()

# ═══════════════════════════════════════════════════════════
#  사이드바
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="app-title">Qnnection</div>', unsafe_allow_html=True)

    # ── UI 언어 ────────────────────────────────────
    ui_lang = st.radio(
        "🌐 UI Language",
        ["ko", "en"],
        format_func=lambda x: "한국어" if x == "ko" else "English",
        horizontal=True,
        key="_ui_lang",
    )
    L = ui_lang

    st.caption(t("app_subtitle", L))
    st.divider()

    # ── 모드 선택 ──────────────────────────────────
    mode_options = ["icebreaker", "speedgame"]
    mode_labels = [t("mode_icebreaker", L), t("mode_speedgame", L)]

    mode_display = st.radio(
        t("mode_label", L), mode_labels, horizontal=True, key="_mode_display",
    )
    mode = mode_options[mode_labels.index(mode_display)]

    if "prev_mode" not in st.session_state:
        st.session_state.prev_mode = mode
    if mode != st.session_state.prev_mode:
        reset_icebreaker()
        reset_speed()
        st.session_state.prev_mode = mode

    deck_dir = DECK_DIRS[mode]
    set_metas = scan_sets(str(deck_dir))

    if not set_metas:
        st.warning(t("no_csv", L))
        st.stop()

    # ── 세트 선택 ──────────────────────────────────
    valid_sets = [m for m in set_metas if m.valid]
    invalid_sets = [m for m in set_metas if not m.valid]

    if invalid_sets:
        with st.expander(f"{t('load_fail_title', L)} ({len(invalid_sets)})", expanded=False):
            for m in invalid_sets:
                st.error(f"**{m.name}**: {'; '.join(m.errors)}")

    if not valid_sets:
        st.error(t("no_valid_sets", L))
        st.stop()

    set_names = [m.name for m in valid_sets]
    selected = st.multiselect(
        t("select_sets", L), set_names, default=set_names, key="selected_sets",
    )

    if not selected:
        st.info(t("select_sets_hint", L))
        st.stop()

    # ── 데이터 로드 ───────────────────────────────
    @st.cache_data(show_spinner=False)
    def _load_sets(paths_names: list[tuple[str, str]]) -> pd.DataFrame:
        frames = []
        for path, name in paths_names:
            df = load_and_prepare(path, set_name=name)
            if df is not None:
                frames.append(df)
        if frames:
            return pd.concat(frames, ignore_index=True)
        return pd.DataFrame()

    paths_names = [(m.path, m.name) for m in valid_sets if m.name in selected]
    pool_all = _load_sets(paths_names)

    if pool_all.empty:
        st.warning(t("load_empty", L))
        st.stop()

    # ── 표시 언어 ──────────────────────────────────
    display_mode = st.selectbox(
        t("display_lang", L),
        ["KO only", "EN only", "KO → EN", "EN → KO"],
        key="display_mode",
    )

    # ── 필터 ───────────────────────────────────────
    st.divider()
    st.subheader(t("filter_title", L))

    cats = get_unique_categories(pool_all)
    sel_cats = st.multiselect(t("filter_category", L), cats, default=[], key="_filter_cats")
    depth_range = st.slider(t("filter_depth", L), 1, 5, (1, 5), key="_filter_depth")

    diff_range = (1, 3)
    if mode == "speedgame":
        diff_range = st.slider(t("filter_difficulty", L), 1, 3, (1, 3), key="_filter_diff")

    tags_all = get_unique_tags(pool_all)
    sel_tags = st.multiselect(t("filter_tags", L), tags_all, default=[], key="_filter_tags")

    filters = Filters(
        categories=sel_cats,
        depth_min=depth_range[0], depth_max=depth_range[1],
        difficulty_min=diff_range[0], difficulty_max=diff_range[1],
        tags_include=sel_tags,
    )
    pool_filtered = apply_filters(pool_all, filters)

    # ── Deck size + Shuffle ────────────────────────
    max_pool = len(pool_filtered)
    st.caption(t("pool_count", L, n=max_pool))

    if max_pool == 0:
        st.warning(t("filter_empty", L))
        st.stop()

    deck_size = st.number_input(
        t("deck_size", L), min_value=0, max_value=max_pool,
        value=0 if max_pool <= 50 else 20, step=1, key="deck_size",
    )
    shuffle_on = st.toggle(t("shuffle_toggle", L), value=True, key="_shuffle")

    # ── 스피드게임 전용 ────────────────────────────
    if mode == "speedgame":
        st.divider()
        st.subheader(t("timer_title", L))
        timer_preset = st.radio(
            t("timer_preset", L), [30, 60, 90], index=1, horizontal=True, key="_timer_preset",
        )
        # 프리셋 변경 시 number_input 값도 동기화
        if "_prev_timer_preset" not in st.session_state:
            st.session_state._prev_timer_preset = timer_preset
        if timer_preset != st.session_state._prev_timer_preset:
            st.session_state.sp_timer_seconds = timer_preset
            st.session_state._prev_timer_preset = timer_preset
        st.number_input(
            t("timer_custom", L), min_value=10, max_value=300,
            value=timer_preset, step=5, key="sp_timer_seconds",
        )


# ═══════════════════════════════════════════════════════════
#  헬퍼
# ═══════════════════════════════════════════════════════════
def _build_fresh_deck(prefix: str):
    """pool_filtered로 새 덱 생성. shuffle 옵션 반영."""
    ds = st.session_state.deck_size or 0
    shuf = st.session_state.get("_shuffle", True)
    deck = build_deck(pool_filtered, deck_size=ds, shuffle=shuf)
    st.session_state[f"{prefix}_deck"] = deck
    st.session_state[f"{prefix}_deck_built"] = True


# ═══════════════════════════════════════════════════════════
#  메인 – 아이스브레이킹
# ═══════════════════════════════════════════════════════════
if mode == "icebreaker":
    st.markdown('<div class="app-title">Qnnection</div>', unsafe_allow_html=True)

    # ── 덱 구축 / 초기화 ──────────────────────────
    col_build, col_reset, _ = st.columns([1, 1, 3])
    with col_build:
        if st.button(t("btn_build", L), use_container_width=True):
            reset_icebreaker()
            _build_fresh_deck("ib")
            st.rerun()
    with col_reset:
        if st.button(t("btn_reset", L), use_container_width=True):
            reset_icebreaker()
            _build_fresh_deck("ib")
            st.rerun()

    # 첫 진입 시 자동 빌드
    if not st.session_state.ib_deck_built:
        _build_fresh_deck("ib")

    deck = st.session_state.ib_deck
    history = st.session_state.ib_history
    cursor = st.session_state.ib_cursor

    st.caption(t("remaining_cards", L, remain=len(deck), used=len(history)))

    # ── 컨트롤 ────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        btn_queue = st.button(t("btn_queue", L), use_container_width=True, type="primary")
    with c2:
        btn_skip = st.button(t("btn_skip", L), use_container_width=True)
    with c3:
        btn_prev = st.button(t("btn_prev", L), use_container_width=True, disabled=(cursor <= 0))
    with c4:
        btn_next = st.button(t("btn_next", L), use_container_width=True, disabled=(cursor >= len(history) - 1))

    # ── 동작 ──────────────────────────────────────
    if btn_queue or btn_skip:
        shuf = st.session_state.get("_shuffle", True)
        q, history, cursor, deck = draw_next(deck, history, cursor if history else -1, shuffle=shuf)
        if q is None and not deck and history:
            st.toast(t("deck_exhausted", L), icon="ℹ️")
        st.session_state.ib_deck = deck
        st.session_state.ib_history = history
        st.session_state.ib_cursor = cursor
        st.session_state.ib_current = q
        st.rerun()

    if btn_prev:
        q, cursor = history_prev(history, cursor)
        st.session_state.ib_cursor = cursor
        st.session_state.ib_current = q
        st.rerun()

    if btn_next:
        q, cursor = history_next(history, cursor)
        st.session_state.ib_cursor = cursor
        st.session_state.ib_current = q
        st.rerun()

    # ── 질문 카드 ─────────────────────────────────
    current = st.session_state.ib_current
    if current:
        primary, secondary = format_question(current, display_mode)
        counter = f"{st.session_state.ib_cursor + 1} / {len(st.session_state.ib_history)}"
        cat = current.get("category", "")
        st.markdown(question_card_html(primary, secondary, counter=counter, category=cat), unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="q-card"><span class="q-main" style="color:#666;">{t("queue_prompt", L)}</span></div>',
            unsafe_allow_html=True,
        )

    # ── 히스토리 ──────────────────────────────────
    if history:
        with st.expander(t("history_title", L, n=len(history)), expanded=False):
            for i, h in enumerate(history):
                marker = "👉 " if i == st.session_state.ib_cursor else ""
                st.write(f"{marker}**{i+1}.** {h.get('ko', '')} / {h.get('en', '')}")


# ═══════════════════════════════════════════════════════════
#  메인 – 스피드게임
# ═══════════════════════════════════════════════════════════
elif mode == "speedgame":
    st.markdown('<div class="app-title">Qnnection ⚡</div>', unsafe_allow_html=True)

    # ── 덱 구축 / 초기화 ──────────────────────────
    col_build, col_reset, _ = st.columns([1, 1, 3])
    with col_build:
        if st.button(t("btn_build", L), use_container_width=True):
            reset_speed()
            _build_fresh_deck("sp")
            st.rerun()
    with col_reset:
        if st.button(t("btn_reset", L), use_container_width=True):
            reset_speed()
            _build_fresh_deck("sp")
            st.rerun()

    if not st.session_state.sp_deck_built:
        _build_fresh_deck("sp")

    deck = st.session_state.sp_deck
    running = st.session_state.sp_running
    paused = st.session_state.sp_paused
    finished = st.session_state.sp_finished
    score = st.session_state.sp_score
    timer_sec = st.session_state.sp_timer_seconds

    # ── 타이머 ────────────────────────────────────
    remaining = timer_sec
    if running and not paused and st.session_state.sp_start_ts:
        elapsed = time.time() - st.session_state.sp_start_ts + st.session_state.sp_pause_elapsed
        remaining = max(0, timer_sec - elapsed)
        if remaining <= 0:
            st.session_state.sp_running = False
            st.session_state.sp_finished = True
            running = False
            finished = True
            remaining = 0

    if remaining > timer_sec * 0.5:
        timer_cls = "timer-green"
    elif remaining > timer_sec * 0.2:
        timer_cls = "timer-yellow"
    else:
        timer_cls = "timer-red"

    st.markdown(f'<div class="timer-display {timer_cls}">{int(remaining)}s</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="score-board">🎯 {score} (✅ {st.session_state.sp_correct} / ❌ {st.session_state.sp_pass})</div>', unsafe_allow_html=True)

    # ── 컨트롤 ────────────────────────────────────
    if not finished:
        if not running:
            c1, c2 = st.columns(2)
            with c1:
                if st.button(t("btn_start", L), use_container_width=True, type="primary"):
                    st.session_state.sp_running = True
                    st.session_state.sp_paused = False
                    st.session_state.sp_start_ts = time.time()
                    st.session_state.sp_pause_elapsed = 0.0
                    if deck and st.session_state.sp_current is None:
                        shuf = st.session_state.get("_shuffle", True)
                        if shuf:
                            import random
                            idx = random.randint(0, len(deck) - 1)
                            st.session_state.sp_current = deck.pop(idx)
                        else:
                            st.session_state.sp_current = deck.pop(0)
                        st.session_state.sp_deck = deck
                    st.rerun()
        else:
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                if not paused:
                    if st.button(t("btn_pause", L), use_container_width=True):
                        st.session_state.sp_paused = True
                        elapsed = time.time() - st.session_state.sp_start_ts
                        st.session_state.sp_pause_elapsed += elapsed
                        st.session_state.sp_start_ts = None
                        st.rerun()
                else:
                    if st.button(t("btn_resume", L), use_container_width=True, type="primary"):
                        st.session_state.sp_paused = False
                        st.session_state.sp_start_ts = time.time()
                        st.rerun()
            with c2:
                if st.button(t("btn_stop", L), use_container_width=True):
                    st.session_state.sp_running = False
                    st.session_state.sp_finished = True
                    st.rerun()
            with c3:
                if st.button(t("btn_correct", L), use_container_width=True, type="primary", disabled=paused):
                    cur = st.session_state.sp_current
                    if cur:
                        evt = SpeedEvent(action="correct", question=cur, score_delta=1)
                        st.session_state.sp_event_stack = push_event(st.session_state.sp_event_stack, evt)
                        st.session_state.sp_round_history.append(evt)
                        st.session_state.sp_score += 1
                        st.session_state.sp_correct += 1
                        if deck:
                            shuf = st.session_state.get("_shuffle", True)
                            if shuf:
                                import random
                                idx = random.randint(0, len(deck) - 1)
                                st.session_state.sp_current = deck.pop(idx)
                            else:
                                st.session_state.sp_current = deck.pop(0)
                            st.session_state.sp_deck = deck
                        else:
                            st.session_state.sp_current = None
                    st.rerun()
            with c4:
                if st.button(t("btn_pass", L), use_container_width=True, disabled=paused):
                    cur = st.session_state.sp_current
                    if cur:
                        evt = SpeedEvent(action="pass", question=cur, score_delta=0)
                        st.session_state.sp_event_stack = push_event(st.session_state.sp_event_stack, evt)
                        st.session_state.sp_round_history.append(evt)
                        st.session_state.sp_pass += 1
                        if deck:
                            shuf = st.session_state.get("_shuffle", True)
                            if shuf:
                                import random
                                idx = random.randint(0, len(deck) - 1)
                                st.session_state.sp_current = deck.pop(idx)
                            else:
                                st.session_state.sp_current = deck.pop(0)
                            st.session_state.sp_deck = deck
                        else:
                            st.session_state.sp_current = None
                    st.rerun()
            with c5:
                if st.button(t("btn_undo", L), use_container_width=True, disabled=paused):
                    popped, stack = undo_event(st.session_state.sp_event_stack)
                    if popped:
                        st.session_state.sp_event_stack = stack
                        st.session_state.sp_score -= popped.score_delta
                        if popped.action == "correct":
                            st.session_state.sp_correct -= 1
                        else:
                            st.session_state.sp_pass -= 1
                        if st.session_state.sp_current:
                            st.session_state.sp_deck.insert(0, st.session_state.sp_current)
                        st.session_state.sp_current = popped.question
                        if st.session_state.sp_round_history:
                            st.session_state.sp_round_history.pop()
                    st.rerun()

    # ── 현재 카드 ─────────────────────────────────
    cur = st.session_state.sp_current
    if cur and not finished:
        primary, secondary = format_question(cur, display_mode)
        st.markdown(question_card_html(primary, secondary), unsafe_allow_html=True)
    elif not finished:
        st.markdown(
            f'<div class="q-card"><span class="q-main" style="color:#666;">{t("start_prompt", L)}</span></div>',
            unsafe_allow_html=True,
        )

    # ── 라운드 결과 ───────────────────────────────
    if finished:
        st.markdown("---")
        st.markdown(t("round_result", L))
        st.markdown(
            f'<div class="score-board" style="font-size:3rem;">{t("final_score", L, score=st.session_state.sp_score)}</div>',
            unsafe_allow_html=True,
        )
        rc = st.session_state.sp_correct
        rp = st.session_state.sp_pass
        st.markdown(t("result_summary", L, c=rc, p=rp, t=rc + rp))

        if st.session_state.sp_round_history:
            st.markdown(t("used_cards", L))
            rows = ""
            for i, evt in enumerate(st.session_state.sp_round_history, 1):
                q = evt.question
                cls = "result-correct" if evt.action == "correct" else "result-pass"
                icon = "✅" if evt.action == "correct" else "❌"
                rows += f'<tr><td>{i}</td><td>{q.get("ko","")}</td><td>{q.get("en","")}</td><td class="{cls}">{icon}</td></tr>'
            st.markdown(
                f'<table class="result-table"><thead><tr><th>{t("table_no",L)}</th><th>{t("table_ko",L)}</th><th>{t("table_en",L)}</th><th>{t("table_result",L)}</th></tr></thead><tbody>{rows}</tbody></table>',
                unsafe_allow_html=True,
            )

    # 타이머 자동 갱신
    if running and not paused and not finished:
        time.sleep(0.3)
        st.rerun()