"""필터링 단위 테스트."""

from __future__ import annotations

import pandas as pd

from core.filtering import (
    Filters,
    apply_filters,
    get_unique_categories,
    get_unique_tags,
)


def _make_df():
    return pd.DataFrame(
        [
            {"id": "1", "ko": "a", "en": "A", "category": "fun",
             "depth": 1, "difficulty": 1, "tags": "일상;감정", "enabled": 1},
            {"id": "2", "ko": "b", "en": "B", "category": "faith",
             "depth": 3, "difficulty": 2, "tags": "신앙;감사", "enabled": 1},
            {"id": "3", "ko": "c", "en": "C", "category": "faith",
             "depth": 5, "difficulty": 3, "tags": "신앙;가치관", "enabled": 1},
            {"id": "4", "ko": "d", "en": "D", "category": "daily",
             "depth": 2, "difficulty": 1, "tags": "일상", "enabled": 0},
        ]
    )


def test_apply_filters_empty_returns_empty():
    assert apply_filters(pd.DataFrame(), Filters()).empty


def test_only_enabled_filters_disabled_rows():
    df = _make_df()
    out = apply_filters(df, Filters())
    assert len(out) == 3
    assert "4" not in out["id"].values


def test_category_filter_includes_only_selected():
    df = _make_df()
    out = apply_filters(df, Filters(categories=["faith"]))
    assert set(out["id"]) == {"2", "3"}


def test_depth_range_inclusive():
    df = _make_df()
    out = apply_filters(df, Filters(depth_min=1, depth_max=3))
    assert set(out["id"]) == {"1", "2"}  # 4는 enabled=0 제외


def test_difficulty_range():
    df = _make_df()
    out = apply_filters(df, Filters(difficulty_min=2, difficulty_max=3))
    assert set(out["id"]) == {"2", "3"}


def test_tags_filter_OR_logic():
    df = _make_df()
    out = apply_filters(df, Filters(tags_include=["감사"]))
    assert set(out["id"]) == {"2"}


def test_tags_filter_multiple_OR():
    df = _make_df()
    out = apply_filters(df, Filters(tags_include=["감사", "가치관"]))
    assert set(out["id"]) == {"2", "3"}


def test_get_unique_categories_sorted():
    df = _make_df()
    cats = get_unique_categories(df)
    assert cats == sorted(cats)
    assert "fun" in cats
    assert "faith" in cats


def test_get_unique_categories_empty_df():
    assert get_unique_categories(pd.DataFrame()) == []


def test_get_unique_tags_split_by_semicolon():
    df = _make_df()
    tags = get_unique_tags(df)
    assert "일상" in tags
    assert "신앙" in tags
    assert "감사" in tags
    assert "가치관" in tags
    assert tags == sorted(tags)


def test_get_unique_tags_empty_df():
    assert get_unique_tags(pd.DataFrame()) == []
