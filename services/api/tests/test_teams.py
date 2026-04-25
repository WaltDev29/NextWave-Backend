"""
팀 도메인 통합 테스트
"""
import pytest
from tests.conftest import create_test_user


class TestTeamCrud:
    def test_create_team(self, client, token_a):
        """팀 생성 및 생성자가 leader로 등록되는지 확인"""
        res = client.post("/api/v1/teams/", json={"name": "드림팀"},
                          headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 200
        assert res.json()["name"] == "드림팀"

    def test_list_my_teams(self, client, token_a, team_with_leader):
        """내 팀 목록 조회"""
        res = client.get("/api/v1/teams/", headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 200
        assert len(res.json()) == 1

    def test_get_team_by_non_member(self, client, token_b, team_with_leader):
        """소속이 아닌 유저가 팀 조회 시 403 반환"""
        res = client.get(f"/api/v1/teams/{team_with_leader.id}",
                         headers={"Authorization": f"Bearer {token_b}"})
        assert res.status_code == 403

    def test_update_team_as_leader(self, client, token_a, team_with_leader):
        """리더가 팀 이름 변경"""
        res = client.put(f"/api/v1/teams/{team_with_leader.id}",
                         json={"name": "새팀이름"},
                         headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 200
        assert res.json()["name"] == "새팀이름"

    def test_delete_team_as_non_leader(self, client, token_b, team_with_leader, user_b, db):
        """리더가 아닌 멤버가 팀 삭제 시 403 반환"""
        from app.db.models import TeamMember, RoleEnum
        db.add(TeamMember(team_id=team_with_leader.id, user_id=user_b.id, role=RoleEnum.member))
        db.commit()
        res = client.delete(f"/api/v1/teams/{team_with_leader.id}",
                            headers={"Authorization": f"Bearer {token_b}"})
        assert res.status_code == 403


class TestTeamMembers:
    def test_invite_member_by_email(self, client, token_a, team_with_leader, user_b):
        """리더가 이메일로 멤버 초대"""
        res = client.post(f"/api/v1/teams/{team_with_leader.id}/members",
                          json={"email": "user_b@test.com", "role": "member"},
                          headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 200
        assert res.json()["user_name"] == "유저B"

    def test_invite_nonexistent_user(self, client, token_a, team_with_leader):
        """존재하지 않는 이메일 초대 시 404 반환"""
        res = client.post(f"/api/v1/teams/{team_with_leader.id}/members",
                          json={"email": "ghost@test.com", "role": "member"},
                          headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 404
