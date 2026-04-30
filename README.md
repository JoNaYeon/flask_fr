# flask_fr

Flask 기반 간단한 테스트 웹 애플리케이션. **계층형 아키텍처(Layered Architecture)** 를 학습/연습하기 위한 미니 프로젝트입니다.

## Quick Start

```bash
pip install -r requirements.txt
python3 app.py
```

서버는 http://127.0.0.1:5001 에서 동작합니다. (macOS에서 5000 포트는 AirPlay Receiver가 점유하므로 5001 사용)

### 엔드포인트

| Method | Path                | 설명                                 |
| ------ | ------------------- | ------------------------------------ |
| GET    | `/`                 | 메인 페이지 (Ping/Echo 테스트 UI)    |
| GET    | `/items`            | `data/items.json` 내용을 표 형태로 |
| GET    | `/api/ping`         | 서버 상태 확인 (현재 시간 반환)      |
| POST   | `/api/echo`         | 받은 JSON을 그대로 돌려보냄          |
| GET    | `/api/items`        | 전체 아이템 JSON                     |
| GET    | `/api/items/<id>`   | 단건 조회 (없으면 404)               |

---

## Flask란

Flask는 Python의 **마이크로 웹 프레임워크**입니다. "마이크로"는 기능이 부족하다는 뜻이 아니라, **핵심만 제공하고 나머지는 개발자가 선택**하도록 설계됐다는 의미입니다.

핵심 구성요소:

- **WSGI 앱 객체**: `Flask(__name__)`이 만드는 객체가 곧 웹 애플리케이션
- **라우팅**: URL과 함수를 매핑 (`@app.route("/")`)
- **Jinja2 템플릿**: HTML 파일에 Python 표현식을 삽입할 수 있는 템플릿 엔진
- **요청/응답 객체**: `request`, `jsonify` 등으로 HTTP를 추상화
- **Blueprint**: 라우트를 모듈 단위로 분리하기 위한 메커니즘

이 프로젝트에서 사용한 Flask 패턴은 다음과 같습니다.

### 1. 앱 팩토리(Application Factory) 패턴

[app.py](app.py)에서 `Flask` 객체를 모듈 최상단에서 즉시 만들지 않고 `create_app()` 함수 안에서 생성합니다.

```python
def create_app():
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.register_blueprint(main_bp)
    ...
    return app
```

**왜 함수로 감쌌나?**
- 테스트 환경에서 별도의 설정으로 앱을 새로 만들 수 있음
- 순환 import 문제를 피할 수 있음 (확장이 늘어났을 때 중요해짐)
- 여러 인스턴스를 띄울 수 있음 (예: 백엔드/관리자용 두 개)

### 2. Blueprint로 라우트 분리

[routes/main_routes.py](routes/main_routes.py)에서 `Blueprint("main", __name__)`을 만들고 라우트들을 여기에 등록합니다. `app.py`는 이 Blueprint를 `register_blueprint`로 가져다 붙입니다.

**왜?** 라우트가 늘어나면 `app.py` 하나에 모두 적는 것은 금방 한계에 부딪힙니다. Blueprint는 라우트를 도메인별로(예: `auth_routes.py`, `admin_routes.py`) 쪼갤 수 있게 해줍니다.

### 3. Jinja2 템플릿

`templates/` 폴더 아래 `.html` 파일들은 Jinja2 문법으로 동적 데이터를 렌더링합니다.

```html
{% for item in items %}
<tr><td>{{ item.id }}</td><td>{{ item.name }}</td></tr>
{% endfor %}
```

`render_template("items.html", items=...)`을 호출하면 Flask가 자동으로 `templates/` 폴더에서 파일을 찾고 컨텍스트를 주입합니다.

---

## 프로젝트 구조

