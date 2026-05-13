# FM-WIKI — 산림경영 실무 위키

산림청 지침·행정규칙을 기반으로 **조림·숲가꾸기·벌채·산림계획** 실무자가 Claude에게 질문하고 즉시 판단 근거를 얻을 수 있는 팀 공유 위키입니다.

## 구조

```
FM wiki/
├── wiki/          ← 위키 본문 (이 저장소가 관리하는 파일)
│   ├── index.md   ← 전체 페이지 카탈로그
│   ├── log.md     ← 인제스트·쿼리·린트 이력
│   ├── 행정규칙/  ← 행정규칙 원문 wiki화 (훈령·고시·예규·지침)
│   ├── 산림작업/  ← 조림·숲가꾸기·벌채 실무 기준
│   └── 산림계획/  ← 경영계획·수확조절 기준
├── raw/           ← 소스 레이어 (별도 세팅 필요, git 미포함)
└── CLAUDE.md      ← 운영 스키마 (Claude 지시문)
```

## raw/ 세팅 방법

`raw/`는 git에 포함되지 않습니다. 아래 sparse clone으로 직접 구성하세요.

```bash
mkdir raw
git clone --filter=blob:none --sparse https://github.com/legalize-kr/admrule-kr.git raw/admrule-kr
git clone --filter=blob:none --sparse https://github.com/legalize-kr/legalize-kr.git raw/legalize-kr
```

## Claude와 함께 핸드폰이나 PC에서 사용하기 (유료사용자 전용)

<PC에서 사용할때>
1. https://claude.com/download 로 접속
2. Download for Windows 를 클릭해서 설치
3. 유료일 경우는 프로그램 실행 후 좌측 상단 </>code를 클릭
4. 새세션을 실행하고, 채팅창에 "https://github.com/chinguli4/FM-WIKI 를 연결해줘" 입력
5. `wiki/index.md`를 참고해 관련 페이지를 파악
6. 질문하면 Claude가 관련 wiki 페이지와 조항을 인용해 답변
   
<핸드폰에서 사용할때>
1. 핸드폰에서 Claude App을 설치하고
2. Claude App에서 </>코드를 선택
3. 새세션을 실행하고, 채팅창에 "https://github.com/chinguli4/FM-WIKI 를 연결해줘" 입력
4. `wiki/index.md`를 참고해 관련 페이지를 파악
5. 질문하면 Claude가 관련 wiki 페이지와 조항을 인용해 답변

## claude.ai Projects로 팀 공유 (무료 플랜)

GitHub 연결 없이 **claude.ai 무료 계정**에서 wiki를 사용하는 방법입니다.

1. `export-for-project.bat` 더블클릭 → 프로젝트 루트에 `export_flat/` 폴더 생성
2. [claude.ai](https://claude.ai) → **Projects** → 새 프로젝트 만들기
3. `export_flat/` 안의 `.md` 파일 전체 선택(Ctrl+A) → 프로젝트에 업로드
4. 이후 해당 프로젝트에서 질문하면 wiki 내용을 참고해 답변

> wiki가 업데이트될 때마다 bat 파일을 다시 실행하고 프로젝트 파일을 교체 업로드하세요.

## 수록 행정규칙

`wiki/index.md` 참조 — 훈령·고시·예규·지침 다수 수록

## 공동작업

수정요청·권한 안내는 [협업 가이드](wiki/협업가이드.md)를 참조하세요.

## 업데이트

새 행정규칙 인제스트 또는 개정 반영 시 `wiki/log.md`에 이력이 기록됩니다.
