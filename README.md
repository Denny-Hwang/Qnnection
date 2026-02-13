# Qnnection 💬

> **Question + Connection** – 교회 아이스브레이킹 & 스피드게임 TV 앱
> **Question + Connection** – Icebreaker & Speed Game TV App for Gatherings

프로젝터/TV에 질문을 크게 띄워 모임을 이끌어가는 Streamlit 웹앱입니다.
운영자는 **CSV 질문 파일만 추가/수정**하면 되고, 앱 코드는 그대로 재사용할 수 있습니다.

A Streamlit web app that displays questions on a projector/TV to lead group gatherings.
Administrators only need to **add or edit CSV question files** — the app code stays unchanged and reusable.

---

## 🚀 실행 방법 | Getting Started

```bash
# uv 사용 (권장) | Using uv (recommended)
uv venv qnnection
source qnnection/bin/activate        # macOS / Linux
# qnnection\Scripts\Activate         # Windows
uv pip install -r requirements.txt
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 자동 열립니다.
The app opens automatically at `http://localhost:8501`.

---

## 📁 프로젝트 구조 | Project Structure

```
Qnnection/
├── app.py                 # 메인 앱 | Main application
├── requirements.txt       # 의존성 | Dependencies
├── .streamlit/
│   └── config.toml        # 테마 / 서버 설정 | Theme & server config
├── core/                  # 핵심 모듈 | Core modules
│   ├── loader.py          #   CSV 스캔·로드·검증 | CSV scan, load, validate
│   ├── filtering.py       #   필터링 로직 | Filtering logic
│   ├── deck.py            #   덱 생성·드로우·히스토리 | Deck build, draw, history
│   ├── state.py           #   세션 상태 관리 | Session state management
│   ├── ui_styles.py       #   CSS·카드 HTML 생성 | CSS & card HTML generation
│   └── i18n.py            #   한/영 번역 (200+ 키) | KO/EN translations (200+ keys)
└── decks/                 # 질문 데이터 | Question data
    ├── icebreaker/        #   아이스브레이킹 세트 | Icebreaker sets
    │   └── church_gathering_a.csv
    └── speedgame/         #   스피드게임 덱 | Speed game decks
        ├── bible_characters.csv
        ├── worship_songs.csv
        └── church_terms.csv
```

---

## 🎮 모드 | Modes

### 아이스브레이킹 | Icebreaker

사이드바에서 CSV 질문 세트를 **복수 선택**하여 질문 풀을 구성합니다.
Select one or more CSV question sets from the sidebar to build a question pool.

| 버튼 | Button | 설명 | Description |
|------|--------|------|-------------|
| **▶️ Queue** | **▶️ Queue** | 질문을 화면에 크게 표시 | Display the next question on screen |
| **⏭ Skip** | **⏭ Skip** | 다음 질문 뽑기 | Draw the next question |
| **⬅ Prev / ➡ Next** | **⬅ Prev / ➡ Next** | 세션 히스토리 탐색 | Navigate session history |
| **🔀 덱 구성 / 셔플** | **🔀 Build / Shuffle** | 새로운 순서로 덱 재생성 | Rebuild deck in a new order |
| **🗑 초기화** | **🗑 Reset** | 히스토리 포함 전체 리셋 | Full reset including history |

📋 **세션 히스토리** 목록에서 사용된 질문 전체를 확인할 수 있습니다.
📋 View all used questions in the **Session History** list.

### 스피드게임 | Speed Game

타이머 프리셋(30/60/90초) 또는 직접 입력으로 시간을 설정합니다.
Set the timer using presets (30/60/90 sec) or enter a custom value.

| 버튼 | Button | 설명 | Description |
|------|--------|------|-------------|
| **▶️ Start** | **▶️ Start** | 타이머 시작 + 첫 카드 표시 | Start timer and show first card |
| **✅ 정답 (+1)** | **✅ Correct (+1)** | 정답 처리 + 다음 카드 | Mark correct and advance |
| **⏭ Pass** | **⏭ Pass** | 패스 + 다음 카드 | Pass and advance |
| **↩ Undo** | **↩ Undo** | 직전 판정 되돌리기 | Undo the last action |
| **⏸ Pause / ▶️ Resume** | **⏸ Pause / ▶️ Resume** | 일시정지 / 재개 | Pause or resume |
| **⏹ Stop** | **⏹ Stop** | 즉시 라운드 종료 | End the round immediately |