```
flask_fr/
├── app.py                  # 앱 팩토리, 진입점
├── requirements.txt
├── data/                   # 영속 데이터 (JSON 파일)
│   └── items.json
├── models/                 # 데이터 클래스/스키마 (현재 비어있음)
├── repositories/           # 데이터 접근 계층 (Data Access Layer)
│   ├── __init__.py
│   └── repositoryManager.py
├── services/               # 비즈니스 로직 계층 (Service Layer)
│   ├── __init__.py
│   └── item_service.py
├── routes/                 # HTTP 계층 (Controller)
│   ├── __init__.py
│   └── main_routes.py
├── scripts/                # 일회성 유틸 스크립트 (마이그레이션 등)
├── static/                 # 정적 자산
│   ├── css/style.css
│   └── js/script.js
└── templates/              # Jinja2 HTML 템플릿
    ├── index.html
    ├── items.html
    └── 404.html
```

---

## 왜 이런 구조인가 — 계층형 아키텍처

이 프로젝트는 **요청이 들어왔을 때 흐름이 한 방향으로만 흐르도록** 계층을 나눴습니다.

```
HTTP 요청
   ↓
routes/        ← URL 파싱, 응답 형식 결정 (HTML/JSON)
   ↓
services/      ← 비즈니스 규칙, 여러 repository 조합
   ↓
repositories/  ← JSON 파일 I/O, 쿼리
   ↓
data/          ← 실제 데이터 파일
```

각 계층은 **바로 아래 계층만** 호출합니다. 즉 라우트는 서비스만 알고, 서비스는 리포지토리만 알며, 리포지토리는 파일을 다룹니다. 라우트가 직접 JSON 파일을 읽는 일은 없습니다.

### 계층별 책임

#### `routes/` — HTTP 계층 (Controller)

**역할**: HTTP 요청을 받아서 적절한 응답 형식(HTML, JSON)으로 변환.

**해야 할 일**
- URL 파라미터 파싱 (`/api/items/<int:item_id>`)
- request body 검증
- 적절한 status code 반환 (200, 404 등)
- `render_template` 또는 `jsonify` 호출

**하지 말아야 할 일**
- JSON 파일을 직접 읽거나 쓰는 것
- 비즈니스 규칙을 코드에 박아넣는 것 (예: "가격이 0보다 커야 한다")

[routes/main_routes.py](routes/main_routes.py:33-38)의 `api_item`은 좋은 예입니다 — 서비스 호출 후 결과가 없으면 `abort(404)`만 합니다. 어디에서 데이터가 오는지는 모릅니다.

#### `services/` — 비즈니스 로직 계층

**역할**: 도메인 규칙을 표현하는 곳. 여러 리포지토리를 조합하거나, 검증하거나, 계산하는 작업이 들어갑니다.

지금은 [services/item_service.py](services/item_service.py)가 단순히 리포지토리를 한 번 더 감싸기만 하지만, 다음과 같이 자라납니다:
- "재고가 0 이상인 아이템만 조회"
- "사용자의 권한에 따라 보여줄 필드 필터링"
- "여러 데이터 소스를 합쳐서 하나의 응답 만들기"

**왜 지금부터 분리했나?** 처음엔 라우트에서 리포지토리를 직접 불러도 동작합니다. 하지만 비즈니스 규칙이 한두 줄씩 늘어나면 라우트가 비대해지고, "이 규칙이 이 한 곳에만 있는가?" 를 추적하기 어려워집니다. 서비스를 미리 만들어 두면 새 규칙이 들어올 자리가 정해져 있습니다.

#### `repositories/` — 데이터 접근 계층

**역할**: 데이터가 어디에 어떻게 저장돼 있는지를 **숨깁니다**.

[repositories/repositoryManager.py](repositories/repositoryManager.py)의 `RepositoryManager`는 파일 이름(`items`)만 받으면 `data/items.json`을 찾아서 읽고/쓰고/검색합니다. 이름 → 경로 → 파일 I/O는 모두 이 클래스 안에 갇혀 있습니다.

