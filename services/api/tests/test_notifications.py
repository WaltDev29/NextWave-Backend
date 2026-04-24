import pytest
from app.db.models import RoleEnum, TeamMember

def test_team_invite_flow(client, db, token_a, user_b, team_with_leader):
    # 1. 유저A(리더)가 유저B를 초대
    res = client.post(
        f"/api/v1/teams/{team_with_leader.id}/members",
        json={"email": "user_b@test.com", "role": "member"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert res.status_code == 200
    assert "초대 알림을 보냈습니다" in res.json()["message"]

    # 2. 유저B의 인박스(알림함) 확인
    token_b = client.post("/api/v1/login/access-token", data={"username": "user_b@test.com", "password": "password123!"}).json()["access_token"]
    res = client.get("/api/v1/inbox/", headers={"Authorization": f"Bearer {token_b}"})
    assert res.status_code == 200
    notifications = res.json()
    assert len(notifications) == 1
    noti = notifications[0]
    assert noti["type"] == "TEAM_INVITE"
    assert "테스트팀" in noti["content"]
    assert noti["related_id"] == team_with_leader.id

    # 3. 유저B가 초대 수락
    res = client.post(f"/api/v1/inbox/{noti['id']}/accept", headers={"Authorization": f"Bearer {token_b}"})
    assert res.status_code == 200
    assert "수락했습니다" in res.json()["message"]

    # 4. 실제 팀 멤버 인가 확인 (트랜잭션 갱신 후 조회)
    db.commit()
    member = db.query(TeamMember).filter(TeamMember.team_id == team_with_leader.id, TeamMember.user_id == user_b.id).first()
    assert member is not None, f"팀 멤버가 생성되지 않았습니다. (TeamID: {team_with_leader.id}, UserB: {user_b.id})"
    assert member.role == RoleEnum.member

    # 5. 유저A에게 '수락됨' 알림이 갔는지 확인
    db.commit()
    res = client.get("/api/v1/inbox/", headers={"Authorization": f"Bearer {token_a}"})
    notifications_a = res.json()
    assert any(n["type"] == "INVITE_ACCEPTED" for n in notifications_a)

def test_schedule_assignment_notification(client, db, token_a, user_a, user_b, team_with_leader):
    # 1. 일정 생성
    res = client.post(
        "/api/v1/schedules/",
        json={
            "title": "테스트 일정",
            "start_time": "2026-12-31T23:59:59",
            "team_id": team_with_leader.id
        },
        headers={"Authorization": f"Bearer {token_a}"}
    )
    schedule_id = res.json()["id"]

    # 2. 유저B를 팀원으로 강제 추가 (초대 수락 과정 생략하고 바로 테스트)
    db.add(TeamMember(team_id=team_with_leader.id, user_id=user_b.id, role=RoleEnum.member))
    db.commit()

    # 3. 유저B를 일정 담당자로 등록
    client.post(
        f"/api/v1/schedules/{schedule_id}/assignees",
        json={"user_ids": [user_b.id]},
        headers={"Authorization": f"Bearer {token_a}"}
    )

    # 4. 유저B 알림 확인
    db.commit()
    token_b = client.post("/api/v1/login/access-token", data={"username": "user_b@test.com", "password": "password123!"}).json()["access_token"]
    res = client.get("/api/v1/inbox/", headers={"Authorization": f"Bearer {token_b}"})
    assert any(n["type"] == "SCHEDULE_ASSIGN" for n in res.json())

def test_memo_mention_notification(client, db, token_a, user_b, team_with_leader):
    # 1. 유저B를 멘션하여 메모 작성
    res = client.post(
        "/api/v1/memos/",
        json={
            "team_id": team_with_leader.id,
            "title": "멘션 메모",
            "content": "이것은 테스트",
            "mentions": [user_b.id]
        },
        headers={"Authorization": f"Bearer {token_a}"}
    )
    assert res.status_code == 200

    # 2. 유저B 알림 확인
    db.commit()
    token_b = client.post("/api/v1/login/access-token", data={"username": "user_b@test.com", "password": "password123!"}).json()["access_token"]
    res = client.get("/api/v1/inbox/", headers={"Authorization": f"Bearer {token_b}"})
    assert any(n["type"] == "MEMO_MENTION" for n in res.json())

def test_comment_notification(client, db, token_a, user_a, user_b, team_with_leader):
    # 1. 유저A가 메모 작성
    res = client.post(
        "/api/v1/memos/",
        json={"team_id": team_with_leader.id, "title": "유저A의 메모"},
        headers={"Authorization": f"Bearer {token_a}"}
    )
    memo_id = res.json()["id"]

    # 2. 유저B가 댓글 작성
    db.add(TeamMember(team_id=team_with_leader.id, user_id=user_b.id, role=RoleEnum.member))
    db.commit()
    token_b = client.post("/api/v1/login/access-token", data={"username": "user_b@test.com", "password": "password123!"}).json()["access_token"]
    
    client.post(
        f"/api/v1/memos/{memo_id}/comments",
        json={"content": "유저B의 댓글입니다."},
        headers={"Authorization": f"Bearer {token_b}"}
    )

    # 3. 유저A 알림 확인 (본인 메모에 댓글 달림)
    db.commit()
    res = client.get("/api/v1/inbox/", headers={"Authorization": f"Bearer {token_a}"})
    assert any(n["type"] == "COMMENT" for n in res.json())