라운드 종료 시 **점수 요약 + 사용 카드 목록**이 표시됩니다.
When the round ends, a **score summary and card list** are displayed.

---

## ⚙️ 공통 기능 | Common Features

| 기능 | Feature | 설명 | Description |
|------|---------|------|-------------|
| **표시 언어** | **Display Language** | `KO only`, `EN only`, `KO → EN`, `EN → KO` 중 선택 | Choose from 4 bilingual display modes |
| **필터** | **Filters** | 카테고리, 깊이(1~5), 난이도(1~3), 태그 | Category, depth (1–5), difficulty (1–3), tags |
| **덱 크기** | **Deck Size** | 세션에서 사용할 총 질문 수 (0 = 전체) | Total questions per session (0 = all) |
| **셔플** | **Shuffle** | 랜덤 순서 토글 | Toggle random order on/off |
| **중복 방지** | **No Repeats** | 덱 소진 전까지 같은 질문 반복 없음 | No duplicate questions until deck is exhausted |
| **UI 언어** | **UI Language** | 한국어 / English UI 전환 | Switch between Korean and English UI |
| **오류 안내** | **Error Guidance** | CSV 누락/컬럼 오류 시 에러 메시지 표시 | Friendly error messages for CSV issues |

---

## 📂 CSV 질문 추가 | Adding Questions

폴더에 CSV 파일을 넣으면 앱이 자동으로 인식합니다.
Drop CSV files into the folder and the app picks them up automatically.

```
decks/
├── icebreaker/          ← 아이스브레이킹 | Icebreaker questions
│   └── *.csv
└── speedgame/           ← 스피드게임 | Speed game decks
    └── *.csv
```

### CSV 컬럼 | CSV Columns

| 컬럼 Column | 필수 Required | 설명 | Description |
|------|------|------|-------------|
| `id` | ✅ | 세트 내 고유 ID | Unique ID within the set |
| `ko` | ✅ | 한국어 질문/단어 | Korean question or word |
| `en` | ✅ | 영어 질문/단어 | English question or word |
| `category` | | 카테고리 (fun, daily, faith, …) | Category label |
| `depth` | | 깊이 1~5 (기본 1) | Depth 1–5 (default 1) |
| `difficulty` | | 난이도 1~3 (기본 1) | Difficulty 1–3 (default 1) |
| `tags` | | 세미콜론(`;`) 구분 태그 | Semicolon-separated tags |
| `enabled` | | 0 비활성 / 1 활성 (기본 1) | 0 disabled / 1 enabled (default 1) |

> 선택 컬럼은 없어도 앱이 동작합니다. 기본값으로 자동 대체됩니다.
> Optional columns can be omitted. The app fills in defaults automatically.

### CSV 예시 | CSV Example

```csv
id,ko,en,category,depth,difficulty,tags,enabled
q01,요즘 감사한 일 한 가지는?,What is one thing you are grateful for?,faith,2,1,감사;신앙,1
q02,나를 동물에 비유한다면?,If you were an animal what would you be?,fun,1,1,상상;자기소개,1
```

---

## 🎨 프로젝터 최적화 | Projector Optimization

`.streamlit/config.toml`에서 다크 테마 + UI 최소화가 기본 설정되어 있습니다.
Dark theme and minimal UI are pre-configured in `.streamlit/config.toml`.

- 큰 글자, 중앙 정렬, 고대비 색상 | Large text, centered layout, high contrast colors
- Streamlit 헤더/푸터 숨김 | Streamlit header and footer hidden
- Noto Sans KR 웹폰트 (한글 최적화) | Noto Sans KR web font for Korean text
- 타이머 색상 표시: 초록 → 노랑 → 빨강(깜박임) | Timer color coding: green → yellow → red (pulsing)

---

## 🛠 기술 스택 | Tech Stack

| | |
|---|---|
| **언어 Language** | Python 3 |
| **프레임워크 Framework** | Streamlit ≥ 1.30 |
| **데이터 Data** | pandas ≥ 2.0 |
| **스타일 Styling** | Custom CSS, Noto Sans KR |
| **설정 Config** | `.streamlit/config.toml` |
