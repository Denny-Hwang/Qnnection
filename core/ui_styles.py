from __future__ import annotations
"""core/ui_styles.py – 프로젝터 최적화 CSS & 스타일 유틸."""

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

.q-card {
    font-family: 'Noto Sans KR', sans-serif;
    background: linear-gradient(145deg, #1e2028, #262a34);
    border: 1px solid rgba(255,255,255,0.06); border-radius: 1.5rem;
    padding: 3rem 2rem; text-align: center; margin: 1rem 0;
    min-height: 50vh; display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3); position: relative;
}
.q-main {
    font-size: clamp(1.8rem, 5vw, 4rem); font-weight: 900;
    color: #FAFAFA; line-height: 1.5; word-break: keep-all;
}
.q-sub {
    font-size: clamp(1rem, 2.5vw, 2rem); color: #999;
    margin-top: 1.5rem; line-height: 1.4; word-break: keep-all;
}
.q-counter {
    position: absolute; top: 1.2rem; right: 1.5rem;
    font-size: 1rem; color: #666;
}
.q-category {
    position: absolute; top: 1.2rem; left: 1.5rem;
    font-size: 0.9rem; color: #888;
    background: rgba(255,255,255,0.08); padding: 0.2rem 0.7rem; border-radius: 1rem;
}

.timer-display {
    font-family: 'Noto Sans KR', monospace;
    font-size: clamp(3rem, 8vw, 7rem); font-weight: 900;
    text-align: center; margin: 0.5rem 0;
}
.timer-green { color: #4ECDC4; }
.timer-yellow { color: #FFE66D; }
.timer-red { color: #FF6B6B; animation: pulse 0.5s infinite alternate; }
@keyframes pulse { from { opacity: 1; } to { opacity: 0.5; } }

.score-board {
    font-family: 'Noto Sans KR', sans-serif;
    font-size: 2.5rem; font-weight: 900;
    text-align: center; color: #FFE66D; margin: 0.5rem 0;
}

div.stButton > button {
    font-family: 'Noto Sans KR', sans-serif; font-weight: 700;
    font-size: 1.1rem; border-radius: 0.75rem;
    padding: 0.5rem 1.5rem; transition: transform 0.1s;
}
div.stButton > button:active { transform: scale(0.96); }

.result-table { width: 100%; border-collapse: collapse; font-family: 'Noto Sans KR', sans-serif; }
.result-table th, .result-table td { padding: 0.5rem 1rem; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
.result-table th { color: #FFE66D; font-weight: 700; }
.result-correct { color: #4ECDC4; }
.result-pass { color: #FF6B6B; }
</style>
"""


def format_question(q: dict, display_mode: str) -> tuple[str, str]:
    """display_mode에 따라 (primary_text, secondary_text) 반환."""
    ko = q.get("ko", "")
    en = q.get("en", "")
    if display_mode == "KO only":
        return ko, ""
    elif display_mode == "EN only":
        return en, ""
    elif display_mode == "KO → EN":
        return ko, en
    elif display_mode == "EN → KO":
        return en, ko
    return ko, en


def question_card_html(
    primary: str, secondary: str = "", counter: str = "", category: str = ""
) -> str:
    """프로젝터 최적화 인라인 카드 HTML. 한 줄로 생성해 Streamlit 렌더링 호환."""
    parts = ['<div class="q-card">']
    if category:
        parts.append(f'<span class="q-category">{category}</span>')
    if counter:
        parts.append(f'<span class="q-counter">{counter}</span>')
    parts.append(f'<span class="q-main">{primary}</span>')
    if secondary:
        parts.append(f'<span class="q-sub">{secondary}</span>')
    parts.append("</div>")
    return "".join(parts)