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

## Claude와 함께 핸드폰이나 PC에서 사용하기
<PC에서 사용할때는 무료로 사용가능, 유료가 편리하긴 함>
1. https://claude.com/download 로 접속
2. Download for Windows 를 클릭해서 설치
3. 무료일 경우는 프로그램에서 채팅방에서 바로 5.번을 실행
4. 유료일 경우는 프로그램 실행 후 좌측 상단 </>code를 클릭
5. 새세션을 실행하고, 채팅창에 "https://github.com/chinguli4/FM-WIKI 를 연결해줘" 입력
6. `wiki/index.md`를 참고해 관련 페이지를 파악
7. 질문하면 Claude가 관련 wiki 페이지와 조항을 인용해 답변
   
<핸드폰에서 사용할때는 Pro 이상 유료사용자만 가능>
1. 핸드폰에서 Claude App을 설치하고
2. Claude App에서 </>코드를 선택
3. 새세션을 실행하고, 채팅창에 "https://github.com/chinguli4/FM-WIKI를 연결해줘" 입력
4. `wiki/index.md`를 참고해 관련 페이지를 파악
5. 질문하면 Claude가 관련 wiki 페이지와 조항을 인용해 답변

## 수록 행정규칙

`wiki/index.md` 참조 — 훈령·고시·예규·지침 다수 수록

## 공동작업

수정요청·권한 안내는 [협업 가이드](wiki/협업가이드.md)를 참조하세요.

## 업데이트

새 행정규칙 인제스트 또는 개정 반영 시 `wiki/log.md`에 이력이 기록됩니다.
