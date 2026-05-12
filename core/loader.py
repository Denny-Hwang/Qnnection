"""core/loader.py – CSV 덱 스캔 · 로드 · 검증 · 정규화."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

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

# Excel-저장 CSV는 BOM이 흔하므로 utf-8-sig 우선.
FALLBACK_ENCODINGS = ["utf-8-sig", "utf-8", "cp949", "euc-kr", "latin-1"]


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
            logger.warning("scan_sets: %s 로드 실패: %s", p, e)
            meta.valid = False
            meta.errors = [str(e)]
        metas.append(meta)
    return metas


def load_csv(path: str, extra_encodings: List[str] | None = None) -> pd.DataFrame:
    """UTF-8(BOM) 우선, 실패 시 보조 인코딩으로 재시도.

    UnicodeDecodeError 외 예외(EmptyData, ParserError 등)는 다음 인코딩을 시도하되,
    모든 시도 실패 시 마지막 예외를 raise.
    """
    encodings = list(FALLBACK_ENCODINGS)
    if extra_encodings:
        encodings = extra_encodings + encodings
    last_err: Exception | None = None
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc, dtype=str, keep_default_na=False)
            df.columns = [c.strip().lower() for c in df.columns]
            return df
        except UnicodeDecodeError as e:
            last_err = e
        except (pd.errors.ParserError, pd.errors.EmptyDataError) as e:
            # 파서 에러는 인코딩과 무관 — 즉시 raise
            raise
        except Exception as e:
            # 기타 예외도 다음 인코딩으로 한 번 더 시도해본다.
            last_err = e
            logger.debug("load_csv: %s 인코딩 %s 시도 실패: %s", path, enc, e)
    raise last_err or RuntimeError(f"Cannot read {path}")


def normalize(df: pd.DataFrame, set_name: str = "") -> pd.DataFrame:
    """컬럼 기본값 채우기 · 타입 변환 · strip."""
    df = df.copy()
    for col, default in OPTIONAL_COLS.items():
        if col not in df.columns:
            df[col] = default
    for col in STR_COLS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    for col in INT_COLS:
        if col in df.columns:
            df[col] = (
                pd.to_numeric(df[col], errors="coerce")
                .fillna(OPTIONAL_COLS.get(col, 0))
                .astype(int)
            )
    df["_set"] = set_name
    return df


def validate(df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
    """필수 컬럼 확인 + 경고 수집."""
    errors: List[str] = []
    warnings: List[str] = []
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        errors.append(f"필수 컬럼 누락: {sorted(missing)}")
    if df.empty:
        warnings.append("CSV가 비어 있습니다.")
    if "id" in df.columns and df["id"].duplicated().any():
        dup_count = int(df["id"].duplicated().sum())
        warnings.append(f"중복 id {dup_count}건 (첫 행 사용)")
    if "enabled" in df.columns:
        enabled_col = pd.to_numeric(df["enabled"], errors="coerce").fillna(1).astype(int)
        if not df.empty and (enabled_col == 0).all():
            warnings.append("모든 행이 enabled=0 — 사용 가능한 질문이 없습니다.")
    return (len(errors) == 0, errors, warnings)


def load_and_prepare(path: str, set_name: str = "") -> pd.DataFrame | None:
    """로드 → 검증 → 정규화 한 번에. 실패 시 None.

    실패 사유는 logger.warning으로 기록되어 운영자가 추적 가능.
    """
    try:
        df = load_csv(path)
        ok, errors, _ = validate(df)
        if not ok:
            logger.warning("load_and_prepare: %s 검증 실패: %s", path, errors)
            return None
        return normalize(df, set_name=set_name)
    except Exception as e:
        logger.warning("load_and_prepare: %s 로드 실패: %s", path, e)
        return None
