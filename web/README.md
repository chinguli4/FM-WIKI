# 산림경영 Wiki 웹 포털

`wiki/`의 마크다운 문서를 빌드 시 자동으로 읽어 카드형 대문, 통합검색, 문서 열람 화면을 생성한다.

## 구성 원칙

- 문서 원본은 계속 `wiki/`와 GitHub에서 관리한다.
- 별도 데이터베이스는 사용하지 않는다.
- `main` 브랜치가 갱신되면 Netlify가 검색 인덱스를 다시 생성한다.
- AI 질문은 공개 NotebookLM을 새 창으로 연다.

## Netlify 설정

저장소 루트의 `netlify.toml`을 자동으로 사용한다.

- Build command: `node web/scripts/build-site.mjs`
- Publish directory: `web/dist`

