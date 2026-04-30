# NextWave Backend 🌊

NextWave는 팀 기반의 일정 협업 및 지식 공유를 지원하는 플랫폼의 핵심 비즈니스 로직을 담당하는 백엔드 API 시스템입니다. **FastAPI**의 비동기 처리 성능과 **AI(LLM)** 연동을 통한 스마트 협업 기능을 제공합니다.

## 🛠 주요 기술 스택 (Core Tech Stack)

- **Language**: Python 3.11+
- **Framework**: FastAPI 
- **Database**: MySQL 8.0 
- **ORM**: SQLAlchemy 
- **AI Integration**: OpenAI SDK 
- **Infrastructure**: Docker & Docker Compose 

## ✨ 핵심 기능 (Key Features)

### 1. 기본 웹 서비스 (Core Web Service)
- **팀 및 멤버십 관리**: 팀 생성, 초대, 권한 설정 및 멤버 관리 기능을 제공합니다.
- **협업 일정 및 메모**: 팀 단위의 일정 공유와 실시간 메모 작성, 댓글 및 알림 시스템을 구축하였습니다.
- **보안 및 인증**: JWT(JSON Web Token)를 사용한 보안 인증과 유저 프로필 기반의 권한 제어를 수행합니다.

### 2. AI 컨텍스트 엔진 (AI Contextual Engine)
- **지능형 온보딩**: 가입 시 사용자의 직업과 사용 목적을 분석하여, LLM이 맞춤형 예시 데이터와 핵심 기능을 추천합니다.
- **맥락 기반 자동 생성**: 사용자의 최근 일정 10개와 메모 10개를 분석하여, 다음에 이어질 확률이 높은 업무나 회의 내용을 AI가 예측하여 생성합니다.
- **팀 프로필 최적화**: 팀 멤버 구성 정보를 AI에 전달하여, 실질적인 협업 맥락에 맞는 담당자 지정 및 멘션 추천이 가능합니다.

## 📂 프로젝트 구조 (Project Structure)

```text
NextWave_Backend/
├── docker/
│   ├── compose/           # 도커 컴포즈 실행 환경 (API, DB, Proxy)
│   └── env/               # 환경별 보안 설정 (.env.api, .env.db 등)
├── services/
│   ├── api/               # FastAPI 메인 애플리케이션
│   │   ├── app/
│   │   │   ├── api/       # API 라우터 (auth, schedules, memos, ai 등)
│   │   │   ├── core/      # 전역 설정 및 보안 구성
│   │   │   ├── db/        # 데이터베이스 세션 및 커넥션 관리
│   │   │   ├── schemas/   # Pydantic 데이터 검증 모델
│   │   │   └── services/  # LLM 연동 및 비즈니스 서비스 로직
│   │   └── main.py        # 실행 엔트리포인트
│   └── proxy/             # Nginx 리버스 프록시 설정
└── README.md
```

## 🚀 시작하기 (Getting Started)

### 1. 환경 변수 설정
`docker/env/` 및 `docker/compose/` 폴더 내의 `.example` 파일들을 복사하여 실제 환경 변수 파일(`.env`)을 생성하십시오.
- **필수 항목**: `DATABASE_URL`, `SECRET_KEY`, `OPENAI_API_KEY`

### 2. 컨테이너 빌드 및 실행
```bash
cd docker/compose
docker compose up -d --build
```

### 3. API 문서 확인
서버 구동 후 다음 주소에서 인터랙티브 API 문서를 확인할 수 있습니다.
- **Swagger UI**: `http://localhost:8000/docs`
- **AI 생성 엔드포인트**: `POST /api/v1/ai/generate/contextual`

## 🔒 운영 및 보안 (Production & Security)
- **비밀키 관리**: 운영 환경 배포 시 반드시 고유한 `SECRET_KEY`를 생성하여 적용하십시오.
- **DB 보안**: 호스트 볼륨 마운트를 통한 데이터 지속성을 확보하며, 운영 시 전용 DB 사용자 권한을 분리하여 관리합니다.
