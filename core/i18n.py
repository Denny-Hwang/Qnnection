"""core/i18n.py – 한/영 UI 번역."""

from __future__ import annotations

TEXTS = {
    # ── 공통 ──────────────────────────────────────
    "app_subtitle": {
        "ko": "Question + Connection 💬",
        "en": "Question + Connection 💬",
    },
    "mode_label": {
        "ko": "모드 선택",
        "en": "Select Mode",
    },
    "mode_icebreaker": {
        "ko": "아이스브레이킹",
        "en": "Icebreaker",
    },
    "mode_speedgame": {
        "ko": "스피드게임",
        "en": "Speed Game",
    },
    "no_csv": {
        "ko": "📂 덱 폴더에 CSV를 추가하세요.",
        "en": "📂 Please add CSV files to the deck folder.",
    },
    "load_fail_title": {
        "ko": "⚠️ 로드 실패 세트",
        "en": "⚠️ Failed Sets",
    },
    "no_valid_sets": {
        "ko": "사용 가능한 세트가 없습니다.",
        "en": "No valid sets available.",
    },
    "select_sets": {
        "ko": "질문 세트",
        "en": "Question Sets",
    },
    "select_sets_hint": {
        "ko": "세트를 1개 이상 선택하세요.",
        "en": "Please select at least one set.",
    },
    "load_empty": {
        "ko": "선택한 세트에서 질문을 로드할 수 없습니다.",
        "en": "Could not load questions from selected sets.",
    },
    "display_lang": {
        "ko": "질문 표시 언어",
        "en": "Question Display Language",
    },
    "filter_title": {
        "ko": "🔍 필터",
        "en": "🔍 Filters",
    },
    "filter_category": {
        "ko": "카테고리",
        "en": "Category",
    },
    "filter_depth": {
        "ko": "깊이 (depth)",
        "en": "Depth",
    },
    "filter_difficulty": {
        "ko": "난이도 (difficulty)",
        "en": "Difficulty",
    },
    "filter_tags": {
        "ko": "태그",
        "en": "Tags",
    },
    "pool_count": {
        "ko": "필터 적용 후 질문 수: **{n}**개",
        "en": "Questions after filter: **{n}**",
    },
    "filter_empty": {
        "ko": "필터 조건에 맞는 질문이 없습니다. 필터를 완화하세요.",
        "en": "No questions match the filters. Try loosening the criteria.",
    },
    "deck_size": {
        "ko": "덱 크기 (0 = 전체)",
        "en": "Deck Size (0 = all)",
    },
    "shuffle_toggle": {
        "ko": "🔀 랜덤 순서",
        "en": "🔀 Shuffle",
    },
    "ui_lang": {
        "ko": "🌐 UI 언어",
        "en": "🌐 UI Language",
    },

    # ── 아이스브레이킹 ───────────────────────────
    "btn_build": {
        "ko": "🔀 덱 구성 / 셔플",
        "en": "🔀 Build / Shuffle Deck",
    },
    "btn_reset": {
        "ko": "🗑 초기화",
        "en": "🗑 Reset",
    },
    "remaining_cards": {
        "ko": "🃏 남은 카드: {remain} | 사용: {used}",
        "en": "🃏 Remaining: {remain} | Used: {used}",
    },
    "btn_queue": {
        "ko": "▶️ Queue",
        "en": "▶️ Queue",
    },
    "btn_skip": {
        "ko": "⏭ Skip",
        "en": "⏭ Skip",
    },
    "btn_prev": {
        "ko": "⬅ Prev",
        "en": "⬅ Prev",
    },
    "btn_next": {
        "ko": "➡ Next",
        "en": "➡ Next",
    },
    "deck_exhausted": {
        "ko": "🔄 덱이 소진되었습니다! 셔플 버튼을 눌러 새 덱을 만드세요.",
        "en": "🔄 Deck exhausted! Press shuffle to build a new deck.",
    },
    "queue_prompt": {
        "ko": "▶️ Queue를 눌러 질문을 시작하세요",
        "en": "▶️ Press Queue to start",
    },
    "history_title": {
        "ko": "📋 세션 히스토리 ({n}개)",
        "en": "📋 Session History ({n})",
    },

    # ── 스피드게임 ────────────────────────────────
    "timer_title": {
        "ko": "⏱ 타이머",
        "en": "⏱ Timer",
    },
    "timer_preset": {
        "ko": "프리셋",
        "en": "Preset",
    },
    "timer_custom": {
        "ko": "직접 입력(초)",
        "en": "Custom (sec)",
    },
    "btn_start": {
        "ko": "▶️ Start",
        "en": "▶️ Start",
    },
    "btn_pause": {
        "ko": "⏸ Pause",
        "en": "⏸ Pause",
    },
    "btn_resume": {
        "ko": "▶️ Resume",
        "en": "▶️ Resume",
    },
    "btn_stop": {
        "ko": "⏹ Stop",
        "en": "⏹ Stop",
    },
    "btn_correct": {
        "ko": "✅ 정답 (+1)",
        "en": "✅ Correct (+1)",
    },
    "btn_pass": {
        "ko": "⏭ Pass",
        "en": "⏭ Pass",
    },
    "btn_undo": {
        "ko": "↩ Undo",
        "en": "↩ Undo",
    },
    "start_prompt": {
        "ko": "▶️ Start를 눌러 게임을 시작하세요",
        "en": "▶️ Press Start to begin",
    },
    "round_result": {
        "ko": "## 🏆 라운드 결과",
        "en": "## 🏆 Round Result",
    },
    "final_score": {
        "ko": "최종 점수: {score}점",
        "en": "Final Score: {score}",
    },
    "result_summary": {
        "ko": "**정답** ✅ {c}개 | **패스** ❌ {p}개 | **총 시도** {t}개",
        "en": "**Correct** ✅ {c} | **Pass** ❌ {p} | **Total** {t}",
    },
    "used_cards": {
        "ko": "#### 📋 사용된 카드",
        "en": "#### 📋 Cards Used",
    },
    "table_no": {
        "ko": "#",
        "en": "#",
    },
    "table_ko": {
        "ko": "한국어",
        "en": "Korean",
    },
    "table_en": {
        "ko": "영어",
        "en": "English",
    },
    "table_result": {
        "ko": "결과",
        "en": "Result",
    },
}


def t(key: str, lang: str = "ko", **kwargs) -> str:
    """번역 문자열 반환. kwargs로 포맷 변수 전달."""
    entry = TEXTS.get(key, {})
    text = entry.get(lang, entry.get("ko", key))
    if kwargs:
        text = text.format(**kwargs)
    return text