from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.db.models import Team, TeamMember, User, RoleEnum
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse, TeamMemberCreate, TeamMemberResponse

router = APIRouter(prefix="/teams", tags=["🧑‍🤝‍🧑 팀 (Teams)"])

_401 = {401: {"description": "인증 토큰 없음 또는 만료"}}
_403 = {403: {"description": "해당 팀의 소속 멤버가 아니거나 권한(leader) 부족"}}
_404 = {404: {"description": "팀 또는 유저를 찾을 수 없음"}}

@router.post("/", response_model=TeamResponse, summary="팀 생성", responses={**_401})
def create_team(*, db: Session = Depends(deps.get_db), team_in: TeamCreate, current_user: User = Depends(deps.get_current_user)):
    """새 팀을 만들고, 생성자는 자동으로 **leader** 권한의 멤버로 등록됩니다."""
    team = Team(name=team_in.name, description=team_in.description, image_path=team_in.image_path)
    db.add(team)
    db.commit()
    db.refresh(team)
    db.add(TeamMember(team_id=team.id, user_id=current_user.id, role=RoleEnum.leader))
    db.commit()
    return team

@router.get("/", response_model=List[TeamResponse], summary="내 팀 목록 조회", responses={**_401})
def read_my_teams(db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    """현재 로그인한 사용자가 소속된 모든 팀 목록을 반환합니다."""
    return db.query(Team).join(TeamMember).filter(TeamMember.user_id == current_user.id).all()

@router.get("/{team_id}", response_model=TeamResponse, summary="특정 팀 상세 조회", responses={**_401, **_403})
def read_team(team_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    """특정 팀의 상세 정보를 조회합니다. **해당 팀의 멤버만 접근 가능**합니다."""
    deps.check_team_membership(db, team_id, current_user.id)
    return db.query(Team).filter(Team.id == team_id).first()

@router.put("/{team_id}", response_model=TeamResponse, summary="팀 정보 수정", responses={**_401, **_403})
def update_team(team_id: int, team_in: TeamUpdate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    """팀 이름, 설명, 이미지를 수정합니다. **leader 권한**만 가능합니다."""
    deps.check_team_membership(db, team_id, current_user.id, required_roles=[RoleEnum.leader])
    team = db.query(Team).filter(Team.id == team_id).first()
    if team_in.name is not None:
        team.name = team_in.name
    if team_in.description is not None:
        team.description = team_in.description
    if team_in.image_path is not None:
        team.image_path = team_in.image_path
    db.commit()
    db.refresh(team)
    return team

@router.delete("/{team_id}", status_code=204, summary="팀 삭제", responses={**_401, **_403})
def delete_team(team_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    """팀을 완전히 삭제합니다. **leader 권한**만 가능하며, 연관된 모든 일정·메모도 함께 삭제됩니다(CASCADE)."""
    deps.check_team_membership(db, team_id, current_user.id, required_roles=[RoleEnum.leader])
    team = db.query(Team).filter(Team.id == team_id).first()
    db.delete(team)
    db.commit()

# --- Team Members API ---

@router.get("/{team_id}/members", response_model=List[TeamMemberResponse], summary="팀 멤버 목록 조회", responses={**_401, **_403})
def read_team_members(team_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    """해당 팀의 전체 멤버 목록 및 역할(role)을 반환합니다."""
    deps.check_team_membership(db, team_id, current_user.id)
    return db.query(TeamMember).filter(TeamMember.team_id == team_id).all()

@router.post("/{team_id}/members", response_model=TeamMemberResponse, summary="팀 멤버 초대 (이메일)", responses={**_401, **_403, **_404})
def add_team_member(team_id: int, member_in: TeamMemberCreate, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    """이메일로 가입된 유저를 팀원으로 초대합니다. **leader 권한**만 가능합니다."""
    deps.check_team_membership(db, team_id, current_user.id, required_roles=[RoleEnum.leader])
    user_to_invite = db.query(User).filter(User.email == member_in.email).first()
    if not user_to_invite:
        raise HTTPException(status_code=404, detail="해당 이메일을 사용하는 사용자가 없습니다.")
    if db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == user_to_invite.id).first():
        raise HTTPException(status_code=400, detail="이미 이 팀에 소속된 사용자입니다.")
    new_member = TeamMember(team_id=team_id, user_id=user_to_invite.id, role=member_in.role)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@router.delete("/{team_id}/members/{user_id}", status_code=204, summary="팀 멤버 내보내기", responses={**_401, **_403, **_404})
def remove_team_member(team_id: int, user_id: int, db: Session = Depends(deps.get_db), current_user: User = Depends(deps.get_current_user)):
    """팀에서 멤버를 강제 퇴출합니다. **leader 권한**만 가능하며, 자기 자신을 내보낼 수는 없습니다."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="리더 스스로를 내보낼 수는 없습니다. 위임 혹은 팀 삭제를 이용하세요.")
    deps.check_team_membership(db, team_id, current_user.id, required_roles=[RoleEnum.leader])
    member_to_remove = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id).first()
    if not member_to_remove:
        raise HTTPException(status_code=404, detail="해당 멤버가 팀에 존재하지 않습니다.")
    db.delete(member_to_remove)
    db.commit()
