"""core/loader.py – CSV 덱 스캔 · 로드 · 검증 · 정규화"""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import pandas as pd

# ── 상수 ────────────────────────────────────────────────
REQUIRED_COLS = {"id", "ko", "en"}
OPTIONAL_COLS = {
    "category": "",
    "depth": 1,
    "difficulty": 1,
    "tags": "",
    "enabled": 1,
}
STR_COLS = {"id", "ko", "en", "category", "tags"}
INT_COLS = {"depth", "difficulty", "enabled"}

FALLBACK_ENCODINGS = ["utf-8", "cp949", "euc-kr", "latin-1"]


# ── 데이터 클래스 ───────────────────────────────────────
@dataclass
class SetMeta:
    name: str
    path: str
    row_count: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    valid: bool = True


# ── 공개 함수 ───────────────────────────────────────────
def scan_sets(root_dir: str) -> List[SetMeta]:
    """root_dir 아래 *.csv 파일을 스캔해 SetMeta 목록 반환."""
    root = Path(root_dir)
    if not root.exists():
        return []
    metas: List[SetMeta] = []
    for p in sorted(root.glob("*.csv")):
        meta = SetMeta(name=p.stem, path=str(p))
        try:
            df = load_csv(str(p))
            ok, errors, warnings = validate(df)
            meta.row_count = len(df)
            meta.errors = errors
            meta.warnings = warnings
            meta.valid = ok
        except Exception as e:
            meta.valid = False
            meta.errors = [str(e)]
        metas.append(meta)
    return metas


def load_csv(path: str, extra_encodings: List[str] | None = None) -> pd.DataFrame:
    """UTF-8 우선, 실패 시 보조 인코딩 시도."""
    encodings = list(FALLBACK_ENCODINGS)
    if extra_encodings:
        encodings = extra_encodings + encodings
    last_err = None
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc, dtype=str, keep_default_na=False)
            df.columns = [c.strip().lower() for c in df.columns]
            return df
        except UnicodeDecodeError as e:
            last_err = e
        except Exception as e:
            raise e
    raise last_err or RuntimeError(f"Cannot read {path}")


def normalize(df: pd.DataFrame, set_name: str = "") -> pd.DataFrame:
    """컬럼 기본값 채우기 · 타입 변환 · strip."""
    df = df.copy()
    # 권장 컬럼 없으면 추가
    for col, default in OPTIONAL_COLS.items():
        if col not in df.columns:
            df[col] = default
    # 문자열 strip
    for col in STR_COLS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    # 숫자 변환
    for col in INT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(OPTIONAL_COLS.get(col, 0)).astype(int)
    # set_name 컬럼
    df["_set"] = set_name
    return df


def validate(df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
    """필수 컬럼 확인 + 경고 수집."""
    errors: List[str] = []
    warnings: List[str] = []
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        errors.append(f"필수 컬럼 누락: {missing}")
    if df.empty:
        warnings.append("CSV가 비어 있습니다.")
    if "id" in df.columns and df["id"].duplicated().any():
        dup_count = df["id"].duplicated().sum()
        warnings.append(f"중복 id {dup_count}건 (첫 행 사용)")
    return (len(errors) == 0, errors, warnings)


def load_and_prepare(path: str, set_name: str = "") -> pd.DataFrame | None:
    """로드 → 검증 → 정규화 한 번에. 실패 시 None."""
    try:
        df = load_csv(path)
        ok, errors, _ = validate(df)
        if not ok:
            return None
        return normalize(df, set_name=set_name)
    except Exception:
        return None
