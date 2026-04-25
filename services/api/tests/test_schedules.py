"""
일정 도메인 통합 테스트
"""
import pytest


BASE_SCHEDULE = {
    "title": "스프린트 회의",
    "start_time": "2026-05-01T10:00:00",
    "end_time": "2026-05-01T11:00:00",
    "status": "PENDING",
}


class TestScheduleCrud:
    def test_create_schedule(self, client, token_a, team_with_leader):
        """정상 일정 생성"""
        payload = {**BASE_SCHEDULE, "team_id": team_with_leader.id}
        res = client.post("/api/v1/schedules/", json=payload,
                          headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 200
        assert res.json()["title"] == "스프린트 회의"

    def test_create_schedule_invalid_time(self, client, token_a, team_with_leader):
        """종료 시간이 시작 시간보다 앞설 경우 422 반환"""
        payload = {
            **BASE_SCHEDULE,
            "team_id": team_with_leader.id,
            "start_time": "2026-05-01T11:00:00",
            "end_time": "2026-05-01T10:00:00",  # 역전된 시간
        }
        res = client.post("/api/v1/schedules/", json=payload,
                          headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 422

    def test_get_team_schedules(self, client, token_a, team_with_leader):
        """팀 일정 목록 조회"""
        payload = {**BASE_SCHEDULE, "team_id": team_with_leader.id}
        client.post("/api/v1/schedules/", json=payload,
                    headers={"Authorization": f"Bearer {token_a}"})
        res = client.get(f"/api/v1/teams/{team_with_leader.id}/schedules",
                         headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 200
        assert len(res.json()) == 1

    def test_patch_schedule_status(self, client, token_a, team_with_leader):
        """일정 상태 변경 (PATCH /status)"""
        payload = {**BASE_SCHEDULE, "team_id": team_with_leader.id}
        schedule_id = client.post("/api/v1/schedules/", json=payload,
                                  headers={"Authorization": f"Bearer {token_a}"}).json()["id"]

        res = client.patch(f"/api/v1/schedules/{schedule_id}/status",
                           json={"status": "IN_PROGRESS"},
                           headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 200
        assert res.json()["status"] == "IN_PROGRESS"


class TestScheduleAssignees:
    def test_add_assignees(self, client, token_a, team_with_leader, user_b, db):
        """담당자 다중 배정"""
        from app.db.models import TeamMember, RoleEnum
        db.add(TeamMember(team_id=team_with_leader.id, user_id=user_b.id, role=RoleEnum.member))
        db.commit()

        payload = {**BASE_SCHEDULE, "team_id": team_with_leader.id}
        schedule_id = client.post("/api/v1/schedules/", json=payload,
                                  headers={"Authorization": f"Bearer {token_a}"}).json()["id"]

        res = client.post(f"/api/v1/schedules/{schedule_id}/assignees",
                          json={"user_ids": [user_b.id]},
                          headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 201
