"""
메모 & 댓글 도메인 통합 테스트
"""
import pytest


class TestMemoCrud:
    def _make_schedule(self, client, token, team_id):
        return client.post("/api/v1/schedules/", json={
            "title": "테스트 일정", "start_time": "2026-05-01T10:00:00",
            "status": "PENDING", "team_id": team_id
        }, headers={"Authorization": f"Bearer {token}"}).json()["id"]

    def test_create_memo(self, client, token_a, team_with_leader):
        """메모 생성"""
        res = client.post("/api/v1/memos/", json={
            "title": "오늘 할 일",
            "content": "API 테스트 작성",
            "team_id": team_with_leader.id
        }, headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 200
        assert res.json()["title"] == "오늘 할 일"
        assert res.json()["author_name"] == "유저A"

    def test_create_memo_with_schedule(self, client, token_a, team_with_leader):
        """일정에 종속된 메모 생성"""
        schedule_id = self._make_schedule(client, token_a, team_with_leader.id)
        res = client.post("/api/v1/memos/", json={
            "title": "일정 노트",
            "team_id": team_with_leader.id,
            "schedule_id": schedule_id
        }, headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 200
        assert res.json()["schedule_id"] == schedule_id

    def test_get_memo_detail_includes_comments(self, client, token_a, team_with_leader):
        """메모 상세 조회 시 댓글 포함 확인"""
        memo_id = client.post("/api/v1/memos/", json={
            "title": "댓글 테스트", "team_id": team_with_leader.id
        }, headers={"Authorization": f"Bearer {token_a}"}).json()["id"]

        client.post(f"/api/v1/memos/{memo_id}/comments",
                    json={"content": "첫 번째 댓글"},
                    headers={"Authorization": f"Bearer {token_a}"})

        res = client.get(f"/api/v1/memos/{memo_id}",
                         headers={"Authorization": f"Bearer {token_a}"})
        assert res.status_code == 200
        assert len(res.json()["comments"]) == 1
        assert res.json()["comments"][0]["content"] == "첫 번째 댓글"

    def test_non_member_cannot_read_memo(self, client, token_b, team_with_leader):
        """소속이 아닌 유저가 메모 읽기 시 403"""
        memo_id = 99999  # 존재하지 않는 ID
        res = client.get(f"/api/v1/memos/{memo_id}",
                         headers={"Authorization": f"Bearer {token_b}"})
        assert res.status_code == 404  # 없는 메모

    def test_delete_memo_by_non_author(self, client, token_a, token_b, team_with_leader, user_b, db):
        """작성자가 아닌 일반 멤버가 삭제 시도 시 403"""
        from app.db.models import TeamMember, RoleEnum
        db.add(TeamMember(team_id=team_with_leader.id, user_id=user_b.id, role=RoleEnum.member))
        db.commit()

        memo_id = client.post("/api/v1/memos/", json={
            "title": "A의 메모", "team_id": team_with_leader.id
        }, headers={"Authorization": f"Bearer {token_a}"}).json()["id"]

        res = client.delete(f"/api/v1/memos/{memo_id}",
                            headers={"Authorization": f"Bearer {token_b}"})
        assert res.status_code == 403
