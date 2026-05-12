"""i18n 단위 테스트."""

from __future__ import annotations

from core.i18n import CATEGORY_LABELS, TEXTS, category_label, t


def test_t_returns_korean_by_default():
    assert t("btn_next", "ko") == "▶️ 다음"


def test_t_returns_english():
    assert t("btn_next", "en") == "▶️ Next"


def test_t_falls_back_to_korean_for_missing_lang():
    # 존재하지 않는 언어 → ko 또는 키 자체 반환
    out = t("btn_next", "fr")
    assert out in ("▶️ 다음", "btn_next")


def test_t_with_format_kwargs():
    out = t("pool_count", "ko", n=42)
    assert "42" in out


def test_t_missing_key_returns_key():
    assert t("__missing__", "ko") == "__missing__"


def test_all_keys_have_both_languages():
    for k, entry in TEXTS.items():
        assert "ko" in entry, f"{k} missing 'ko'"
        assert "en" in entry, f"{k} missing 'en'"


def test_category_label_known_slug_korean():
    assert category_label("faith", "ko") == "신앙"


def test_category_label_known_slug_english():
    assert category_label("faith", "en") == "Faith"


def test_category_label_unknown_returns_raw():
    assert category_label("custom_cat", "ko") == "custom_cat"


def test_category_label_empty_returns_empty():
    assert category_label("", "ko") == ""


def test_category_labels_dict_consistency():
    for slug, entry in CATEGORY_LABELS.items():
        assert "ko" in entry, f"{slug} missing 'ko'"
        assert "en" in entry, f"{slug} missing 'en'"
