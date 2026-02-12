# Qnnection 💬

> **Question + Connection** – 교회 모임 아이스브레이킹 & 스피드게임 TV 앱

프로젝터/TV에 질문을 크게 띄워 모임을 이끌어가는 Streamlit 웹앱입니다.  
운영자는 **CSV 질문 파일만 추가/수정**하면 되고, 앱 코드는 그대로 재사용할 수 있습니다.

---

## 🚀 실행 방법

```bash
# uv 사용 (권장)
uv venv qnnection
qnnection\Scripts\Activate        # Windows
# source qnnection/bin/activate   # macOS/Linux
uv pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 자동 열립니다.

---

## 🎮 모드

### 아이스브레이킹 모드
- 사이드바에서 CSV 질문 세트를 **복수 선택**하여 질문 풀 구성
- **Queue** → 질문이 화면 가득 크게 표시
- **Skip** → 다음 질문 뽑기
- **Prev / Next** → 세션 히스토리 탐색 (이전에 나온 질문 다시 보기)
- **🔀 덱 구성 / 셔플** → 새로운 순서로 덱 재생성
- **🗑 초기화** → 세션 히스토리 포함 전체 리셋
- 📋 **세션 히스토리** 목록에서 사용된 질문 전체 확인 가능

### 스피드게임 모드
- 타이머 프리셋(30/60/90초) 또는 직접 입력으로 설정
- **Start** → 타이머 시작 + 첫 카드 표시
- **Correct(+1)** → 정답 처리 + 다음 카드
- **Pass** → 패스 + 다음 카드
- **Undo** → 직전 판정 되돌리기
- **Pause / Resume** → 일시정지
- **Stop** → 즉시 라운드 종료
- 라운드 종료 시 **점수 요약 + 사용 카드 목록** 확인

---

## ⚙️ 공통 기능

| 기능 | 설명 |
|------|------|
| **표시 언어** | `KO only`, `EN only`, `KO → EN`, `EN → KO` 중 선택 |
| **필터** | 카테고리, 깊이(1~5), 난이도(1~3), 태그로 질문 풀 조절 |
| **덱 크기** | 세션에서 사용할 총 질문 수 지정 (0 = 전체) |
| **중복 방지** | 덱 소진 전까지 같은 질문 반복 없음 |
| **오류 안내** | CSV 누락/컬럼 오류 시 친절한 에러 메시지 표시 |

---

## 📂 CSV 질문 추가

폴더에 CSV 파일을 넣으면 앱이 자동으로 인식합니다.

```
decks/
├── icebreaker/          ← 아이스브레이킹 질문 세트
│   └── *.csv
└── speedgame/           ← 스피드게임 덱 (파일별로 덱 분리)
    ├── bible_characters.csv
    ├── worship_songs.csv
    └── church_terms.csv
```

### CSV 컬럼

| 컬럼 | 필수 | 설명 |
|------|------|------|
| `id` | ✅ | 세트 내 고유 ID |
| `ko` | ✅ | 한국어 질문 |
| `en` | ✅ | 영어 질문 |
| `category` | | 카테고리 (fun, daily, faith, …) |
| `depth` | | 깊이 1~5 (기본 1) |
| `difficulty` | | 난이도 1~3 (기본 1) |
| `tags` | | 세미콜론(;) 구분 태그 |
| `enabled` | | 0/1 비활성/활성 (기본 1) |

> 권장 컬럼은 없어도 앱이 동작합니다. 기본값으로 자동 대체됩니다.

---

## 🎨 프로젝터 최적화

`.streamlit/config.toml`에서 다크 테마 + UI 최소화가 기본 설정되어 있습니다.

- 큰 글자, 중앙 정렬, 고대비 색상
- Streamlit 헤더/푸터 숨김
- Noto Sans KR 웹폰트 사용