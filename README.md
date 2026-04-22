# NextWave Backend 🌊

NextWave는 일정 관리 및 게시글을 개인 및 팀 단위로 사용할 수 있도록 지원하는 웹 서비스의 백엔드 API 시스템입니다. 
빠르고 확장이 용이한 **FastAPI**와 안정적인 관계형 데이터베이스인 **MySQL**을 기반으로 구축되었습니다.

## 🛠 기술 스택 (Tech Stack)

- **언어**: Python 3.11+
- **프레임워크**: FastAPI
- **데이터베이스**: MySQL 8.0
- **ORM & 마이그레이션**: SQLAlchemy, Alembic
- **인프라**: Docker, Docker Compose

## 📂 프로젝트 구조 (Project Structure)

```text
NextWave_Backend/
├── docker/
│   ├── compose/
│   │   ├── docker-compose.yml     # API & DB Docker 컨테이너 실행 환경
│   │   ├── .env                   # Compose 글로벌 환경 변수 (Git에는 제외되어야 함)
│   │   └── .env.example           # Compose 환경 변수 템플릿
│   └── env/
│       ├── .env.api               # API 서버용 환경 변수 (.gitignore)
│       ├── .env.api.example       # API 환경 변수 템플릿
│       ├── .env.db                # DB 서버용 환경 변수 (.gitignore)
│       └── .env.db.example        # DB 환경 변수 템플릿
├── services/
│   ├── api/                       # FastAPI 메인 애플리케이션 디렉터리
│   │   ├── alembic/               # 데이터베이스 마이그레이션 설정
│   │   ├── app/                   # 비즈니스 로직 및 API 엔드포인트
│   │   │   ├── core/              # 전역 설정 (Config 등)
│   │   │   ├── db/                # 데이터베이스 세션 및 커넥션 관리
│   │   │   └── __init__.py        # FastAPI 앱 Factory 함수
│   │   ├── main.py                # 실행 진입점
│   │   ├── requirements.txt       # Python 패키지 의존성
│   │   └── Dockerfile             # API 서버 이미지 빌드 파일
│   └── db/                        # MySQL 로컬 데이터가 저장되는 볼륨 마운트 폴더 (Git 제외)
└── README.md
```

## 🚀 시작하기 (Getting Started)

이 프로젝트는 Docker 기반으로 로컬 구동 환경을 제공합니다.

### 1. 환경 변수 설정
프로젝트 실행 전, `docker/` 폴더 내에 마련된 템플릿(`.example`) 파일들을 복사하여 실제 환경 변수 파일을 생성해야 합니다.
- `docker/compose/.env.example` -> `docker/compose/.env`
- `docker/env/.env.api.example` -> `docker/env/.env.api`
- `docker/env/.env.db.example` -> `docker/env/.env.db`

### 2. 컨테이너 빌드 및 실행
```bash
cd docker/compose
docker compose up -d --build
```
초기 구동 시 MySQL 초기화 및 API 컨테이너 빌드가 진행됩니다.

### 3. 접속 확인
서버가 정상적으로 기동되었는지 확인합니다.
- API 헬스 체크: [http://localhost:8000/health](http://localhost:8000/health)
- API 문서 (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)

## 📦 데이터베이스 마이그레이션 (Alembic)

`app/models`에 정의된 SQLAlchemy 스키마를 데이터베이스에 반영하려면 `nextwave-api` 컨테이너 내부에서 다음 명령어를 실행합니다.

```bash
# 컨테이너에 접속 후 마이그레이션 스크립트 모드 진입
docker exec -it nextwave-api bash

# 스키마 변경점 감지 및 마이그레이션 파일 자동 생성
alembic revision --autogenerate -m "마이그레이션 내용 설명"

# 생성된 마이그레이션을 데이터베이스에 적용
alembic upgrade head
```
