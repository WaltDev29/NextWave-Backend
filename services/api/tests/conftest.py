import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app import create_app
from app.db.database import Base, get_db
from app.db.models import User, Team, TeamMember, RoleEnum
from app.core.security import get_password_hash

# ============================================================
# 테스트 DB 설정
# CI 환경: TEST_DATABASE_URL 환경변수로 주입 (localhost:3306)
# 로컬 환경: Docker 네트워크 호스트명(nextwave-db) 기본값 사용
# ============================================================
_default_url = "mysql+pymysql://nextwave_user:user_password!@nextwave-db:3306/nextwave_test"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", _default_url)

test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """테스트 세션 시작 시 테이블 생성, 종료 시 전체 DROP"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_tables():
    """각 테스트 실행 후 전체 데이터 초기화 (테이블 구조는 유지)"""
    yield
    db = TestingSessionLocal()
    try:
        db.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        db.commit()
    finally:
        db.close()


@pytest.fixture
def client():
    """테스트용 FastAPI TestClient"""
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


# ============================================================
# 유저 및 팀 픽스처
# ============================================================
@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_test_user(db, email: str, username: str, password: str = "password123!") -> User:
    user = User(email=email, username=username, password_hash=get_password_hash(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_token(client, email: str, password: str = "password123!") -> str:
    res = client.post("/api/v1/login/access-token", data={"username": email, "password": password})
    return res.json()["access_token"]


@pytest.fixture
def user_a(db):
    return create_test_user(db, "user_a@test.com", "유저A")


@pytest.fixture
def user_b(db):
    return create_test_user(db, "user_b@test.com", "유저B")


@pytest.fixture
def token_a(client, user_a):
    return get_token(client, "user_a@test.com")


@pytest.fixture
def token_b(client, user_b):
    return get_token(client, "user_b@test.com")


@pytest.fixture
def team_with_leader(db, user_a):
    """user_a가 리더인 팀 생성"""
    team = Team(name="테스트팀")
    db.add(team)
    db.flush()
    db.add(TeamMember(team_id=team.id, user_id=user_a.id, role=RoleEnum.leader))
    db.commit()
    db.refresh(team)
    return team
