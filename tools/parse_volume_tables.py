#!/usr/bin/env python3
"""
2023 입목재적·바이오매스 및 임분수확표 — 전체 섹션 파서 (Ⅱ ~ Ⅹ).

원본: raw/manuals/2023년 입목재적·바이오매스 및 임분수확표.md
출력:
  - wiki/매뉴얼/2023_입목재적_바이오매스_임분수확표/수종/{수종명}.md (16수종 통합)
  - wiki/매뉴얼/2023_입목재적_바이오매스_임분수확표/01_원목재적표.md (Ⅲ, Smalian)
  - wiki/매뉴얼/2023_입목재적_바이오매스_임분수확표/02_벌근직경_흉고직경_추정.md (Ⅴ)

지원 섹션:
  Ⅱ. 입목수간재적표 (16수종)             — 매트릭스 (수고 × 흉고직경)
  Ⅲ. 원목재적표 (기타침·활·소나무·낙엽송) — 매트릭스 (말구직경 × 길이), 표준페이지
  Ⅳ. 입목 수간중량표 및 이용중량표 (8수종, 표본 따라 1~4 부표) — 매트릭스
  Ⅴ. 벌근직경 → 흉고직경 추정 (11수종)    — 단일 표, 표준페이지
  Ⅵ. 입목 바이오매스표 (12수종)            — 매트릭스 + 부위별 전환계수
  Ⅶ. 법정림 지위지수 분류표 (11수종)        — 소형 매트릭스 (임령 × 지위지수)
  Ⅷ. 법정림 임분수확표 (13수종)             — 장형 (11열: 지위지수·임령·평균직경·…)
  Ⅸ. 현실림 지위지수 분류표 (14수종)        — 소형 매트릭스
  Ⅹ. 현실림 임분수확표 (14수종)             — 장형 (11열)

곡선도(이미지) 부분은 별도 처리 — 본 파서는 표 데이터만 처리.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "manuals" / "2023년 입목재적·바이오매스 및 임분수확표.md"
MANUAL_DIR = ROOT / "wiki" / "매뉴얼" / "2023_입목재적_바이오매스_임분수확표"
SPECIES_DIR = MANUAL_DIR / "수종"

# 16수종 (Ⅱ장 등록 순)
SPECIES_ORDER = [
    "강원지방소나무", "중부지방소나무", "해송", "리기다소나무",
    "잣나무", "낙엽송", "삼나무", "편백",
    "상수리나무", "굴참나무", "신갈나무", "졸참나무",
    "자작나무", "백합나무", "이태리포플러", "대나무",
]

# 섹션별 등장 수종
SPECIES_II = SPECIES_ORDER  # 모든 16종
SPECIES_IV = ["잣나무", "낙엽송", "리기다소나무", "강원지방소나무", "중부지방소나무", "해송", "상수리나무", "신갈나무"]
SPECIES_V_CONIFER = ["강원지방소나무", "중부지방소나무", "리기다소나무", "잣나무", "낙엽송", "편백"]
SPECIES_V_BROAD = ["상수리나무", "굴참나무", "신갈나무", "자작나무", "백합나무"]
SPECIES_VI = ["강원지방소나무", "중부지방소나무", "해송", "리기다소나무", "잣나무", "낙엽송", "삼나무", "편백", "상수리나무", "굴참나무", "신갈나무", "자작나무"]
SPECIES_VII = ["강원지방소나무", "중부지방소나무", "리기다소나무", "잣나무", "낙엽송", "편백", "상수리나무", "굴참나무", "신갈나무", "자작나무(잠정)", "백합나무(잠정)"]
SPECIES_VIII = ["강원지방소나무", "중부지방소나무", "리기다소나무", "잣나무", "낙엽송", "편백", "삼나무", "상수리나무", "굴참나무", "신갈나무", "자작나무(잠정)", "백합나무(잠정)", "졸참나무(잠정)"]
SPECIES_IX = ["강원지방소나무", "중부지방소나무", "해송", "리기다소나무", "잣나무", "낙엽송", "삼나무", "편백", "상수리나무", "굴참나무", "졸참나무", "신갈나무", "자작나무", "백합나무"]
SPECIES_X = ["강원지방소나무", "중부지방소나무", "해송", "리기다소나무", "잣나무", "낙엽송", "삼나무", "편백", "상수리나무", "굴참나무", "졸참나무", "신갈나무", "자작나무", "백합나무"]

# 원본 PDF 페이지번호 (지위지수 분류표·곡선도)
# Ⅶ 법정림: 책 페이지 232~242, Ⅸ 현실림: 274~287
PDF_PAGE_VII = {
    "강원지방소나무": 232, "중부지방소나무": 233, "리기다소나무": 234,
    "잣나무": 235, "낙엽송": 236, "편백": 237,
    "상수리나무": 238, "굴참나무": 239, "신갈나무": 240,
    "자작나무": 241, "백합나무": 242,
}
PDF_PAGE_IX = {
    "강원지방소나무": 274, "중부지방소나무": 275, "해송": 276, "리기다소나무": 277,
    "잣나무": 278, "낙엽송": 279, "삼나무": 280, "편백": 281,
    "상수리나무": 282, "굴참나무": 283, "졸참나무": 284, "신갈나무": 285,
    "자작나무": 286, "백합나무": 287,
}

# 매뉴얼 표 종류별 키 — 자작나무는 OCR 오타로 "피포함"
KIND_II = {
    "강원지방소나무": "수피포함", "중부지방소나무": "수피포함", "해송": "수피포함",
    "리기다소나무": "수피포함", "잣나무": "수피포함", "낙엽송": "수피포함",
    "삼나무": "수피포함", "편백": "수피포함",
    "상수리나무": "수피포함", "굴참나무": "수피포함", "신갈나무": "수피포함",
    "졸참나무": "수피포함", "자작나무": "피포함", "백합나무": "수피포함",
    "이태리포플러": "수피포함", "대나무": "수피외직경",
}

# ─────────────────────────────────────────────────────────────
# 공통 유틸
# ─────────────────────────────────────────────────────────────

RUNNING_HEADER_PATTERNS = [
    re.compile(r"^Ⅰ$|^Ⅱ$|^Ⅲ$|^Ⅳ$|^Ⅴ$|^Ⅵ$|^Ⅶ$|^Ⅷ$|^Ⅸ$|^Ⅹ$"),
    re.compile(r"^Ⅰ\.\s|^Ⅱ\.\s|^Ⅲ\.\s|^Ⅳ\.\s|^Ⅴ\.\s|^Ⅵ\.\s|^Ⅶ\.\s|^Ⅷ\.\s|^Ⅸ\.\s|^Ⅹ\.\s"),
    re.compile(r"^\d{1,3}\s「2023」\s입목재적"),
    re.compile(r"^\d{1,3}\s+「2023」"),
]

def is_running_header(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    return any(pat.search(s) for pat in RUNNING_HEADER_PATTERNS)


def find_section_bounds(lines: list[str], roman: str, next_roman: str | None, *, body_offset: int = 190) -> tuple[int, int]:
    """본문 시작/종료 — 본문은 라인 body_offset 이후에서 탐지.

    TOC 엔트리(점 포함)는 무시. 본문의 섹션 헤더는 '{roman}. {제목}' 정확히 일치.
    """
    start = end = -1
    sec_pat = re.compile(rf"^{re.escape(roman)}\.\s+[^·]+$")
    next_pat = re.compile(rf"^{re.escape(next_roman)}\.\s+[^·]+$") if next_roman else None
    for i in range(body_offset, len(lines)):
        s = lines[i].strip()
        if start == -1 and sec_pat.match(s):
            start = i + 1
            continue
        if start != -1 and next_pat is not None and next_pat.match(s):
            end = i
            break
    if end == -1:
        end = len(lines)
    if start == -1:
        raise RuntimeError(f"섹션 {roman}장 경계 탐지 실패")
    return start, end


def find_chapter_in_section(lines: list[str], sec_start: int, sec_end: int, species: str, *, next_candidates: list[str] | None = None) -> tuple[int, int] | None:
    """섹션 내에서 'N. {species}' 챕터 마커를 탐지하고 다음 챕터까지의 범위 반환."""
    species_pat = re.compile(rf"^\d{{1,3}}\.\s+{re.escape(species)}$")
    start = -1
    for i in range(sec_start, sec_end):
        if species_pat.match(lines[i].strip()):
            start = i + 1
            break
    if start == -1:
        return None
    end = sec_end
    next_pat = re.compile(r"^\d{1,3}\.\s+\S")
    for i in range(start, sec_end):
        s = lines[i].strip()
        if next_pat.match(s) and not is_running_header(lines[i]):
            # 차후 챕터 마커 (예: '20. 중부지방소나무')
            # 단, 첫 줄 자기 자신은 이미 지난 상태
            end = i
            break
    return start, end


# ─────────────────────────────────────────────────────────────
# 매트릭스 표 파서 (Ⅱ, Ⅳ, Ⅵ, Ⅲ, Ⅶ, Ⅸ)
# ─────────────────────────────────────────────────────────────

def is_header_row(line: str, *, max_diff: int = 50, min_cols: int = 4) -> bool:
    """정수만, min_cols 이상, 단조증가, 등차 일정한 헤더 행."""
    s = line.strip()
    if not s:
        return False
    parts = s.split()
    if len(parts) < min_cols:
        return False
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return False
    if any(nums[i + 1] <= nums[i] for i in range(len(nums) - 1)):
        return False
    diffs = {nums[i + 1] - nums[i] for i in range(len(nums) - 1)}
    if len(diffs) != 1:
        return False
    d = next(iter(diffs))
    return 1 <= d <= max_diff


def is_float_header_row(line: str) -> bool:
    """원목재적표 길이 헤더 (소수): 1.8 1.9 2.0 ..."""
    s = line.strip()
    if not s:
        return False
    parts = s.split()
    if len(parts) < 4:
        return False
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        return False
    if any(not (0 < n < 100) for n in nums):
        return False
    if any(nums[i + 1] <= nums[i] for i in range(len(nums) - 1)):
        return False
    # 등차가 거의 일정 (소수점 오차 허용)
    diffs = [round(nums[i + 1] - nums[i], 2) for i in range(len(nums) - 1)]
    return len(set(diffs)) == 1


def is_data_row(line: str) -> tuple[bool, list[str]]:
    """숫자(정수/소수)만으로 구성된 행."""
    s = line.strip()
    if not s:
        return False, []
    parts = s.split()
    if not parts:
        return False, []
    for p in parts:
        if not re.fullmatch(r"-?\d+(?:\.\d+)?", p):
            return False, []
    return True, parts


@dataclass
class MatrixChunk:
    cols: list[str] = field(default_factory=list)  # 열 헤더 (DBH, 길이 등)
    rows: list[tuple[str | None, list[str]]] = field(default_factory=list)  # (행 헤더, 값들)


def parse_matrix_chunks(
    lines: list[str], start: int, end: int, *,
    integer_col_max_diff: int = 50,
    min_cols: int = 4,
    allow_float_cols: bool = False,
    stop_on_subtable: bool = False,
) -> list[MatrixChunk]:
    """범위 내에서 청크(헤더 행 + 데이터 행 묶음) 추출.

    stop_on_subtable=True 면 'N-M. ...' 또는 '부위별 / 전환계수' 가 나오면 중단.
    """
    chunks: list[MatrixChunk] = []
    current: MatrixChunk | None = None

    i = start
    subtable_pat = re.compile(r"^\d+-\d+\.")
    while i < end:
        line = lines[i]
        s = line.strip()

        if is_running_header(line):
            i += 1
            continue

        # 다음 부표 시작 → 중단
        if stop_on_subtable and (subtable_pat.match(s) or s == "부위별"):
            break

        if is_header_row(line, max_diff=integer_col_max_diff, min_cols=min_cols) or (allow_float_cols and is_float_header_row(line)):
            if current and current.rows:
                chunks.append(current)
            current = MatrixChunk(cols=s.split())
            i += 1
            continue

        if current is not None:
            ok, parts = is_data_row(line)
            if ok:
                n = len(current.cols)
                if len(parts) == n + 1:
                    current.rows.append((parts[0], parts[1:]))
                elif len(parts) == n:
                    current.rows.append((None, parts))
                # else: 너비 불일치 — 스킵
                i += 1
                continue

        i += 1

    if current and current.rows:
        chunks.append(current)
    return chunks


def merge_chunks(chunks: list[MatrixChunk]) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """청크 목록 → 전체 매트릭스 (행 헤더, 값들). 첫 청크의 행 헤더를 기준으로 매칭."""
    if not chunks:
        return [], []
    all_cols: list[str] = []
    for c in chunks:
        all_cols.extend(c.cols)
    # 행 인덱스 기반 병합 — 첫 청크에 행 헤더가 있고, 이후 청크는 헤더 없음
    n_rows = max(len(c.rows) for c in chunks)
    merged: list[tuple[str, list[str]]] = []
    for r in range(n_rows):
        header: str | None = None
        vals: list[str] = []
        for c in chunks:
            if r < len(c.rows):
                h, v = c.rows[r]
                if h is not None and header is None:
                    header = h
                vals.extend(v)
            else:
                vals.extend(["—"] * len(c.cols))
        if header is None:
            continue
        merged.append((header, vals))
    return all_cols, merged


def render_matrix_md(
    title: str, row_label: str, col_label: str, unit: str,
    cols: list[str], rows: list[tuple[str, list[str]]],
) -> str:
    if not cols or not rows:
        return f"### {title}\n\n*(데이터 파싱 실패)*\n"
    lines = [
        f"### {title}",
        "",
        f"> 단위: {unit} | 행: {row_label} | 열: {col_label}",
        "",
    ]
    header = f"| {row_label}\\{col_label} | " + " | ".join(cols) + " |"
    sep = "|---|" + "|".join("---:" for _ in cols) + "|"
    lines.append(header)
    lines.append(sep)
    for h, vals in rows:
        lines.append(f"| **{h}** | " + " | ".join(vals) + " |")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# Ⅵ 부위별 전환계수
# ─────────────────────────────────────────────────────────────

def parse_conversion_coefs(lines: list[str], start: int, end: int) -> dict[str, str]:
    """OCR이 세로로 나열한 '부위별 / 전환계수 / 가지 / 0.240 / 잎 / 0.100 / 뿌리 / 0.342' 파싱."""
    coefs: dict[str, str] = {}
    found_marker = False
    keys = ["가지", "잎", "뿌리"]
    pending: str | None = None
    for i in range(start, end):
        s = lines[i].strip()
        if s == "부위별":
            found_marker = True
            continue
        if not found_marker:
            continue
        if s in keys:
            pending = s
            continue
        if pending is not None and re.fullmatch(r"\d+(?:\.\d+)?", s):
            coefs[pending] = s
            pending = None
            if len(coefs) == len(keys):
                break
    return coefs


# ─────────────────────────────────────────────────────────────
# Ⅷ·Ⅹ 임분수확표 (장형 11열)
# ─────────────────────────────────────────────────────────────

YIELD_COLS = [
    "지위지수", "임령(년)", "평균직경(cm)", "흉고단면적(㎡/ha)",
    "평균수고(m)", "우세목수고(m)", "본수(본)", "재적(㎥/ha)",
    "정기평균생장량(㎥/ha)", "정기평균생장률(%)", "연평균생장량(㎥/ha/yr)",
]


def parse_yield_table(lines: list[str], start: int, end: int) -> list[list[str]]:
    """11열 임분수확표 데이터 행 추출. 첫 행은 9열(정기평균생장량·률 없음), 이후 11열.

    본수(본)가 1,000본 단위로 콤마를 가지면 콤마 제거 후 단일 토큰으로 처리.
    """
    rows: list[list[str]] = []
    token_pat = re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?")
    for i in range(start, end):
        line = lines[i].strip()
        if not line:
            continue
        if is_running_header(lines[i]):
            continue
        if not re.search(r"\d", line):
            continue
        # 챕터 마커 'N. 수종명' 또는 비숫자 헤더는 스킵
        if re.match(r"^\d+\.\s\S+[가-힣]", line):
            continue
        # 모든 토큰이 숫자(콤마 포함) 패턴인지
        toks = token_pat.findall(line)
        nontoks = token_pat.sub("", line).strip()
        if nontoks or len(toks) not in (9, 11):
            continue
        # 본수의 콤마 제거 — 표시는 콤마 유지하되 토큰 단일화
        rows.append(toks)
    return rows


def render_yield_md(title: str, rows: list[list[str]]) -> str:
    if not rows:
        return f"### {title}\n\n*(데이터 파싱 실패)*\n"
    lines = [
        f"### {title}",
        "",
        "| " + " | ".join(YIELD_COLS) + " |",
        "|" + "|".join("---:" for _ in YIELD_COLS) + "|",
    ]
    for r in rows:
        if len(r) == 9:
            # 첫 임령 행 — 정기평균생장량·률 빈칸
            cells = r[:8] + ["—", "—"] + [r[8]]
        else:
            cells = r
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# Ⅴ 벌근직경 → 흉고직경 (단일 표)
# ─────────────────────────────────────────────────────────────

def parse_bunkeun_table(lines: list[str], sec_start: int, sec_end: int) -> tuple[list[str], list[tuple[str, list[str]]], list[str], list[list[str]]]:
    """침엽수(벌근직경 컬럼 포함) 5수종 + 활엽수(벌근직경 없음) 6수종 표 파싱."""
    # 침엽수 페이지: '강원지방소나무 중부지방소나무 ... 낙엽송' 헤더 다음 데이터 행
    coni_header_pat = re.compile(r"^강원지방소나무\s")
    broad_header_pat = re.compile(r"^편백\s")
    conifer_species: list[str] = []
    broad_species: list[str] = []
    conifer_rows: list[tuple[str, list[str]]] = []
    broad_rows: list[list[str]] = []

    state = None
    for i in range(sec_start, sec_end):
        line = lines[i]
        s = line.strip()
        if is_running_header(line):
            continue
        if coni_header_pat.match(s):
            conifer_species = s.split()
            state = "conifer"
            continue
        if broad_header_pat.match(s):
            broad_species = s.split()
            state = "broad"
            continue
        if state is None:
            continue
        ok, parts = is_data_row(line)
        if not ok:
            continue
        if state == "conifer":
            # 벌근직경 + 5수종 값 = 6 토큰
            if len(parts) == len(conifer_species) + 1:
                conifer_rows.append((parts[0], parts[1:]))
        else:
            # 활엽수: 벌근직경 컬럼 없음, 6 토큰
            if len(parts) == len(broad_species):
                broad_rows.append(parts)
    return conifer_species, conifer_rows, broad_species, broad_rows


# ─────────────────────────────────────────────────────────────
# Ⅲ 원목재적표 — 카테고리 별 (기타침엽수 / 기타활엽수 / 소나무 / 낙엽송)
# ─────────────────────────────────────────────────────────────

LOG_CATEGORIES = ["기타침엽수", "기타활엽수", "소나무", "낙엽송"]


def find_log_category_blocks(lines: list[str], sec_start: int, sec_end: int) -> dict[str, tuple[int, int]]:
    """원목재적표는 카테고리가 여러 챕터에 걸쳐 반복됨 (예: 24. 기타침엽수, 25. 기타침엽수 ...).

    카테고리별 전체 범위를 합치기 위해 첫 등장 ~ 다음 다른 카테고리 직전 + 동일 카테고리 연속 구간 추적.
    """
    cat_pat = re.compile(r"^\d+\.\s+(기타침엽수|기타활엽수|소나무|낙엽송)$")
    blocks: dict[str, list[int]] = {c: [] for c in LOG_CATEGORIES}
    chap_lines: list[tuple[str, int]] = []
    for i in range(sec_start, sec_end):
        m = cat_pat.match(lines[i].strip())
        if m:
            chap_lines.append((m.group(1), i))
    # 각 카테고리별로 (첫 챕터 시작 ~ 마지막 챕터 종료) 범위 산출 — 카테고리는 연속 등장
    result: dict[str, tuple[int, int]] = {}
    if not chap_lines:
        return result
    chap_lines.append(("__END__", sec_end))
    cur_cat: str | None = None
    cur_start: int = -1
    for cat, idx in chap_lines:
        if cat != cur_cat:
            if cur_cat is not None and cur_cat in LOG_CATEGORIES:
                # 이전 카테고리 종료
                result[cur_cat] = (cur_start, idx)
            cur_cat = cat
            cur_start = idx
    return result


# ─────────────────────────────────────────────────────────────
# Ⅳ 입목 수간중량표 — 4 부표 per species
# ─────────────────────────────────────────────────────────────

IV_SUBTABLES = [
    ("생중량", "수피포함 생중량"),
    ("건중량", "수피포함 건중량"),
    ("이용생중량", "수피포함 이용생중량"),
    ("이용건중량", "수피제외 이용건중량"),
]


def parse_iv_subtables(lines: list[str], chap_start: int, chap_end: int) -> dict[str, tuple[list[str], list[tuple[str, list[str]]]]]:
    """챕터 범위 내 4 부표 추출."""
    # '1-1.', '1-2.', '1-3.', '1-4.' 등의 마커로 분할
    subtable_pat = re.compile(r"^\d+-(\d+)\.")
    submarkers: list[tuple[int, int]] = []  # (sub_index, line_idx)
    for i in range(chap_start, chap_end):
        m = subtable_pat.match(lines[i].strip())
        if m:
            submarkers.append((int(m.group(1)), i))
    submarkers.append((-1, chap_end))

    result: dict[str, tuple[list[str], list[tuple[str, list[str]]]]] = {}
    for idx in range(len(submarkers) - 1):
        sub_idx, line_idx = submarkers[idx]
        next_line = submarkers[idx + 1][1]
        if sub_idx < 1 or sub_idx > 4:
            continue
        chunks = parse_matrix_chunks(lines, line_idx + 1, next_line)
        cols, rows = merge_chunks(chunks)
        if cols and rows:
            kind = IV_SUBTABLES[sub_idx - 1][0]
            result[kind] = (cols, rows)
    return result


# ─────────────────────────────────────────────────────────────
# 페이지 생성
# ─────────────────────────────────────────────────────────────

def _interpolation_block(si_cols: list[str], use_label: str) -> str:
    """지위지수 분류표 보간 안내 블록 (선형 보간식 + 사용 예시)."""
    si_min = si_cols[0] if si_cols else "?"
    si_max = si_cols[-1] if si_cols else "?"
    return "\n".join([
        "**보간 안내** (표 행·열 사이 값 추정)",
        "",
        f"- **지위지수 결정** — 임분의 임령과 측정 우세목 수고로 SI 판정. 측정 H가 인접 SI 두 열 값 H₁·H₂ 사이면: `SI = SI₁ + (SI₂ − SI₁) × (H − H₁) / (H₂ − H₁)`",
        "- **임령 사이 보간** — 임령 t가 표 행 t₁·t₂ 사이면: `H(t) = H(t₁) + (H(t₂) − H(t₁)) × (t − t₁) / (t₂ − t₁)`",
        f"- **표 범위 밖** — 본 표의 지위지수 범위는 {si_min}~{si_max}, 임령 범위는 표 첫·마지막 행 기준. 외삽은 권장하지 않으며, 곡선도(원본 PDF)의 점근 형태 확인 후 보수적으로 판단.",
        "",
    ])


def build_species_page(
    species: str,
    sec_ii: dict, sec_iv: dict, sec_vi: dict, sec_vii: dict, sec_viii: dict, sec_ix: dict, sec_x: dict,
) -> str:
    parts: list[str] = []
    parts.append(f"# {species}")
    parts.append("")
    parts.append(f"> 원본: `raw/manuals/2023년 입목재적·바이오매스 및 임분수확표.md`")
    parts.append(f"> 발행: 산림청·국립산림과학원, 2023")
    parts.append("")
    parts.append(f"이 페이지는 「2023 입목재적·바이오매스 및 임분수확표」에서 **{species}**가 등장하는 모든 표를 통합 수록한다.")
    parts.append("")
    parts.append("---")
    parts.append("")
    # Ⅱ
    parts.append("## Ⅱ. 입목수간재적표")
    parts.append("")
    if species in sec_ii:
        cols, rows = sec_ii[species]
        parts.append(render_matrix_md(
            title=f"입목수간재적표 ({KIND_II.get(species, '수피포함')})",
            row_label="수고(m)", col_label="흉고직경(cm)", unit="m³",
            cols=cols, rows=rows,
        ))
        parts.append("")
        parts.append("> 사용법: 흉고직경 열 × 수고 행 교차 셀이 단목 재적(m³). 표에 없는 값은 인접 값 선형 보간.")
    else:
        parts.append("*(해당 수종은 Ⅱ장에 등장하지 않음)*")
    parts.append("")
    parts.append("---")
    parts.append("")
    # Ⅳ
    parts.append("## Ⅳ. 입목 수간중량표 및 원목 이용중량표")
    parts.append("")
    if species in sec_iv:
        for kind, label in IV_SUBTABLES:
            if kind in sec_iv[species]:
                cols, rows = sec_iv[species][kind]
                parts.append(render_matrix_md(
                    title=label, row_label="수고(m)", col_label="흉고직경(cm)", unit="kg",
                    cols=cols, rows=rows,
                ))
                parts.append("")
    else:
        parts.append("*(해당 수종은 Ⅳ장에 등장하지 않음 — 등장 수종: 잣나무·낙엽송·리기다소나무·강원지방소나무·중부지방소나무·해송·상수리나무·신갈나무)*")
    parts.append("")
    parts.append("---")
    parts.append("")
    # Ⅵ
    parts.append("## Ⅵ. 입목 바이오매스표 + 부위별 전환계수")
    parts.append("")
    if species in sec_vi:
        cols, rows, coefs = sec_vi[species]
        parts.append(render_matrix_md(
            title="줄기(수피포함) 바이오매스표",
            row_label="수고(m)", col_label="흉고직경(cm)", unit="kg(건중량)",
            cols=cols, rows=rows,
        ))
        parts.append("")
        parts.append("**부위별 전환계수표** (줄기 바이오매스 × 계수 = 부위별 바이오매스)")
        parts.append("")
        parts.append("| 부위 | 전환계수 |")
        parts.append("|---|---:|")
        for k in ["가지", "잎", "뿌리"]:
            if k in coefs:
                parts.append(f"| {k} | {coefs[k]} |")
        parts.append("")
    else:
        parts.append("*(해당 수종은 Ⅵ장에 등장하지 않음 — 등장 12종: 침엽수 8 + 활엽수 4(상수리·굴참·신갈·자작))*")
    parts.append("")
    parts.append("---")
    parts.append("")
    # Ⅶ
    parts.append("## Ⅶ. 법정림 지위지수 분류표")
    parts.append("")
    key_vii = species if species in sec_vii else f"{species}(잠정)"
    if key_vii in sec_vii:
        cols, rows = sec_vii[key_vii]
        suffix = " (잠정)" if "(잠정)" in key_vii else ""
        parts.append(render_matrix_md(
            title=f"법정림 지위지수 분류표{suffix}",
            row_label="임령(년)", col_label="지위지수", unit="m (우세목 수고)",
            cols=cols, rows=rows,
        ))
        parts.append("")
        page = PDF_PAGE_VII.get(species.replace("(잠정)", ""))
        if page is not None:
            parts.append(f"> **원본 PDF**: {page}쪽 (분류표 + 곡선도) · `raw/manuals/2023년 입목재적·바이오매스 및 임분수확표.md`")
            parts.append("")
        parts.append(_interpolation_block(cols, "지위지수 결정"))
    else:
        parts.append("*(해당 수종은 Ⅶ장에 등장하지 않음)*")
    parts.append("")
    parts.append("---")
    parts.append("")
    # Ⅷ
    parts.append("## Ⅷ. 법정림 임분수확표")
    parts.append("")
    key_viii = species if species in sec_viii else f"{species}(잠정)"
    if key_viii in sec_viii:
        rows = sec_viii[key_viii]
        suffix = " (잠정)" if "(잠정)" in key_viii else ""
        parts.append(render_yield_md(f"법정림 임분수확표{suffix}", rows))
    else:
        parts.append("*(해당 수종은 Ⅷ장에 등장하지 않음)*")
    parts.append("")
    parts.append("---")
    parts.append("")
    # Ⅸ
    parts.append("## Ⅸ. 현실림 지위지수 분류표")
    parts.append("")
    if species in sec_ix:
        cols, rows = sec_ix[species]
        parts.append(render_matrix_md(
            title="현실림 지위지수 분류표",
            row_label="임령(년)", col_label="지위지수", unit="m (우세목 수고)",
            cols=cols, rows=rows,
        ))
        parts.append("")
        page = PDF_PAGE_IX.get(species)
        if page is not None:
            parts.append(f"> **원본 PDF**: {page}쪽 (분류표 + 곡선도) · 제5~6차 국가산림자원조사(NFI) 기반")
            parts.append("")
        parts.append(_interpolation_block(cols, "지위지수 결정"))
    else:
        parts.append("*(해당 수종은 Ⅸ장에 등장하지 않음)*")
    parts.append("")
    parts.append("---")
    parts.append("")
    # Ⅹ
    parts.append("## Ⅹ. 현실림 임분수확표")
    parts.append("")
    if species in sec_x:
        rows = sec_x[species]
        parts.append(render_yield_md("현실림 임분수확표", rows))
    else:
        parts.append("*(해당 수종은 Ⅹ장에 등장하지 않음)*")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("## 관련 wiki")
    parts.append("")
    parts.append("- [매뉴얼 인덱스](../index.md)")
    parts.append("- [Ⅰ. 서언 — 개정 배경·수록 내용](../00_서언_사용법.md)")
    parts.append("- [Ⅲ. 원목재적표 (Smalian)](../01_원목재적표.md)")
    parts.append("- [Ⅴ. 벌근직경 → 흉고직경 추정](../02_벌근직경_흉고직경_추정.md)")
    parts.append("- [[법령/산림자원법/시행규칙]] — 별표 3 기준벌기령")
    parts.append("- [[매뉴얼/지속가능한_산림자원관리_표준매뉴얼/4장_일반지침_2_다층_혼효_수확_안전]] — 수종별 기준 벌기령")
    parts.append("")
    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────────────────────

def main() -> int:
    if not RAW.exists():
        print(f"raw 미발견: {RAW}", file=sys.stderr)
        return 1
    SPECIES_DIR.mkdir(parents=True, exist_ok=True)

    text = RAW.read_text(encoding="utf-8")
    lines = text.splitlines()

    # 섹션 경계
    bounds = {}
    romans = ["Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ", "Ⅶ", "Ⅷ", "Ⅸ", "Ⅹ"]
    for idx, r in enumerate(romans):
        nxt = romans[idx + 1] if idx + 1 < len(romans) else "부록"
        # 부록은 'Ⅲ.', 'Ⅳ.' 등으로 재시작 — 라인 11900+에서 끝남, 임시로 Ⅹ까지만
        try:
            bounds[r] = find_section_bounds(lines, r, nxt if nxt != "부록" else None)
        except RuntimeError:
            bounds[r] = (0, 0)
    # Ⅹ는 부록 시작 전까지로 제한 — 부록의 'Ⅲ. 입목 수간중량표' 가 11919에 등장
    appendix_start = None
    for i, ln in enumerate(lines):
        if i > 11000 and ln.strip().startswith("Ⅲ. 입목 수간중량표"):
            appendix_start = i
            break
    if appendix_start:
        rs, re_ = bounds["Ⅹ"]
        bounds["Ⅹ"] = (rs, min(re_, appendix_start))
    # Ⅷ는 Ⅸ 시작까지, Ⅸ는 Ⅹ 시작까지 — find_section_bounds 가 이미 처리

    print(f"섹션 경계: {dict((k, v) for k, v in bounds.items())}")

    # ── Ⅱ. 입목수간재적표 ──
    sec_ii: dict = {}
    for sp in SPECIES_II:
        rng = find_chapter_in_section(lines, *bounds["Ⅱ"], sp)
        if rng is None:
            continue
        chunks = parse_matrix_chunks(lines, *rng)
        cols, rows = merge_chunks(chunks)
        if cols and rows:
            sec_ii[sp] = (cols, rows)

    # ── Ⅳ. 수간중량표 ──
    sec_iv: dict = {}
    for sp in SPECIES_IV:
        rng = find_chapter_in_section(lines, *bounds["Ⅳ"], sp)
        if rng is None:
            continue
        sub = parse_iv_subtables(lines, *rng)
        if sub:
            sec_iv[sp] = sub

    # ── Ⅵ. 바이오매스 ──
    sec_vi: dict = {}
    for sp in SPECIES_VI:
        rng = find_chapter_in_section(lines, *bounds["Ⅵ"], sp)
        if rng is None:
            continue
        chunks = parse_matrix_chunks(lines, *rng)
        cols, rows = merge_chunks(chunks)
        coefs = parse_conversion_coefs(lines, *rng)
        if cols and rows:
            sec_vi[sp] = (cols, rows, coefs)

    # ── Ⅶ. 법정림 지위지수 ──
    sec_vii: dict = {}
    for sp_full in SPECIES_VII:
        base = sp_full.replace("(잠정)", "")
        # 챕터 마커는 "수종명(잠정)" 또는 "수종명"
        rng = find_chapter_in_section(lines, *bounds["Ⅶ"], sp_full)
        if rng is None:
            rng = find_chapter_in_section(lines, *bounds["Ⅶ"], base)
        if rng is None:
            continue
        chunks = parse_matrix_chunks(lines, *rng, integer_col_max_diff=10, min_cols=3)
        cols, rows = merge_chunks(chunks)
        if cols and rows:
            sec_vii[sp_full] = (cols, rows)

    # ── Ⅷ. 법정림 임분수확표 ──
    sec_viii: dict = {}
    for sp_full in SPECIES_VIII:
        rng = find_chapter_in_section(lines, *bounds["Ⅷ"], sp_full)
        if rng is None:
            rng = find_chapter_in_section(lines, *bounds["Ⅷ"], sp_full.replace("(잠정)", ""))
        if rng is None:
            continue
        rows = parse_yield_table(lines, *rng)
        if rows:
            sec_viii[sp_full] = rows

    # ── Ⅸ. 현실림 지위지수 ──
    sec_ix: dict = {}
    for sp in SPECIES_IX:
        rng = find_chapter_in_section(lines, *bounds["Ⅸ"], sp)
        if rng is None:
            continue
        chunks = parse_matrix_chunks(lines, *rng, integer_col_max_diff=10, min_cols=3)
        cols, rows = merge_chunks(chunks)
        if cols and rows:
            sec_ix[sp] = (cols, rows)

    # ── Ⅹ. 현실림 임분수확표 ──
    sec_x: dict = {}
    for sp in SPECIES_X:
        rng = find_chapter_in_section(lines, *bounds["Ⅹ"], sp)
        if rng is None:
            continue
        rows = parse_yield_table(lines, *rng)
        if rows:
            sec_x[sp] = rows

    # 진단
    print(f"  Ⅱ: {len(sec_ii)}/{len(SPECIES_II)}수종")
    print(f"  Ⅳ: {len(sec_iv)}/{len(SPECIES_IV)}수종")
    print(f"  Ⅵ: {len(sec_vi)}/{len(SPECIES_VI)}수종")
    print(f"  Ⅶ: {len(sec_vii)}/{len(SPECIES_VII)}수종")
    print(f"  Ⅷ: {len(sec_viii)}/{len(SPECIES_VIII)}수종")
    print(f"  Ⅸ: {len(sec_ix)}/{len(SPECIES_IX)}수종")
    print(f"  Ⅹ: {len(sec_x)}/{len(SPECIES_X)}수종")

    # 수종 페이지 생성
    written = 0
    for sp in SPECIES_ORDER:
        page = build_species_page(sp, sec_ii, sec_iv, sec_vi, sec_vii, sec_viii, sec_ix, sec_x)
        (SPECIES_DIR / f"{sp}.md").write_text(page, encoding="utf-8")
        written += 1
    print(f"수종 페이지 {written}개 생성")

    # ── Ⅲ. 원목재적표 (표준페이지) ──
    log_blocks = find_log_category_blocks(lines, *bounds["Ⅲ"])
    log_md = build_log_volume_page(lines, log_blocks)
    (MANUAL_DIR / "01_원목재적표.md").write_text(log_md, encoding="utf-8")
    print(f"01_원목재적표.md 생성 ({len(log_blocks)}/4 카테고리)")

    # ── Ⅴ. 벌근직경 → 흉고직경 (표준페이지) ──
    bk_md = build_bunkeun_page(lines, *bounds["Ⅴ"])
    (MANUAL_DIR / "02_벌근직경_흉고직경_추정.md").write_text(bk_md, encoding="utf-8")
    print("02_벌근직경_흉고직경_추정.md 생성")

    return 0


def build_log_volume_page(lines: list[str], blocks: dict[str, tuple[int, int]]) -> str:
    parts = [
        "# Ⅲ. 원목재적표 (Smalian식)",
        "",
        "> 원본: `raw/manuals/2023년 입목재적·바이오매스 및 임분수확표.md` Ⅲ장",
        "> 산식: **Smalian식 (양단면적식)** — 2009년판 말구직경자승법의 과소·과대 추정 문제를 보완.",
        "",
        "## 사용법",
        "",
        "1. **원목 길이 측정**: 벌근 단면 가까운 원구에서 시작, 최첨두까지(짧은 끝 단면이 0이 아닌 지점까지).",
        "2. **말구직경 측정 (mm)**: 용도에 따라 원목을 조제한 후, 최첨두 부위 측정.",
        "3. **카테고리 선택**: 소나무·낙엽송은 전용 표, 그 외 침엽수는 「기타침엽수」, 그 외 활엽수는 「기타활엽수」.",
        "4. **표 검색**: 말구직경(mm) 행 × 길이(m) 열 교차 셀이 원목재적(㎥).",
        "",
        "> 예: 낙엽송 말구직경 300 mm, 원목길이 1.8 m → 0.1481 ㎥",
        "",
        "---",
        "",
    ]
    for cat in LOG_CATEGORIES:
        rng = blocks.get(cat)
        parts.append(f"## {cat}")
        parts.append("")
        if rng is None:
            parts.append("*(파싱 실패 — 원본 참조)*")
            parts.append("")
            continue
        chunks = parse_matrix_chunks(lines, rng[0], rng[1], allow_float_cols=True)
        cols, rows = merge_chunks(chunks)
        if cols and rows:
            parts.append(render_matrix_md(
                title=f"{cat} 원목재적표",
                row_label="말구직경(mm)", col_label="길이(m)", unit="㎥",
                cols=cols, rows=rows,
            ))
        else:
            parts.append("*(파싱 실패 — 원본 참조)*")
        parts.append("")
        parts.append("---")
        parts.append("")
    parts.append("## 관련 wiki")
    parts.append("")
    parts.append("- [매뉴얼 인덱스](index.md)")
    parts.append("- [Ⅰ. 서언 — 개정 배경](00_서언_사용법.md)")
    parts.append("- [[법령/산림자원법/시행규칙]] — 별표 3 기준벌기령")
    parts.append("")
    return "\n".join(parts)


def build_bunkeun_page(lines: list[str], sec_start: int, sec_end: int) -> str:
    coni_sp, coni_rows, broad_sp, broad_rows = parse_bunkeun_table(lines, sec_start, sec_end)
    parts = [
        "# Ⅴ. 벌근직경 → 흉고직경 추정",
        "",
        "> 원본: `raw/manuals/2023년 입목재적·바이오매스 및 임분수확표.md` Ⅴ장",
        "> 정의: **벌근직경** = 지면으로부터 0.2 m 높이에서 벌채된 입목의 수피포함 직경",
        "",
        "## 사용법",
        "",
        "1. 수종을 구분하여 **벌근직경**(그루터기의 직경)을 측정하고 2 cm로 괄약.",
        "2. 아래 표에서 흉고직경을 검색.",
        "",
        "> 예: 강원지방소나무 벌근직경 20 cm → 흉고직경 **16.5 cm**",
        "",
        "---",
        "",
        "## 침엽수 (5수종)",
        "",
    ]
    if coni_sp and coni_rows:
        header = "| 벌근직경(cm) | " + " | ".join(coni_sp) + " |"
        sep = "|---:|" + "|".join("---:" for _ in coni_sp) + "|"
        parts.append(header)
        parts.append(sep)
        for h, vals in coni_rows:
            parts.append(f"| **{h}** | " + " | ".join(vals) + " |")
        parts.append("")
        parts.append("> 단위: cm | 값 = 추정 흉고직경")
    else:
        parts.append("*(파싱 실패)*")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("## 활엽수 + 편백 (6수종)")
    parts.append("")
    parts.append("> 활엽수 5수종(상수리·굴참·신갈·자작·백합) + 침엽수 편백. OCR 헤더는 '활엽수'로 표기되지만 편백은 침엽수임에 주의.")
    parts.append("")
    if broad_sp and broad_rows and coni_rows:
        # 벌근직경은 침엽수 페이지에서 가져옴 (페이지 2에는 컬럼이 없음, 행 수가 일치해야 함)
        bunkeun_vals = [h for h, _ in coni_rows]
        if len(bunkeun_vals) == len(broad_rows):
            header = "| 벌근직경(cm) | " + " | ".join(broad_sp) + " |"
            sep = "|---:|" + "|".join("---:" for _ in broad_sp) + "|"
            parts.append(header)
            parts.append(sep)
            for bk, vals in zip(bunkeun_vals, broad_rows):
                parts.append(f"| **{bk}** | " + " | ".join(vals) + " |")
            parts.append("")
            parts.append("> 단위: cm | 값 = 추정 흉고직경")
        else:
            parts.append(f"*(파싱 부분 실패 — 침엽수 {len(bunkeun_vals)}행 vs 활엽수 {len(broad_rows)}행)*")
    else:
        parts.append("*(파싱 실패)*")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("## 관련 wiki")
    parts.append("")
    parts.append("- [매뉴얼 인덱스](index.md)")
    parts.append("- [Ⅲ. 원목재적표 (Smalian)](01_원목재적표.md)")
    parts.append("")
    return "\n".join(parts)


if __name__ == "__main__":
    sys.exit(main())
