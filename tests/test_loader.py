"""로더 단위 테스트 (CSV 검증/정규화/인코딩 fallback)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from core.loader import (
    FALLBACK_ENCODINGS,
    load_and_prepare,
    load_csv,
    normalize,
    scan_sets,
    validate,
)


def _write(tmp_path: Path, name: str, content: str, encoding: str = "utf-8") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding=encoding)
    return p


def test_utf_8_sig_is_first_in_fallback():
    # Excel BOM 호환을 위해 utf-8-sig를 최우선으로 시도해야 함
    assert FALLBACK_ENCODINGS[0] == "utf-8-sig"


def test_load_csv_reads_utf8_bom(tmp_path: Path):
    p = _write(
        tmp_path, "bom.csv",
        "id,ko,en\nq1,안녕,Hi\n",
        encoding="utf-8-sig",
    )
    df = load_csv(str(p))
    assert list(df.columns) == ["id", "ko", "en"]
    assert df.iloc[0]["ko"] == "안녕"


def test_load_csv_falls_back_to_cp949(tmp_path: Path):
    p = tmp_path / "cp949.csv"
    p.write_bytes("id,ko,en\nq1,안녕,Hi\n".encode("cp949"))
    df = load_csv(str(p))
    assert df.iloc[0]["ko"] == "안녕"


def test_validate_missing_required_cols():
    df = pd.DataFrame({"id": ["1"], "ko": ["a"]})
    ok, errors, _ = validate(df)
    assert not ok
    assert errors


def test_validate_passes_with_required_cols():
    df = pd.DataFrame({"id": ["1"], "ko": ["a"], "en": ["A"]})
    ok, errors, _ = validate(df)
    assert ok
    assert errors == []


def test_validate_warns_on_duplicate_ids():
    df = pd.DataFrame({"id": ["1", "1"], "ko": ["a", "b"], "en": ["A", "B"]})
    ok, _, warnings = validate(df)
    assert ok
    assert any("중복" in w for w in warnings)


def test_validate_warns_all_disabled():
    df = pd.DataFrame(
        {"id": ["1", "2"], "ko": ["a", "b"], "en": ["A", "B"], "enabled": ["0", "0"]}
    )
    ok, _, warnings = validate(df)
    assert ok
    assert any("enabled=0" in w for w in warnings)


def test_normalize_fills_optional_columns():
    df = pd.DataFrame({"id": ["1"], "ko": ["a"], "en": ["A"]})
    out = normalize(df, set_name="my_set")
    assert "category" in out.columns
    assert "depth" in out.columns
    assert "difficulty" in out.columns
    assert "tags" in out.columns
    assert "enabled" in out.columns
    assert out["depth"].iloc[0] == 1
    assert out["enabled"].iloc[0] == 1
    assert out["_set"].iloc[0] == "my_set"


def test_normalize_strips_strings():
    df = pd.DataFrame({"id": ["  1  "], "ko": [" 안녕 "], "en": [" Hi "]})
    out = normalize(df)
    assert out["id"].iloc[0] == "1"
    assert out["ko"].iloc[0] == "안녕"
    assert out["en"].iloc[0] == "Hi"


def test_normalize_coerces_numeric_with_fallback():
    df = pd.DataFrame(
        {"id": ["1"], "ko": ["a"], "en": ["A"], "depth": ["bad"], "difficulty": ["2"]}
    )
    out = normalize(df)
    assert out["depth"].iloc[0] == 1  # fallback default
    assert out["difficulty"].iloc[0] == 2


def test_load_and_prepare_returns_none_for_missing_required(tmp_path: Path):
    p = _write(tmp_path, "bad.csv", "id,ko\nq1,안녕\n")
    assert load_and_prepare(str(p)) is None


def test_load_and_prepare_success(tmp_path: Path):
    p = _write(tmp_path, "good.csv", "id,ko,en\nq1,안녕,Hi\nq2,잘가,Bye\n")
    df = load_and_prepare(str(p), set_name="greet")
    assert df is not None
    assert len(df) == 2
    assert df["_set"].iloc[0] == "greet"


def test_scan_sets_skips_nonexistent_dir(tmp_path: Path):
    metas = scan_sets(str(tmp_path / "nope"))
    assert metas == []


def test_scan_sets_marks_invalid(tmp_path: Path):
    _write(tmp_path, "ok.csv", "id,ko,en\nq1,a,A\n")
    _write(tmp_path, "bad.csv", "id,ko\nq1,a\n")
    metas = scan_sets(str(tmp_path))
    by_name = {m.name: m for m in metas}
    assert by_name["ok"].valid is True
    assert by_name["bad"].valid is False
