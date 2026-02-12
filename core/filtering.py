"""core/filtering.py – 카테고리 · 깊이 · 난이도 · 태그 · enabled 필터."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

import pandas as pd


@dataclass
class Filters:
    categories: List[str] = field(default_factory=list)  # 빈 = 전체
    depth_min: int = 1
    depth_max: int = 5
    difficulty_min: int = 1
    difficulty_max: int = 3
    tags_include: List[str] = field(default_factory=list)
    only_enabled: bool = True


def apply_filters(df: pd.DataFrame, f: Filters) -> pd.DataFrame:
    """필터 조건에 맞는 행만 반환."""
    if df.empty:
        return df
    out = df.copy()

    # enabled
    if f.only_enabled and "enabled" in out.columns:
        out = out[out["enabled"] == 1]

    # category
    if f.categories and "category" in out.columns:
        out = out[out["category"].isin(f.categories)]

    # depth
    if "depth" in out.columns:
        out = out[(out["depth"] >= f.depth_min) & (out["depth"] <= f.depth_max)]

    # difficulty
    if "difficulty" in out.columns:
        out = out[(out["difficulty"] >= f.difficulty_min) & (out["difficulty"] <= f.difficulty_max)]

    # tags (OR 로직: 하나라도 포함되면 통과)
    if f.tags_include and "tags" in out.columns:
        pattern = "|".join(f.tags_include)
        out = out[out["tags"].str.contains(pattern, case=False, na=False)]

    return out.reset_index(drop=True)


def get_unique_categories(df: pd.DataFrame) -> List[str]:
    if "category" not in df.columns or df.empty:
        return []
    return sorted(df["category"].dropna().unique().tolist())


def get_unique_tags(df: pd.DataFrame) -> List[str]:
    if "tags" not in df.columns or df.empty:
        return []
    all_tags: set[str] = set()
    for val in df["tags"].dropna():
        for t in str(val).split(";"):
            t = t.strip()
            if t:
                all_tags.add(t)
    return sorted(all_tags)
