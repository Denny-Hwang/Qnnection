from __future__ import annotations
"""core/ui_styles.py – 프로젝터 최적화 CSS & 카드 HTML 빌더 (XSS-safe)."""

import html

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');

section[data-testid="stSidebar"] { width: 320px !important; }
.block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 100% !important; }
header[data-testid="stHeader"] { display: none !important; }
#MainMenu, footer { display: none !important; }

.app-title {
    font-family: 'Noto Sans KR', sans-serif; font-weight: 900; font-size: 2rem;
    text-align: center; letter-spacing: 0.15em; margin-bottom: 0.2rem;
    background: linear-gradient(135deg, #FF6B6B, #FFE66D, #4ECDC4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* ── 질문 카드 ─────────────────────────────────── */
.q-card {
    font-family: 'Noto Sans KR', sans-serif;
    background: linear-gradient(145deg, #1e2028, #262a34);
    border: 1px solid rgba(255,255,255,0.06); border-radius: 1.5rem;
    padding: 3rem 2rem; text-align: center; margin: 1rem 0;
    min-height: 50vh; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3); position: relative;
    overflow-wrap: anywhere;
}
.q-card.flash-correct { animation: flashCorrect 0.6s ease-out; }
.q-card.flash-pass { animation: flashPass 0.6s ease-out; }
@keyframes flashCorrect {
    0% { box-shadow: 0 0 0 0 rgba(78,205,196,0.7); border-color: rgba(78,205,196,0.9);}
    50% { box-shadow: 0 0 40px 20px rgba(78,205,196,0.4); border-color: rgba(78,205,196,1);}
    100% { box-shadow: 0 8px 32px rgba(0,0,0,0.3); border-color: rgba(255,255,255,0.06);}
}
@keyframes flashPass {
    0% { box-shadow: 0 0 0 0 rgba(255,107,107,0.7); border-color: rgba(255,107,107,0.9);}
    50% { box-shadow: 0 0 40px 20px rgba(255,107,107,0.3); border-color: rgba(255,107,107,1);}
    100% { box-shadow: 0 8px 32px rgba(0,0,0,0.3); border-color: rgba(255,255,255,0.06);}
}
.q-main {
    font-size: clamp(1.8rem, 5vw, 4rem); font-weight: 900;
    color: #FAFAFA; line-height: 1.5; word-break: keep-all;
    white-space: pre-wrap;
}
.q-sub {
    font-size: clamp(1rem, 2.5vw, 2rem); color: #C8C8C8;
    margin-top: 1.5rem; line-height: 1.4; word-break: keep-all;
    white-space: pre-wrap;
}
.q-counter {
    position: absolute; top: 1.2rem; right: 1.5rem;
    font-size: 1rem; color: #B8B8B8;
    background: rgba(255,255,255,0.05); padding: 0.2rem 0.7rem; border-radius: 1rem;
}
.q-category {
    position: absolute; top: 1.2rem; left: 1.5rem;
    font-size: 0.95rem; color: #FAFAFA;
    background: rgba(78,205,196,0.18); padding: 0.25rem 0.8rem; border-radius: 1rem;
    border: 1px solid rgba(78,205,196,0.35);
}

/* 일시정지 오버레이 */
.paused-overlay {
    position: absolute; inset: 0;
    background: rgba(14,17,23,0.78);
    display: flex; align-items: center; justify-content: center;
    border-radius: 1.5rem; font-weight: 900; letter-spacing: 0.2em;
    font-size: clamp(2.5rem, 6vw, 5rem); color: #FFE66D;
    text-shadow: 0 0 20px rgba(255,230,109,0.6);
}

/* 빈/대기 상태 */
.q-card .empty-prompt {
    color: #C8C8C8;
    font-size: clamp(1.4rem, 3.5vw, 2.2rem);
    font-weight: 700;
}

/* ── 타이머 ───────────────────────────────────── */
.timer-display {
    font-family: 'Noto Sans KR', monospace;
    font-size: clamp(3rem, 8vw, 7rem); font-weight: 900;
    text-align: center; margin: 0.25rem 0;
    font-variant-numeric: tabular-nums;
}
.timer-green { color: #4ECDC4; }
.timer-yellow { color: #FFE66D; }
.timer-red { color: #FF6B6B; animation: pulse 0.5s infinite alternate; }
@keyframes pulse { from { opacity: 1; } to { opacity: 0.5; } }

.timer-bar {
    height: 10px; background: rgba(255,255,255,0.08);
    border-radius: 999px; overflow: hidden; margin: 0.25rem auto 0.5rem;
    max-width: 720px;
}
.timer-bar-fill {
    height: 100%; transition: width 0.25s linear, background-color 0.3s;
    border-radius: 999px;
}

/* ── 스코어 보드 ──────────────────────────────── */
.score-board {
    font-family: 'Noto Sans KR', sans-serif;
    text-align: center; margin: 0.25rem 0 0.5rem;
}
.score-board .score-main {
    display: block;
    font-size: clamp(2.5rem, 7vw, 5rem);
    font-weight: 900; color: #FFE66D;
    line-height: 1.1;
    text-shadow: 0 2px 10px rgba(255,230,109,0.25);
}
.score-board .score-breakdown {
    display: block; margin-top: 0.25rem;
    font-size: clamp(0.9rem, 1.6vw, 1.2rem);
    color: #C8C8C8; font-weight: 600;
}
.score-board .score-correct { color: #4ECDC4; }
.score-board .score-pass { color: #FF6B6B; }

/* ── 버튼 ─────────────────────────────────────── */
div.stButton > button {
    font-family: 'Noto Sans KR', sans-serif; font-weight: 700;
    font-size: 1.05rem; border-radius: 0.75rem;
    padding: 0.55rem 1.4rem; transition: transform 0.08s, box-shadow 0.2s;
    min-height: 2.8rem;
}
div.stButton > button:active { transform: scale(0.96); }
div.stButton > button:focus-visible {
    outline: 3px solid #FFE66D;
    outline-offset: 2px;
}

/* ── 결과 테이블 ─────────────────────────────── */
.result-table { width: 100%; border-collapse: collapse; font-family: 'Noto Sans KR', sans-serif; }
.result-table th, .result-table td { padding: 0.5rem 1rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
.result-table th { color: #FFE66D; font-weight: 700; }
.result-correct { color: #4ECDC4; font-weight: 700; }
.result-pass { color: #FF6B6B; font-weight: 700; }

/* ── 모바일 반응형 ───────────────────────────── */
@media (max-width: 640px) {
    .q-card { padding: 1.5rem 1rem; min-height: 38vh; }
    .q-counter { top: 0.6rem; right: 0.7rem; font-size: 0.85rem; }
    .q-category { top: 0.6rem; left: 0.7rem; font-size: 0.8rem; }
    div.stButton > button { font-size: 0.95rem; padding: 0.5rem 0.6rem; min-height: 2.6rem; }
    .timer-display { font-size: clamp(2.5rem, 16vw, 5rem); }
    .score-board .score-main { font-size: clamp(2rem, 10vw, 4rem); }
}

/* ── 동작 줄임 (vestibular accessibility) ──── */
@media (prefers-reduced-motion: reduce) {
    .timer-red { animation: none !important; }
    .q-card.flash-correct, .q-card.flash-pass { animation: none !important; }
    div.stButton > button { transition: none !important; }
    .timer-bar-fill { transition: none !important; }
}

/* ── Streamlit 토스트 가독성 ─────────────────── */
div[data-testid="stToastContainer"] { z-index: 9999; }
</style>
"""


def safe(text: str | int | float | None) -> str:
    """사용자/CSV 입력을 HTML 안전 문자열로 escape."""
    if text is None:
        return ""
    return html.escape(str(text), quote=True)


def format_question(q: dict, display_mode: str) -> tuple[str, str]:
    """display_mode에 따라 (primary_text, secondary_text) 반환. raw string."""
    ko = q.get("ko", "") or ""
    en = q.get("en", "") or ""
    if display_mode == "KO only":
        return ko, ""
    if display_mode == "EN only":
        return en, ""
    if display_mode == "KO → EN":
        return ko, en
    if display_mode == "EN → KO":
        return en, ko
    return ko, en


def question_card_html(
    primary: str,
    secondary: str = "",
    counter: str = "",
    category: str = "",
    flash: str = "",
    paused_label: str = "",
) -> str:
    """프로젝터 최적화 카드 HTML — 모든 동적 텍스트 escape."""
    classes = ["q-card"]
    if flash == "correct":
        classes.append("flash-correct")
    elif flash == "pass":
        classes.append("flash-pass")

    parts: list[str] = [
        f'<div class="{" ".join(classes)}" role="region" aria-live="polite" aria-atomic="true">'
    ]
    if category:
        parts.append(f'<span class="q-category">{safe(category)}</span>')
    if counter:
        parts.append(f'<span class="q-counter">{safe(counter)}</span>')
    parts.append(f'<span class="q-main">{safe(primary)}</span>')
    if secondary:
        parts.append(f'<span class="q-sub">{safe(secondary)}</span>')
    if paused_label:
        parts.append(f'<div class="paused-overlay" role="status">{safe(paused_label)}</div>')
    parts.append("</div>")
    return "".join(parts)


def empty_card_html(prompt: str) -> str:
    """카드 영역의 빈 상태 표시."""
    return (
        '<div class="q-card" role="region" aria-live="polite">'
        f'<span class="empty-prompt">{safe(prompt)}</span>'
        "</div>"
    )


def score_board_html(score: int, correct: int, passed: int, label_correct: str, label_pass: str) -> str:
    """스피드게임 스코어 보드 HTML (시각 위계 강화)."""
    return (
        '<div class="score-board" role="status" aria-live="polite">'
        f'<span class="score-main">🎯 {safe(score)}</span>'
        '<span class="score-breakdown">'
        f'<span class="score-correct">{safe(label_correct)} {safe(correct)}</span>'
        '&nbsp;&nbsp;|&nbsp;&nbsp;'
        f'<span class="score-pass">{safe(label_pass)} {safe(passed)}</span>'
        '</span>'
        '</div>'
    )


def timer_bar_html(remaining: float, total: float) -> str:
    """타이머 진행 바."""
    pct = max(0.0, min(1.0, remaining / total if total else 0)) * 100
    if pct > 50:
        color = "#4ECDC4"
    elif pct > 20:
        color = "#FFE66D"
    else:
        color = "#FF6B6B"
    return (
        '<div class="timer-bar" role="progressbar" '
        f'aria-valuenow="{int(remaining)}" aria-valuemin="0" aria-valuemax="{int(total)}">'
        f'<div class="timer-bar-fill" style="width:{pct:.1f}%;background:{color};"></div>'
        '</div>'
    )
