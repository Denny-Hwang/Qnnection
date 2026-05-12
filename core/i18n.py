"""core/i18n.py – 한/영 UI 번역."""

from __future__ import annotations

TEXTS = {
    # ── 공통 ──────────────────────────────────────
    "app_subtitle": {
        "ko": "질문 + 연결 💬",
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
    "filter_depth_help": {
        "ko": "1=가벼운 일상, 3=내면, 5=깊은 신앙/가치관",
        "en": "1=light/daily, 3=inner thoughts, 5=deep faith/values",
    },
    "filter_difficulty_help": {
        "ko": "1=쉬움, 2=보통, 3=어려움",
        "en": "1=easy, 2=medium, 3=hard",
    },
    "filter_reset": {
        "ko": "🧹 필터 초기화",
        "en": "🧹 Reset Filters",
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
    "sound_toggle": {
        "ko": "🔊 효과음",
        "en": "🔊 Sound FX",
    },

    # ── 아이스브레이킹 ───────────────────────────
    "btn_shuffle": {
        "ko": "🔀 셔플",
        "en": "🔀 Shuffle",
    },
    "btn_reset": {
        "ko": "🗑 초기화",
        "en": "🗑 Reset",
    },
    "remaining_cards": {
        "ko": "🃏 남은 카드: {remain} | 사용: {used}",
        "en": "🃏 Remaining: {remain} | Used: {used}",
    },
    "btn_next": {
        "ko": "▶️ 다음",
        "en": "▶️ Next",
    },
    "btn_prev": {
        "ko": "⬅ 이전",
        "en": "⬅ Prev",
    },
    "deck_exhausted": {
        "ko": "🔄 덱이 소진되었습니다! 셔플 버튼을 눌러 새 덱을 만드세요.",
        "en": "🔄 Deck exhausted! Press shuffle to build a new deck.",
    },
    "queue_prompt": {
        "ko": "▶️ '다음' 버튼을 눌러 질문을 시작하세요",
        "en": "▶️ Press 'Next' to start",
    },
    "history_title": {
        "ko": "📋 세션 히스토리 ({n}개)",
        "en": "📋 Session History ({n})",
    },
    "history_export": {
        "ko": "📥 CSV 다운로드",
        "en": "📥 Download CSV",
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
    "btn_play_again": {
        "ko": "🔁 한 판 더",
        "en": "🔁 Play Again",
    },
    "paused_overlay": {
        "ko": "⏸ 일시정지",
        "en": "⏸ PAUSED",
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

    # ── 모드 전환 확인 ────────────────────────────
    "mode_switch_warning": {
        "ko": "⚠️ 진행 중인 세션을 종료하고 모드를 전환하시겠습니까?",
        "en": "⚠️ End the current session and switch mode?",
    },
    "btn_confirm_switch": {
        "ko": "✅ 전환하기",
        "en": "✅ Switch",
    },
    "btn_cancel_switch": {
        "ko": "❌ 취소",
        "en": "❌ Cancel",
    },

    # ── 단축키 도움말 ────────────────────────────
    "shortcuts_title": {
        "ko": "⌨️ 단축키",
        "en": "⌨️ Shortcuts",
    },
    "shortcuts_body_icebreaker": {
        "ko": "Space/→: 다음 · ←: 이전 · S: 셔플",
        "en": "Space/→: Next · ←: Prev · S: Shuffle",
    },
    "shortcuts_body_speedgame": {
        "ko": "Space/Y: 정답 · N: 패스 · P: 일시정지 · Z: Undo",
        "en": "Space/Y: Correct · N: Pass · P: Pause · Z: Undo",
    },

    # ── 라운드/진행 ──────────────────────────────
    "round_progress": {
        "ko": "라운드 진행: {used} / {total}",
        "en": "Round Progress: {used} / {total}",
    },
}


# ── 카테고리/태그 라벨 ──────────────────────────────────
# CSV 슬러그(영문/한글) → UI 표시용 (양국어) 매핑.
# 매핑이 없으면 원본 값을 그대로 표시한다.
CATEGORY_LABELS = {
    "fun": {"ko": "재미", "en": "Fun"},
    "daily": {"ko": "일상", "en": "Daily"},
    "faith": {"ko": "신앙", "en": "Faith"},
    "family": {"ko": "가족", "en": "Family"},
    "growth": {"ko": "성장", "en": "Growth"},
    "vision": {"ko": "비전", "en": "Vision"},
    "성경인물": {"ko": "성경인물", "en": "Bible Figures"},
    "찬양": {"ko": "찬양", "en": "Worship"},
    "교회용어": {"ko": "교회용어", "en": "Church Terms"},
}


def t(key: str, lang: str = "ko", **kwargs) -> str:
    """번역 문자열 반환. kwargs로 포맷 변수 전달."""
    entry = TEXTS.get(key, {})
    text = entry.get(lang, entry.get("ko", key))
    if kwargs:
        text = text.format(**kwargs)
    return text


def category_label(raw: str, lang: str = "ko") -> str:
    """카테고리 슬러그를 표시용 라벨로 변환. 매핑 없으면 원본 반환."""
    if not raw:
        return ""
    entry = CATEGORY_LABELS.get(raw)
    if not entry:
        return raw
    return entry.get(lang, entry.get("ko", raw))
