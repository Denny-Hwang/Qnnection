"""UI 스타일 헬퍼 단위 테스트 (XSS 차단 포함)."""

from __future__ import annotations

from core.ui_styles import (
    empty_card_html,
    format_question,
    question_card_html,
    safe,
    score_board_html,
)


def test_safe_escapes_lt_gt():
    assert safe("<script>") == "&lt;script&gt;"


def test_safe_escapes_quotes():
    assert "&quot;" in safe('"onmouseover="alert(1)"')


def test_safe_escapes_ampersand():
    assert safe("a & b") == "a &amp; b"


def test_safe_handles_none():
    assert safe(None) == ""


def test_safe_handles_int():
    assert safe(42) == "42"


def test_format_question_ko_only():
    p, s = format_question({"ko": "한", "en": "EN"}, "KO only")
    assert p == "한"
    assert s == ""


def test_format_question_en_only():
    p, s = format_question({"ko": "한", "en": "EN"}, "EN only")
    assert p == "EN"
    assert s == ""


def test_format_question_ko_en():
    p, s = format_question({"ko": "한", "en": "EN"}, "KO → EN")
    assert p == "한"
    assert s == "EN"


def test_format_question_en_ko():
    p, s = format_question({"ko": "한", "en": "EN"}, "EN → KO")
    assert p == "EN"
    assert s == "한"


def test_format_question_default_returns_both():
    p, s = format_question({"ko": "한", "en": "EN"}, "unknown_mode")
    assert p == "한"
    assert s == "EN"


def test_format_question_missing_keys_returns_empty():
    p, s = format_question({}, "KO only")
    assert p == ""


def test_question_card_html_escapes_xss():
    """raw HTML 태그/속성/스크립트가 실행 가능한 형태로 남으면 안 된다."""
    html = question_card_html(
        primary='<img src=x onerror="alert(1)">',
        secondary="</span><script>alert(1)</script>",
        category='" onclick="x"',
    )
    # raw 태그/스크립트가 그대로 들어가면 안 됨
    assert "<script>" not in html
    assert "<img " not in html
    assert "</script>" not in html
    # raw 따옴표 + 속성 패턴 (escape 안된 경우)이 없어야 함
    assert 'onerror="' not in html  # 진짜 quote는 escape되어 &quot;
    assert 'onclick="' not in html
    # 카드 컨테이너 구조는 유지
    assert 'class="q-card' in html
    assert 'role="region"' in html
    assert 'aria-live="polite"' in html
    # 위험 입력은 HTML entity 형태로 들어가야 함
    assert "&lt;img" in html
    assert "&lt;script&gt;" in html


def test_question_card_html_with_flash():
    html = question_card_html("Q", flash="correct")
    assert "flash-correct" in html


def test_question_card_html_with_paused_overlay():
    html = question_card_html("Q", paused_label="PAUSED")
    assert "paused-overlay" in html
    assert "PAUSED" in html


def test_empty_card_html_escapes():
    html = empty_card_html("<b>hi</b>")
    assert "&lt;b&gt;" in html
    assert "<b>hi</b>" not in html


def test_score_board_html_includes_score():
    html = score_board_html(7, 5, 2, "✅", "❌")
    assert "🎯 7" in html
    assert ">5<" in html or "&gt;5&lt;" in html or "✅ 5" in html
    assert "aria-live" in html
