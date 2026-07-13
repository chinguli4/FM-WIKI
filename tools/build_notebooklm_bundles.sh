#!/usr/bin/env bash
# FM Wiki — NotebookLM 업로드용 묶음 빌드 스크립트
#
# 사용법:
#   bash tools/build_notebooklm_bundles.sh
#
# 결과: bundles/ 폴더에 6개 .md 파일 생성
#   - FM_Wiki_행정규칙.md
#   - FM_Wiki_매뉴얼.md
#   - FM_Wiki_산림작업.md
#   - FM_Wiki_산림계획.md
#   - FM_Wiki_법령.md
#   - FM_Wiki_타부처법령.md
#
# 생성된 파일을 NotebookLM (notebooklm.google.com) 새 노트북에
# 끌어다 놓으면 위키 전체를 한 번에 올릴 수 있습니다.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WIKI_DIR="$SCRIPT_DIR/../wiki"
OUTPUT_DIR="$SCRIPT_DIR/../bundles"

mkdir -p "$OUTPUT_DIR"

write_separator() {
  local rel="$1"
  local output="$2"
  {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "원본 경로: wiki/${rel}"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
  } >> "$output"
}

bundle_folder() {
  local folder="$1"
  local extra_files="${2:-}"
  local output="$OUTPUT_DIR/FM_Wiki_${folder}.md"

  {
    echo "# FM Wiki — ${folder} 묶음 (NotebookLM 업로드용)"
    echo ""
    echo "wiki/${folder}/ 아래 모든 페이지를 자동으로 합친 묶음입니다."
    echo ""
    echo "- 생성일: $(date '+%Y-%m-%d %H:%M')"
    echo "- 원본 저장소: https://github.com/chinguli4/FM-WIKI"
    echo ""
    echo "각 페이지 시작에 \`원본 경로:\` 표시가 있어 GitHub 원문을 추적할 수 있습니다."
  } > "$output"

  local count=0

  # Extra files at wiki root (예: 법령체계.md를 법령 묶음에 포함)
  if [[ -n "$extra_files" ]]; then
    for extra in $extra_files; do
      local extra_path="$WIKI_DIR/$extra"
      if [[ -f "$extra_path" ]]; then
        write_separator "$extra" "$output"
        cat "$extra_path" >> "$output"
        echo "" >> "$output"
        count=$((count + 1))
      fi
    done
  fi

  # 폴더 내 모든 .md
  while IFS= read -r file; do
    local rel="${file#$WIKI_DIR/}"
    write_separator "$rel" "$output"
    cat "$file" >> "$output"
    echo "" >> "$output"
    count=$((count + 1))
  done < <(find "$WIKI_DIR/$folder" -name "*.md" | sort)

  local size
  size=$(wc -c < "$output")
  printf "  ✓ FM_Wiki_%s.md — %d개 페이지, %d KB\n" "$folder" "$count" "$((size / 1024))"
}

echo ""
echo "📦 FM Wiki NotebookLM 묶음 빌드"
echo ""

# 매뉴얼은 단일 파일이 NotebookLM 소스 한도에 걸릴 수 있어 매뉴얼별로 분할한다.
bundle_manuals_split() {
  local manual_root="$WIKI_DIR/매뉴얼"
  while IFS= read -r sub; do
    local name
    name="$(basename "$sub")"
    local output="$OUTPUT_DIR/FM_Wiki_매뉴얼_${name}.md"
    {
      echo "# FM Wiki — 매뉴얼: ${name} (NotebookLM 업로드용)"
      echo ""
      echo "wiki/매뉴얼/${name}/ 아래 모든 페이지를 합친 묶음입니다."
      echo ""
      echo "- 생성일: $(date '+%Y-%m-%d %H:%M')"
      echo "- 원본 저장소: https://github.com/chinguli4/FM-WIKI"
      echo ""
      echo "각 페이지 시작에 \`원본 경로:\` 표시가 있어 GitHub 원문을 추적할 수 있습니다."
    } > "$output"

    local count=0
    while IFS= read -r file; do
      local rel="${file#$WIKI_DIR/}"
      write_separator "$rel" "$output"
      cat "$file" >> "$output"
      echo "" >> "$output"
      count=$((count + 1))
    done < <(find "$sub" -name "*.md" | sort)

    local size
    size=$(wc -c < "$output")
    printf "  ✓ FM_Wiki_매뉴얼_%s.md — %d개 페이지, %d KB\n" "$name" "$count" "$((size / 1024))"
  done < <(find "$manual_root" -mindepth 1 -maxdepth 1 -type d | sort)
}

# 전체 페이지 카탈로그(index.md)를 NotebookLM이 주제 지도로 쓸 수 있게 단독 묶음으로 포함
bundle_index() {
  local output="$OUTPUT_DIR/FM_Wiki_색인.md"
  {
    echo "# FM Wiki — 전체 색인 (NotebookLM 업로드용)"
    echo ""
    echo "wiki/index.md — 전체 페이지 카탈로그와 한 줄 요약입니다. 어떤 주제가 어느 페이지에 있는지 파악하는 지도로 사용하세요."
    echo ""
    echo "- 생성일: $(date '+%Y-%m-%d %H:%M')"
    echo "- 원본 저장소: https://github.com/chinguli4/FM-WIKI"
  } > "$output"
  write_separator "index.md" "$output"
  cat "$WIKI_DIR/index.md" >> "$output"
  echo "" >> "$output"
  local size
  size=$(wc -c < "$output")
  printf "  ✓ FM_Wiki_색인.md — 1개 페이지, %d KB\n" "$((size / 1024))"
}

bundle_index
bundle_folder "행정규칙"
bundle_manuals_split
bundle_folder "산림작업"
bundle_folder "산림계획"
bundle_folder "법령" "법령체계.md"
bundle_folder "타부처법령"

echo ""
echo "✅ 완료. 출력 위치: bundles/"
echo ""
echo "다음 단계:"
echo "  1. notebooklm.google.com 접속 → 새 노트북 만들기"
echo "  2. bundles/ 폴더의 모든 .md 파일을 끌어다 놓기 (매뉴얼은 매뉴얼별 분할)"
echo "  3. 질문 시작"
echo ""
