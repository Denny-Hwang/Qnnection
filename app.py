"""Qnnection – Question + Connection
교회 모임 아이스브레이킹 & 스피드게임 TV 앱.
"""

from __future__ import annotations

import random
import time
from pathlib import Path

import pandas as pd
import streamlit as st

from core.components import (
    install_keyboard_shortcuts,
    play_sound,
    render_running_timer,
)
from core.deck import (
    SpeedEvent,
    build_deck,
    draw_next,
    history_prev,
    pop_next,
    push_event,
    undo_event,
)
from core.filtering import (
    Filters,
    apply_filters,
    get_unique_categories,
    get_unique_tags,
)
from core.i18n import category_label, t
from core.loader import load_and_prepare, scan_sets
from core.state import (
    has_icebreaker_progress,
    has_speed_progress,
    init_state,
    reset_icebreaker,
    reset_speed,
)
from core.ui_styles import (
    GLOBAL_CSS,
    empty_card_html,
    format_question,
    question_card_html,
    safe,
    score_board_html,
)

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

# ── PWA 메타태그 ────────────────────────────────────────
st.markdown(
    """
    <link rel="manifest" href="app/static/manifest.json">
    <link rel="apple-touch-icon" href="app/static/icon.svg">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Qnnection">
    <meta name="theme-color" content="#FF6B6B">
    """,
    unsafe_allow_html=True,
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
init_state()
install_keyboard_shortcuts()


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

    # ── 모드 선택 (확인 다이얼로그 지원) ─────────────
    mode_options = ["icebreaker", "speedgame"]
    mode_labels = [t("mode_icebreaker", L), t("mode_speedgame", L)]

    if "current_mode" not in st.session_state:
        st.session_state.current_mode = "icebreaker"

    # 언어 변경 등으로 라벨이 어긋났으면 동기화
    expected_label = mode_labels[mode_options.index(st.session_state.current_mode)]
    if st.session_state.get("_mode_radio") not in mode_labels:
        st.session_state._mode_radio = expected_label

    def _on_mode_change():
        new_label = st.session_state._mode_radio
        new_mode = mode_options[mode_labels.index(new_label)]
        if new_mode == st.session_state.current_mode:
            return
        cur = st.session_state.current_mode
        has_prog = (
            (cur == "icebreaker" and has_icebreaker_progress())
            or (cur == "speedgame" and has_speed_progress())
        )
        if has_prog:
            # 라디오 값 원복 + pending 설정 → 메인에서 확인
            st.session_state._pending_mode = new_mode
            st.session_state._mode_radio = mode_labels[mode_options.index(cur)]
        else:
            st.session_state.current_mode = new_mode

    st.radio(
        t("mode_label", L),
        mode_labels,
        horizontal=True,
        key="_mode_radio",
        on_change=_on_mode_change,
    )
    mode = st.session_state.current_mode

    # ── 세트 스캔/로드 ─────────────────────────────
    deck_dir = DECK_DIRS[mode]
    set_metas = scan_sets(str(deck_dir))

    if not set_metas:
        st.warning(t("no_csv", L))
        st.stop()

    valid_sets = [m for m in set_metas if m.valid]
    invalid_sets = [m for m in set_metas if not m.valid]

    if invalid_sets:
        with st.expander(f"{t('load_fail_title', L)} ({len(invalid_sets)})", expanded=False):
            for m in invalid_sets:
                st.error(f"**{safe(m.name)}**: {safe('; '.join(m.errors))}")

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

    @st.cache_data(show_spinner=False)
    def _load_sets(paths_names: tuple) -> pd.DataFrame:
        frames = []
        for path, name in paths_names:
            df = load_and_prepare(path, set_name=name)
            if df is not None:
                frames.append(df)
        if frames:
            return pd.concat(frames, ignore_index=True)
        return pd.DataFrame()

    paths_names = tuple((m.path, m.name) for m in valid_sets if m.name in selected)
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

    raw_cats = get_unique_categories(pool_all)
    cat_options = sorted(raw_cats, key=lambda c: category_label(c, L))
    sel_cats = st.multiselect(
        t("filter_category", L),
        cat_options,
        default=[],
        format_func=lambda c: category_label(c, L),
        key="_filter_cats",
    )
    depth_range = st.slider(
        t("filter_depth", L), 1, 5, (1, 5),
        help=t("filter_depth_help", L), key="_filter_depth",
    )

    diff_range = (1, 3)
    if mode == "speedgame":
        diff_range = st.slider(
            t("filter_difficulty", L), 1, 3, (1, 3),
            help=t("filter_difficulty_help", L), key="_filter_diff",
        )

    tags_all = get_unique_tags(pool_all)
    sel_tags = st.multiselect(
        t("filter_tags", L), tags_all, default=[], key="_filter_tags",
    )

    filters = Filters(
        categories=sel_cats,
        depth_min=depth_range[0], depth_max=depth_range[1],
        difficulty_min=diff_range[0], difficulty_max=diff_range[1],
        tags_include=sel_tags,
    )
    pool_filtered = apply_filters(pool_all, filters)
    max_pool = len(pool_filtered)
    st.caption(t("pool_count", L, n=max_pool))

    if max_pool == 0:
        st.warning(t("filter_empty", L))
        if st.button(t("filter_reset", L), use_container_width=True, key="_filter_reset_btn"):
            st.session_state._filter_cats = []
            st.session_state._filter_depth = (1, 5)
            if "_filter_diff" in st.session_state:
                st.session_state._filter_diff = (1, 3)
            st.session_state._filter_tags = []
            st.rerun()
        st.stop()

    deck_size = st.number_input(
        t("deck_size", L), min_value=0, max_value=max_pool,
        value=0 if max_pool <= 50 else 20, step=1, key="deck_size",
    )
    shuffle_on = st.toggle(t("shuffle_toggle", L), value=True, key="_shuffle")
    st.toggle(t("sound_toggle", L), value=True, key="sound_on")

    if mode == "speedgame":
        st.divider()
        st.subheader(t("timer_title", L))
        timer_preset = st.radio(
            t("timer_preset", L), [30, 60, 90], index=1, horizontal=True, key="_timer_preset",
        )
        if "_prev_timer_preset" not in st.session_state:
            st.session_state._prev_timer_preset = timer_preset
        if timer_preset != st.session_state._prev_timer_preset:
            st.session_state.sp_timer_seconds = timer_preset
            st.session_state._prev_timer_preset = timer_preset
        st.number_input(
            t("timer_custom", L), min_value=10, max_value=300,
            value=timer_preset, step=5, key="sp_timer_seconds",
        )

    # ── 단축키 안내 ────────────────────────────────
    st.divider()
    with st.expander(t("shortcuts_title", L), expanded=False):
        body_key = "shortcuts_body_icebreaker" if mode == "icebreaker" else "shortcuts_body_speedgame"
        st.caption(t(body_key, L))


# ═══════════════════════════════════════════════════════════
#  모드 전환 확인 (메인 영역)
# ═══════════════════════════════════════════════════════════
if st.session_state.get("_pending_mode"):
    st.warning(t("mode_switch_warning", L))
    c1, c2, _ = st.columns([1, 1, 3])
    with c1:
        if st.button(t("btn_confirm_switch", L), type="primary", use_container_width=True, key="_confirm_switch"):
            new_mode = st.session_state._pending_mode
            reset_icebreaker()
            reset_speed()
            st.session_state.current_mode = new_mode
            st.session_state._mode_radio = mode_labels[mode_options.index(new_mode)]
            st.session_state._pending_mode = None
            st.rerun()
    with c2:
        if st.button(t("btn_cancel_switch", L), use_container_width=True, key="_cancel_switch"):
            st.session_state._pending_mode = None
            st.rerun()
    st.stop()


# ═══════════════════════════════════════════════════════════
#  헬퍼
# ═══════════════════════════════════════════════════════════
def _build_fresh_deck(prefix: str) -> None:
    """pool_filtered로 새 덱 생성. shuffle 옵션 반영."""
    ds = st.session_state.deck_size or 0
    shuf = st.session_state.get("_shuffle", True)
    deck = build_deck(pool_filtered, deck_size=ds, shuffle=shuf)
    st.session_state[f"{prefix}_deck"] = deck
    st.session_state[f"{prefix}_deck_built"] = True


def _shuffle_remaining(prefix: str) -> None:
    """남은 덱만 재셔플 (히스토리/현재 카드 보존)."""
    deck = st.session_state[f"{prefix}_deck"]
    if deck:
        random.shuffle(deck)
        st.session_state[f"{prefix}_deck"] = deck


# ═══════════════════════════════════════════════════════════
#  메인 – 아이스브레이킹
# ═══════════════════════════════════════════════════════════
if mode == "icebreaker":
    st.markdown('<div class="app-title">Qnnection</div>', unsafe_allow_html=True)

    # ── 덱 셔플 / 초기화 ──────────────────────────
    col_shuf, col_reset, _ = st.columns([1, 1, 3])
    with col_shuf:
        if st.button(t("btn_shuffle", L), use_container_width=True, key="_ib_shuffle"):
            _shuffle_remaining("ib")
            st.rerun()
    with col_reset:
        if st.button(t("btn_reset", L), use_container_width=True, key="_ib_reset"):
            reset_icebreaker()
            _build_fresh_deck("ib")
            st.rerun()

    if not st.session_state.ib_deck_built:
        _build_fresh_deck("ib")

    deck = st.session_state.ib_deck
    history = st.session_state.ib_history
    cursor = st.session_state.ib_cursor

    st.caption(t("remaining_cards", L, remain=len(deck), used=len(history)))

    # ── Prev / Next 컨트롤 ─────────────────────────
    c1, c2, _, _ = st.columns(4)
    with c1:
        btn_prev = st.button(
            t("btn_prev", L),
            use_container_width=True,
            disabled=(cursor <= 0),
            key="_ib_prev",
        )
    with c2:
        # 끝에서 덱이 비었으면 비활성
        next_disabled = (cursor >= len(history) - 1) and (not deck)
        btn_next = st.button(
            t("btn_next", L),
            type="primary",
            use_container_width=True,
            disabled=next_disabled,
            key="_ib_next",
        )

    if btn_next:
        shuf = st.session_state.get("_shuffle", True)
        q, history, cursor, deck = draw_next(
            deck, history, cursor if history else -1, shuffle=shuf,
        )
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

    # ── 카드 영역 ─────────────────────────────────
    current = st.session_state.ib_current
    if current:
        primary, secondary = format_question(current, display_mode)
        counter = f"{st.session_state.ib_cursor + 1} / {len(st.session_state.ib_history)}"
        cat = category_label(current.get("category", ""), L)
        st.markdown(
            question_card_html(primary, secondary, counter=counter, category=cat),
            unsafe_allow_html=True,
        )
    elif not deck and history:
        # 덱 소진 – 영구 알림 (toast 대체)
        st.markdown(empty_card_html(t("deck_exhausted", L)), unsafe_allow_html=True)
    else:
        st.markdown(empty_card_html(t("queue_prompt", L)), unsafe_allow_html=True)

    # ── 히스토리 + 내보내기 ──────────────────────
    if history:
        with st.expander(t("history_title", L, n=len(history)), expanded=False):
            for i, h in enumerate(history):
                marker = "👉 " if i == st.session_state.ib_cursor else ""
                st.markdown(f"{marker}**{i+1}.** {safe(h.get('ko', ''))} / {safe(h.get('en', ''))}")
            df_hist = pd.DataFrame(history)
            st.download_button(
                t("history_export", L),
                df_hist.to_csv(index=False).encode("utf-8-sig"),
                file_name="qnnection_history.csv",
                mime="text/csv",
                key="_ib_history_dl",
            )


# ═══════════════════════════════════════════════════════════
#  메인 – 스피드게임
# ═══════════════════════════════════════════════════════════
elif mode == "speedgame":
    st.markdown('<div class="app-title">Qnnection ⚡</div>', unsafe_allow_html=True)

    running_now = st.session_state.sp_running

    # ── 덱 셔플 / 초기화 (러닝 중 비활성) ───────────
    col_shuf, col_reset, _ = st.columns([1, 1, 3])
    with col_shuf:
        if st.button(t("btn_shuffle", L), use_container_width=True,
                     disabled=running_now, key="_sp_shuffle"):
            reset_speed()
            _build_fresh_deck("sp")
            st.rerun()
    with col_reset:
        if st.button(t("btn_reset", L), use_container_width=True,
                     disabled=running_now, key="_sp_reset"):
            reset_speed()
            _build_fresh_deck("sp")
            st.rerun()

    if not st.session_state.sp_deck_built:
        _build_fresh_deck("sp")

    deck = st.session_state.sp_deck
    running = st.session_state.sp_running
    paused = st.session_state.sp_paused
    finished = st.session_state.sp_finished
    timer_sec = float(st.session_state.sp_timer_seconds)

    # ── 타이머 계산 (server-side, monotonic) ─────────
    remaining = timer_sec
    just_finished = False
    if running and not paused and st.session_state.sp_start_mono is not None:
        elapsed = (
            (time.monotonic() - st.session_state.sp_start_mono)
            + st.session_state.sp_pause_elapsed
        )
        remaining = max(0.0, timer_sec - elapsed)
        if remaining <= 0:
            st.session_state.sp_running = False
            st.session_state.sp_finished = True
            running = False
            finished = True
            remaining = 0.0
            just_finished = True
    if just_finished:
        play_sound("finish")

    # ── 타이머 표시 ───────────────────────────────
    if running and not paused and st.session_state.sp_start_wall is not None:
        # 클라이언트 측 부드러운 카운트다운
        render_running_timer(
            start_epoch=st.session_state.sp_start_wall,
            initial_remaining=timer_sec - st.session_state.sp_pause_elapsed,
            total=timer_sec,
            uid=f"r{int(st.session_state.sp_start_wall * 1000) & 0xFFFFFFF}",
        )
    else:
        if remaining > timer_sec * 0.5:
            cls = "timer-green"
        elif remaining > timer_sec * 0.2:
            cls = "timer-yellow"
        else:
            cls = "timer-red"
        st.markdown(
            f'<div class="timer-display {cls}">{int(remaining)}s</div>',
            unsafe_allow_html=True,
        )
        pct = max(0.0, min(100.0, (remaining / timer_sec * 100) if timer_sec else 0))
        bar_color = "#4ECDC4" if pct > 50 else ("#FFE66D" if pct > 20 else "#FF6B6B")
        st.markdown(
            f'<div class="timer-bar" role="progressbar">'
            f'<div class="timer-bar-fill" style="width:{pct:.1f}%;background:{bar_color};"></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── 스코어 보드 ───────────────────────────────
    st.markdown(
        score_board_html(
            score=st.session_state.sp_score,
            correct=st.session_state.sp_correct,
            passed=st.session_state.sp_pass,
            label_correct="✅",
            label_pass="❌",
        ),
        unsafe_allow_html=True,
    )

    # ── 컨트롤 ────────────────────────────────────
    if not finished:
        shuf = st.session_state.get("_shuffle", True)

        if not running:
            c1, _ = st.columns([1, 4])
            with c1:
                if st.button(t("btn_start", L), use_container_width=True,
                             type="primary", key="_sp_start"):
                    st.session_state.sp_running = True
                    st.session_state.sp_paused = False
                    st.session_state.sp_start_mono = time.monotonic()
                    st.session_state.sp_start_wall = time.time()
                    st.session_state.sp_pause_elapsed = 0.0
                    if deck and st.session_state.sp_current is None:
                        st.session_state.sp_current = pop_next(deck, shuffle=shuf)
                        st.session_state.sp_deck = deck
                    play_sound("start")
                    st.rerun()
        else:
            # 주요 액션: Correct / Pass (모바일에서 큰 행)
            c_corr, c_pass = st.columns(2)
            with c_corr:
                if st.button(t("btn_correct", L), use_container_width=True,
                             type="primary", disabled=paused, key="_sp_correct"):
                    cur = st.session_state.sp_current
                    if cur:
                        evt = SpeedEvent(action="correct", question=cur, score_delta=1)
                        st.session_state.sp_event_stack = push_event(
                            st.session_state.sp_event_stack, evt,
                        )
                        st.session_state.sp_round_history.append(evt)
                        st.session_state.sp_score += 1
                        st.session_state.sp_correct += 1
                        st.session_state.sp_last_action = "correct"
                        st.session_state.sp_current = pop_next(deck, shuffle=shuf)
                        st.session_state.sp_deck = deck
                        play_sound("correct")
                    st.rerun()
            with c_pass:
                if st.button(t("btn_pass", L), use_container_width=True,
                             disabled=paused, key="_sp_pass"):
                    cur = st.session_state.sp_current
                    if cur:
                        evt = SpeedEvent(action="pass", question=cur, score_delta=0)
                        st.session_state.sp_event_stack = push_event(
                            st.session_state.sp_event_stack, evt,
                        )
                        st.session_state.sp_round_history.append(evt)
                        st.session_state.sp_pass += 1
                        st.session_state.sp_last_action = "pass"
                        st.session_state.sp_current = pop_next(deck, shuffle=shuf)
                        st.session_state.sp_deck = deck
                        play_sound("pass")
                    st.rerun()

            # 보조 액션: Pause / Undo / Stop (작은 행)
            c_pause, c_undo, c_stop = st.columns(3)
            with c_pause:
                if not paused:
                    if st.button(t("btn_pause", L), use_container_width=True, key="_sp_pause"):
                        st.session_state.sp_paused = True
                        if st.session_state.sp_start_mono is not None:
                            st.session_state.sp_pause_elapsed += (
                                time.monotonic() - st.session_state.sp_start_mono
                            )
                        st.session_state.sp_start_mono = None
                        st.session_state.sp_start_wall = None
                        st.rerun()
                else:
                    if st.button(t("btn_resume", L), use_container_width=True,
                                 type="primary", key="_sp_resume"):
                        st.session_state.sp_paused = False
                        st.session_state.sp_start_mono = time.monotonic()
                        st.session_state.sp_start_wall = time.time()
                        st.rerun()
            with c_undo:
                if st.button(t("btn_undo", L), use_container_width=True,
                             disabled=paused, key="_sp_undo"):
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
            with c_stop:
                if st.button(t("btn_stop", L), use_container_width=True, key="_sp_stop"):
                    st.session_state.sp_running = False
                    st.session_state.sp_finished = True
                    play_sound("finish")
                    st.rerun()

    # ── 현재 카드 ─────────────────────────────────
    cur = st.session_state.sp_current
    if cur and not finished:
        primary, secondary = format_question(cur, display_mode)
        flash = (
            st.session_state.sp_last_action
            if st.session_state.sp_last_action in ("correct", "pass")
            else ""
        )
        paused_label = t("paused_overlay", L) if paused else ""
        cat = category_label(cur.get("category", ""), L)
        st.markdown(
            question_card_html(
                primary, secondary,
                category=cat, flash=flash, paused_label=paused_label,
            ),
            unsafe_allow_html=True,
        )
        # 다음 렌더에선 플래시 제거
        if flash:
            st.session_state.sp_last_action = ""
    elif not finished:
        st.markdown(empty_card_html(t("start_prompt", L)), unsafe_allow_html=True)

    # ── 라운드 결과 ───────────────────────────────
    if finished:
        st.markdown("---")
        st.markdown(t("round_result", L))
        st.markdown(
            '<div class="score-board">'
            f'<span class="score-main">🎯 {safe(st.session_state.sp_score)}</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        rc = st.session_state.sp_correct
        rp = st.session_state.sp_pass
        st.markdown(t("result_summary", L, c=rc, p=rp, t=rc + rp))

        c_again, _, _ = st.columns([1, 1, 3])
        with c_again:
            if st.button(t("btn_play_again", L), type="primary",
                         use_container_width=True, key="_sp_play_again"):
                reset_speed()
                _build_fresh_deck("sp")
                st.rerun()

        if st.session_state.sp_round_history:
            st.markdown(t("used_cards", L))
            rows = ""
            for i, evt in enumerate(st.session_state.sp_round_history, 1):
                q = evt.question
                cls = "result-correct" if evt.action == "correct" else "result-pass"
                icon = "✅" if evt.action == "correct" else "❌"
                rows += (
                    f"<tr><td>{i}</td>"
                    f"<td>{safe(q.get('ko',''))}</td>"
                    f"<td>{safe(q.get('en',''))}</td>"
                    f'<td class="{cls}">{icon}</td></tr>'
                )
            st.markdown(
                '<table class="result-table"><thead><tr>'
                f"<th>{safe(t('table_no', L))}</th>"
                f"<th>{safe(t('table_ko', L))}</th>"
                f"<th>{safe(t('table_en', L))}</th>"
                f"<th>{safe(t('table_result', L))}</th>"
                f"</tr></thead><tbody>{rows}</tbody></table>",
                unsafe_allow_html=True,
            )
            df_round = pd.DataFrame(
                [
                    {
                        "id": evt.question.get("id", ""),
                        "ko": evt.question.get("ko", ""),
                        "en": evt.question.get("en", ""),
                        "action": evt.action,
                    }
                    for evt in st.session_state.sp_round_history
                ]
            )
            st.download_button(
                t("history_export", L),
                df_round.to_csv(index=False).encode("utf-8-sig"),
                file_name="qnnection_round.csv",
                mime="text/csv",
                key="_sp_round_dl",
            )

    # ── 서버 타임아웃 폴링 (1초 — 버튼 흡수 최소화) ──
    if st.session_state.sp_running and not st.session_state.sp_paused and not st.session_state.sp_finished:
        time.sleep(1.0)
        st.rerun()
