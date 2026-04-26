from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.database import Base

class RoleEnum(str, enum.Enum):
    leader = "leader"
    member = "member"
    guest = "guest"

class NotificationType(str, enum.Enum):
    TEAM_INVITE = "TEAM_INVITE"           # 팀 초대
    INVITE_ACCEPTED = "INVITE_ACCEPTED"   # 초대 수락
    INVITE_REJECTED = "INVITE_REJECTED"   # 초대 거절
    SCHEDULE_ASSIGN = "SCHEDULE_ASSIGN"    # 일정 배정
    MEMO_MENTION = "MEMO_MENTION"         # 메모 멘션
    COMMENT = "COMMENT"                   # 댓글 알림

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), nullable=False)
    password_hash = Column(String(255), nullable=False)
    job = Column(String(50), nullable=True)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=True)
    purpose = Column(Text, nullable=True)
    image_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    image_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # 관계 설정: 팀 삭제 시 연관된 데이터도 함께 삭제 (Cascade)
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="team", cascade="all, delete-orphan")
    memos = relationship("Memo", back_populates="team", cascade="all, delete-orphan")

class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)

    team = relationship("Team", back_populates="members")
    user = relationship("User", backref="team_memberships")

    @property
    def team_name(self):
        return self.team.name if self.team else "알 수 없음"

    @property
    def user_name(self):
        return self.user.username if self.user else "알 수 없음"

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    created_by = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    team = relationship("Team", back_populates="schedules")
    # 관계 설정: 일정 삭제 시 연관된 담당자 및 알림도 삭제
    assignees = relationship("ScheduleAssignee", back_populates="schedule", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="schedule", cascade="all, delete-orphan")

class ScheduleAssignee(Base):
    __tablename__ = "schedule_assignees"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    schedule = relationship("Schedule", back_populates="assignees")
    user = relationship("User")

    @property
    def user_name(self):
        return self.user.username if self.user else "알 수 없음"

class Memo(Base):
    __tablename__ = "memos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    author_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    team = relationship("Team", back_populates="memos")
    author = relationship("User")
    mentions = relationship("MemoMention", backref="memo", cascade="all, delete-orphan")
    comments = relationship("Comment", backref="memo", cascade="all, delete-orphan")

    @property
    def author_name(self):
        return self.author.username if self.author else "알 수 없음"

class MemoMention(Base):
    __tablename__ = "memo_mentions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    memo_id = Column(Integer, ForeignKey("memos.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User")

    @property
    def user_name(self):
        return self.user.username if self.user else "알 수 없음"

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    memo_id = Column(Integer, ForeignKey("memos.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    author = relationship("User")

    @property
    def author_name(self):
        return self.author.username if self.author else "알 수 없음"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False)
    remind_at = Column(DateTime, nullable=False)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    schedule = relationship("Schedule", back_populates="notifications")
    user = relationship("User")

class AppNotification(Base):
    __tablename__ = "app_notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    receiver_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sender_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    related_id = Column(Integer, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    receiver = relationship("User", foreign_keys=[receiver_id], backref="notifications")
    sender = relationship("User", foreign_keys=[sender_id])
