"""
인증/회원 도메인 통합 테스트
"""
import pytest
from tests.conftest import create_test_user, get_token


class TestSignup:
    def test_signup_success(self, client):
        """정상 회원가입"""
        res = client.post("/api/v1/users/signup", json={
            "email": "new@test.com",
            "username": "신규유저",
            "password": "Abcd1234!"
        })
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == "new@test.com"
        assert "password_hash" not in data  # 비밀번호 노출 방지 확인

    def test_signup_duplicate_email(self, client, db):
        """중복 이메일 가입 시 400 반환"""
        create_test_user(db, "dup@test.com", "기존유저")
        res = client.post("/api/v1/users/signup", json={
            "email": "dup@test.com",
            "username": "신규유저",
            "password": "Abcd1234!"
        })
        assert res.status_code == 400

    def test_signup_invalid_email(self, client):
        """잘못된 이메일 형식 시 422 반환"""
        res = client.post("/api/v1/users/signup", json={
            "email": "not-an-email",
            "username": "유저",
            "password": "Abcd1234!"
        })
        assert res.status_code == 422


class TestLogin:
    def test_login_success(self, client, user_a):
        """정상 로그인 후 JWT 발급 확인"""
        res = client.post("/api/v1/login/access-token", data={
            "username": "user_a@test.com",
            "password": "password123!"
        })
        assert res.status_code == 200
        assert "access_token" in res.json()
        assert res.json()["token_type"] == "bearer"

    def test_login_wrong_password(self, client, user_a):
        """비밀번호 불일치 시 401 반환"""
        res = client.post("/api/v1/login/access-token", data={
            "username": "user_a@test.com",
            "password": "wrongpassword"
        })
        assert res.status_code == 401

    def test_get_me_without_token(self, client):
        """토큰 없이 /users/me 접근 시 401 반환"""
        res = client.get("/api/v1/users/me")
        assert res.status_code == 401

    def test_get_me_with_token(self, client, token_a):
        """유효한 토큰으로 /users/me 접근 성공"""
        res = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 200
        assert res.json()["email"] == "user_a@test.com"
