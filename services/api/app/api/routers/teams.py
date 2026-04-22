from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.db.models import Team, TeamMember, User, RoleEnum
from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse, TeamMemberCreate, TeamMemberResponse

router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("/", response_model=TeamResponse)
def create_team(
    *,
    db: Session = Depends(deps.get_db),
    team_in: TeamCreate,
    current_user: User = Depends(deps.get_current_user),
):
    """새로운 팀을 만들고, 방장을 리더로 추가"""
    team = Team(name=team_in.name)
    db.add(team)
    db.commit()
    db.refresh(team)
    
    # 만든 사람은 leader
    tm = TeamMember(
        team_id=team.id,
        user_id=current_user.id,
        role=RoleEnum.leader
    )
    db.add(tm)
    db.commit()
    
    return team

@router.get("/", response_model=List[TeamResponse])
def read_my_teams(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """내가 소속된 팀 목록 조회"""
    teams = db.query(Team).join(TeamMember).filter(TeamMember.user_id == current_user.id).all()
    return teams

@router.get("/{team_id}", response_model=TeamResponse)
def read_team(
    team_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """특정 팀 조회 (팀 멤버만 가능)"""
    deps.check_team_membership(db, team_id, current_user.id)
    team = db.query(Team).filter(Team.id == team_id).first()
    return team

@router.put("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: int,
    team_in: TeamUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """팀 정보 수정 (leader만 가능)"""
    deps.check_team_membership(db, team_id, current_user.id, required_roles=[RoleEnum.leader])
    
    team = db.query(Team).filter(Team.id == team_id).first()
    team.name = team_in.name
    db.commit()
    db.refresh(team)
    return team

@router.delete("/{team_id}", status_code=204)
def delete_team(
    team_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """팀 완전 삭제 (leader만 가능)"""
    deps.check_team_membership(db, team_id, current_user.id, required_roles=[RoleEnum.leader])
    
    team = db.query(Team).filter(Team.id == team_id).first()
    db.delete(team)
    db.commit()

# --- Team Members API ---

@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
def read_team_members(
    team_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """팀의 멤버 목록 조회"""
    deps.check_team_membership(db, team_id, current_user.id)
    members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    return members

@router.post("/{team_id}/members", response_model=TeamMemberResponse)
def add_team_member(
    team_id: int,
    member_in: TeamMemberCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """이메일을 받아 해당 유저를 팀원으로 초대 (leader만 가능)"""
    deps.check_team_membership(db, team_id, current_user.id, required_roles=[RoleEnum.leader])
    
    user_to_invite = db.query(User).filter(User.email == member_in.email).first()
    if not user_to_invite:
        raise HTTPException(status_code=404, detail="해당 이메일을 사용하는 사용자가 없습니다.")
        
    existing = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == user_to_invite.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 이 팀에 소속된 사용자입니다.")
        
    new_member = TeamMember(
        team_id=team_id,
        user_id=user_to_invite.id,
        role=member_in.role
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@router.delete("/{team_id}/members/{user_id}", status_code=204)
def remove_team_member(
    team_id: int,
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """팀에서 팀원 내보내기 (leader만 가능)"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="리더 스스로를 내보낼 수는 없습니다. 위임 혹은 팀 삭제를 이용하세요.")
        
    deps.check_team_membership(db, team_id, current_user.id, required_roles=[RoleEnum.leader])
    
    member_to_remove = db.query(TeamMember).filter(TeamMember.team_id == team_id, TeamMember.user_id == user_id).first()
    if not member_to_remove:
        raise HTTPException(status_code=404, detail="해당 멤버가 팀에 존재하지 않습니다.")
        
    db.delete(member_to_remove)
    db.commit()