**이 계층의 진짜 가치는 미래에 드러납니다.**

지금은 JSON 파일을 씁니다. 나중에 SQLite로 옮긴다면? `RepositoryManager`의 내부만 바꾸고 `services/`와 `routes/`는 손대지 않아도 됩니다. **변경의 파급 범위를 한 곳에 가두는 것** — 이게 계층 분리의 핵심 효익입니다.

#### `models/` — 데이터 형태 정의 (현재 비어있음)

**역할**: 도메인 객체의 형태(필드, 타입)를 정의. `dataclass`나 Pydantic `BaseModel`로 작성합니다.

지금은 dict로 다루지만, `Item` 같은 클래스가 생기면 IDE 자동완성, 타입 체크, 직렬화/역직렬화 통합이 가능해집니다.

#### `data/` — 실제 데이터

JSON 파일들이 사는 곳. 코드와 데이터를 분리하기 위한 폴더입니다. 운영에서는 DB로 대체될 위치입니다.

#### `scripts/` — 일회성 유틸리티

마이그레이션, 시드 데이터 생성, 백업 같은 **앱 실행과 무관한** 스크립트가 들어갑니다. 라우트나 서비스에 들어가면 안 되는 코드가 자연스럽게 모이는 곳입니다.

#### `static/`, `templates/` — Flask 컨벤션

Flask가 기본적으로 인식하는 폴더 이름입니다.
- `static/`: CSS, JS, 이미지 등 — `url_for('static', filename='css/style.css')`로 참조
- `templates/`: Jinja2 템플릿 — `render_template('index.html')`로 참조

---

## 데이터 흐름 예시: `GET /api/items/2`

이 요청 하나가 어떻게 흘러가는지 따라가보면 구조의 의도가 분명해집니다.

1. **요청 수신** — Flask가 URL을 파싱, `item_id=2`를 추출
2. **routes/main_routes.py** `api_item(2)` 호출
   ```python
   item = get_item(2)
   if item is None:
       abort(404)
   return jsonify(item)
   ```
3. **services/item_service.py** `get_item(2)` 호출
   ```python
   return repository_manager.find_by_id("items", 2)
   ```
4. **repositories/repositoryManager.py** `find_by_id("items", 2)` 호출
   - `data/items.json` 로드
   - `id == 2`인 항목 검색
   - dict 반환 (또는 None)
5. **응답** — Flask가 dict를 JSON으로 직렬화, `Content-Type: application/json`으로 응답

각 단계는 자기 위 계층만 의존합니다. 라우트는 "데이터가 JSON 파일에서 온다"는 사실을 모르고, 리포지토리는 "이 데이터가 HTTP 응답으로 나갈 것"이라는 사실을 모릅니다.

---

## 이 구조의 트레이드오프

**좋은 점**
- 변경 영향 범위가 좁음 (DB 교체 = 리포지토리만 수정)
- 테스트하기 쉬움 (서비스 테스트할 때 리포지토리를 가짜로 대체)
- 새 기능 추가 시 코드를 어디에 둬야 할지 명확

**비용**
- 작은 기능 하나 추가에도 여러 파일을 건드려야 함
- 처음엔 "왜 이렇게 복잡하게?"라는 인상을 줄 수 있음

**언제 가치가 드러나는가?** 기능이 5~10개를 넘어가고, 데이터 소스가 추가되고, 비즈니스 규칙이 쌓일 때입니다. 이 프로젝트는 그 시점이 오기 **전에** 미리 골격을 잡아둔 상태입니다.

---

## 확장 아이디어

- `models/Item` dataclass 추가 → 타입 안전성 확보
- `repositories/`에 SQLite 어댑터 추가 → 같은 인터페이스로 DB 사용
- `services/`에 검증/필터링 로직 추가 (예: 가격 범위 검색)
- `routes/`에 인증 미들웨어 적용
- `scripts/seed.py`로 초기 데이터 생성 자동화
