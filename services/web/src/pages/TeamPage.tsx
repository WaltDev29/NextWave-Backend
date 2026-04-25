import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { teamsApi } from '../api/teams';
import { schedulesApi } from '../api/schedules';
import { memosApi } from '../api/memos';
import type { Team, TeamMember, Schedule, Memo, ScheduleStatus } from '../types';
import { useAuthStore } from '../stores/authStore';

// ===== 공통 서브 컴포넌트 =====

function Avatar({ name, src, size = 44 }: { name: string; src?: string | null; size?: number }) {
  return (
    <div style={{
      width: size, height: size, borderRadius: '50%',
      background: src ? 'none' : 'var(--accent-dim)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: size * 0.38, fontWeight: 700, color: 'var(--accent-light)',
      overflow: 'hidden', flexShrink: 0, border: '2px solid var(--border)',
    }}>
      {src ? <img src={src} alt={name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : name.slice(0, 2).toUpperCase()}
    </div>
  );
}

const STATUS_LABELS: Record<ScheduleStatus, string> = {
  PENDING: '대기', IN_PROGRESS: '진행 중', COMPLETED: '완료', CANCELLED: '취소',
};

// ===== 멤버 탭 =====
function MembersTab({ teamId, isLeader }: { teamId: number; isLeader: boolean }) {
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('member');
  const [msg, setMsg] = useState('');
  const qc = useQueryClient();

  const { data: members = [] } = useQuery({
    queryKey: ['members', teamId],
    queryFn: () => teamsApi.getMembers(teamId).then((r) => r.data),
  });
  const inviteMutation = useMutation({
    mutationFn: () => teamsApi.addMember(teamId, inviteEmail, inviteRole),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['members', teamId] }); setInviteEmail(''); setMsg('초대 완료!'); setTimeout(() => setMsg(''), 2000); },
    onError: (e: any) => setMsg(e.response?.data?.detail || '오류'),
  });

  return (
    <div>
      {/* 초대 폼 (리더만 노출) */}
      {isLeader && (
        <div className="card" style={{ display: 'flex', gap: '10px', alignItems: 'flex-end', marginBottom: '20px' }}>
          <div className="form-group" style={{ flex: 1 }}>
            <label>이메일로 멤버 초대</label>
            <input value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)} placeholder="초대할 이메일 주소" />
          </div>
          <div className="form-group" style={{ width: '120px' }}>
            <label>권한</label>
            <select value={inviteRole} onChange={(e) => setInviteRole(e.target.value)}>
              <option value="member">멤버</option>
              <option value="guest">게스트</option>
            </select>
          </div>
          <button className="btn btn-primary" disabled={!inviteEmail} onClick={() => inviteMutation.mutate()}>초대</button>
        </div>
      )}
      {msg && <p style={{ marginBottom: '12px', color: msg.includes('완료') ? 'var(--success)' : 'var(--danger)', fontSize: '13px' }}>{msg}</p>}

      {/* 멤버 목록 */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {members.map((m: TeamMember) => (
          <div key={m.id} className="card" style={{ padding: '16px', display: 'flex', alignItems: 'center', gap: '14px' }}>
            <Avatar name={m.user_name} size={40} />
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600 }}>{m.user_name}</div>
            </div>
            <span className={`badge badge-${m.role}`}>{m.role}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ===== 일정 탭 =====
function SchedulesTab({ teamId, isLeader }: { teamId: number; isLeader: boolean }) {
  const [showCreate, setShowCreate] = useState(false);
  const [title, setTitle] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const qc = useQueryClient();
  const { user } = useAuthStore();

  const { data: schedules = [] } = useQuery({
    queryKey: ['schedules', teamId],
    queryFn: () => schedulesApi.listByTeam(teamId).then((r) => r.data),
  });
  const createMut = useMutation({
    mutationFn: () => schedulesApi.create({ team_id: teamId, title, start_time: startTime, end_time: endTime || undefined }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['schedules', teamId] }); setShowCreate(false); setTitle(''); setStartTime(''); setEndTime(''); },
  });
  const statusMut = useMutation({
    mutationFn: ({ id, status }: { id: number; status: ScheduleStatus }) =>
      schedulesApi.patchStatus(id, status),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['schedules', teamId] }),
  });
  const deleteMut = useMutation({
    mutationFn: (id: number) => schedulesApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['schedules', teamId] }),
  });

  return (
    <div>
      {isLeader && (
        <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'flex-end' }}>
          <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ 일정 추가</button>
        </div>
      )}

      {schedules.length === 0 ? (
        <div className="empty-state"><div style={{ fontSize: '40px' }}>📅</div><p>등록된 일정이 없습니다.</p></div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {schedules.map((s: Schedule) => (
            <div key={s.id} className="card" style={{ padding: '16px', display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600 }}>{s.title}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  {new Date(s.start_time).toLocaleString('ko-KR')}
                  {s.end_time ? ` ~ ${new Date(s.end_time).toLocaleString('ko-KR')}` : ''}
                </div>
              </div>
              <select value={s.status}
                onChange={(e) => statusMut.mutate({ id: s.id, status: e.target.value as ScheduleStatus })}
                style={{ width: 'auto', padding: '6px 10px', borderRadius: '8px' }}>
                {(['PENDING', 'IN_PROGRESS', 'COMPLETED'] as ScheduleStatus[]).map((st) => (
                  <option key={st} value={st}>{STATUS_LABELS[st]}</option>
                ))}
              </select>
              {(isLeader || s.created_by === user?.id) && (
                <button className="btn btn-danger btn-sm" onClick={() => deleteMut.mutate(s.id)}>삭제</button>
              )}
            </div>
          ))}
        </div>
      )}

      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>일정 추가</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="form-group"><label>제목 *</label><input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="일정 제목" /></div>
              <div className="form-group"><label>시작 시간 *</label><input type="datetime-local" value={startTime} onChange={(e) => setStartTime(e.target.value)} /></div>
              <div className="form-group"><label>종료 시간</label><input type="datetime-local" value={endTime} onChange={(e) => setEndTime(e.target.value)} /></div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setShowCreate(false)}>취소</button>
              <button className="btn btn-primary" disabled={!title || !startTime} onClick={() => createMut.mutate()}>추가</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ===== 메모 탭 =====
function MemosTab({ teamId, isLeader }: { teamId: number; isLeader: boolean }) {
  const [showCreate, setShowCreate] = useState(false);
  const [memoTitle, setMemoTitle] = useState('');
  const [memoContent, setMemoContent] = useState('');
  const [selectedMemo, setSelectedMemo] = useState<number | null>(null);
  const [comment, setComment] = useState('');
  const qc = useQueryClient();
  const { user } = useAuthStore();

  // 내 역할 확인을 위해 멤버 목록 조회
  const { data: members = [] } = useQuery({
    queryKey: ['members', teamId],
    queryFn: () => teamsApi.getMembers(teamId).then((r) => r.data),
  });
  const myRole = members.find((m) => m.user_id === user?.id)?.role;
  const isGuest = myRole === 'guest';

  const { data: memos = [] } = useQuery({
    queryKey: ['memos', teamId],
    queryFn: () => memosApi.listByTeam(teamId).then((r) => r.data),
  });
  const { data: memoDetail } = useQuery({
    queryKey: ['memo', selectedMemo],
    queryFn: () => selectedMemo ? memosApi.get(selectedMemo).then((r) => r.data) : null,
    enabled: !!selectedMemo,
  });
  const createMut = useMutation({
    mutationFn: () => memosApi.create({ team_id: teamId, title: memoTitle, content: memoContent }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['memos', teamId] }); setShowCreate(false); setMemoTitle(''); setMemoContent(''); },
  });
  const commentMut = useMutation({
    mutationFn: () => selectedMemo ? memosApi.createComment(selectedMemo, comment) : Promise.reject(),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['memo', selectedMemo] }); setComment(''); },
  });
  const deleteMemoMut = useMutation({
    mutationFn: (id: number) => memosApi.delete(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['memos', teamId] }); setSelectedMemo(null); },
  });

  return (
    <div style={{ display: 'grid', gridTemplateColumns: selectedMemo ? '1fr 1fr' : '1fr', gap: '20px' }}>
      {/* 목록 */}
      <div>
        {!isGuest && (
          <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'flex-end' }}>
            <button className="btn btn-primary" onClick={() => setShowCreate(true)}>+ 메모 작성</button>
          </div>
        )}
        {memos.length === 0 ? (
          <div className="empty-state"><div style={{ fontSize: '40px' }}>📝</div><p>작성된 메모가 없습니다.</p></div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {memos.map((m: Memo) => (
              <div key={m.id} className="card" style={{ padding: '16px', cursor: 'pointer', borderColor: selectedMemo === m.id ? 'var(--accent)' : 'var(--border-subtle)', transition: 'var(--transition)' }}
                onClick={() => setSelectedMemo(selectedMemo === m.id ? null : m.id)}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ fontWeight: 600 }}>{m.title}</div>
                  {(isLeader || m.author_id === user?.id) && (
                    <button className="btn btn-danger btn-sm" onClick={(e) => { e.stopPropagation(); deleteMemoMut.mutate(m.id); }}>삭제</button>
                  )}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '6px' }}>
                  {m.author_name} · {new Date(m.created_at).toLocaleDateString('ko-KR')}
                </div>
                {m.content && <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '8px', lineHeight: 1.5 }}>{m.content}</p>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 상세 (댓글) */}
      {selectedMemo && memoDetail && (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxHeight: '70vh', overflow: 'hidden' }}>
          <div style={{ fontWeight: 700, fontSize: '16px' }}>{memoDetail.title}</div>
          <hr className="divider" style={{ margin: '0' }} />
          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {(memoDetail.comments || []).map((c) => (
              <div key={c.id} style={{ padding: '12px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)' }}>
                <div style={{ fontWeight: 600, fontSize: '13px' }}>{c.author_name}</div>
                <p style={{ fontSize: '13px', marginTop: '4px', color: 'var(--text-secondary)' }}>{c.content}</p>
              </div>
            ))}
            {memoDetail.comments?.length === 0 && <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>댓글이 없습니다.</p>}
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            {isGuest ? (
              <div style={{ flex: 1, padding: '10px', background: 'var(--bg-elevated)', borderRadius: '8px', fontSize: '13px', color: 'var(--text-muted)', textAlign: 'center' }}>
                게스트는 댓글을 작성할 수 없습니다.
              </div>
            ) : (
              <>
                <input value={comment} onChange={(e) => setComment(e.target.value)} placeholder="댓글 입력..." onKeyDown={(e) => e.key === 'Enter' && comment && commentMut.mutate()} />
                <button className="btn btn-primary btn-sm" disabled={!comment} onClick={() => commentMut.mutate()}>전송</button>
              </>
            )}
          </div>
        </div>
      )}

      {/* 생성 모달 */}
      {showCreate && (
        <div className="modal-overlay" onClick={() => setShowCreate(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>메모 작성</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div className="form-group"><label>제목 *</label><input value={memoTitle} onChange={(e) => setMemoTitle(e.target.value)} placeholder="메모 제목" /></div>
              <div className="form-group"><label>내용</label><textarea value={memoContent} onChange={(e) => setMemoContent(e.target.value)} placeholder="내용 입력..." rows={4} style={{ resize: 'vertical' }} /></div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setShowCreate(false)}>취소</button>
              <button className="btn btn-primary" disabled={!memoTitle} onClick={() => createMut.mutate()}>작성</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ===== 팀 페이지 =====
export default function TeamPage() {
  const { teamId } = useParams<{ teamId: string }>();
  const id = Number(teamId);
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [tab, setTab] = useState<'members' | 'schedules' | 'memos'>('members');
  const [editName, setEditName] = useState('');
  const [showEdit, setShowEdit] = useState(false);

  const { data: team } = useQuery<Team>({
    queryKey: ['team', id],
    queryFn: () => teamsApi.get(id).then((r) => r.data),
  });

  const updateMut = useMutation({
    mutationFn: () => teamsApi.update(id, { name: editName }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['team', id] }); qc.invalidateQueries({ queryKey: ['teams'] }); setShowEdit(false); },
  });

  const uploadImageMut = useMutation({
    mutationFn: (file: File) => teamsApi.uploadImage(id, file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['team', id] }),
  });

  const deleteMut = useMutation({
    mutationFn: () => teamsApi.delete(id),
    onSuccess: () => navigate('/'),
  });

  // 내 역할 확인 (리더만 관리 권한 부여)
  const { user } = useAuthStore();
  const { data: members = [], isLoading: isMembersLoading } = useQuery<TeamMember[]>({
    queryKey: ['members', id],
    queryFn: () => teamsApi.getMembers(id).then((r) => r.data),
  });

  const myRole = members.find((m) => Number(m.user_id) === Number(user?.id))?.role;
  const isLeader = myRole === 'leader';

  if (!team || isMembersLoading) return <div style={{ padding: '40px', color: 'var(--text-muted)' }}>불러오는 중...</div>;

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '40px 24px' }}>
      {/* 팀 헤더 */}
      <div className="card" style={{ marginBottom: '32px', display: 'flex', gap: '24px', alignItems: 'center' }}>
        <label 
          style={{ cursor: isLeader ? 'pointer' : 'default' }} 
          title={isLeader ? "이미지 수정" : ""}
        >
          <div style={{
            width: 80, height: 80, borderRadius: '20px', overflow: 'hidden',
            background: 'var(--accent-dim)', display: 'flex', alignItems: 'center',
            justifyContent: 'center', fontSize: '32px', fontWeight: 700,
            color: 'var(--accent-light)', border: '2px solid var(--border)',
          }}>
            {team.image_path
              ? <img src={team.image_path} alt={team.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              : team.name.slice(0, 2).toUpperCase()}
          </div>
          {isLeader && (
            <input type="file" accept="image/*" style={{ display: 'none' }}
              onChange={(e) => e.target.files?.[0] && uploadImageMut.mutate(e.target.files[0])} />
          )}
        </label>
        <div style={{ flex: 1 }}>
          <h1 style={{ fontSize: '24px', fontWeight: 800 }}>{team.name}</h1>
          {team.description && <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>{team.description}</p>}
          <p style={{ color: 'var(--text-muted)', fontSize: '12px', marginTop: '6px' }}>
            📅 {new Date(team.created_at).toLocaleDateString('ko-KR')} 생성
          </p>
        </div>
        
        {isLeader && (
          <div style={{ display: 'flex', gap: '8px' }}>
            <button className="btn btn-ghost btn-sm" onClick={() => { setEditName(team.name); setShowEdit(true); }}>수정</button>
            <button className="btn btn-danger btn-sm" onClick={() => window.confirm('팀을 삭제하시겠습니까?') && deleteMut.mutate()}>삭제</button>
          </div>
        )}
      </div>

      {/* 탭 */}
      <div className="tabs">
        {(['members', 'schedules', 'memos'] as const).map((t) => (
          <button key={t} className={`tab-btn ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>
            {{ members: '👥 멤버', schedules: '📅 일정', memos: '📝 메모' }[t]}
          </button>
        ))}
      </div>

      {tab === 'members' && <MembersTab teamId={id} isLeader={isLeader} />}
      {tab === 'schedules' && <SchedulesTab teamId={id} isLeader={isLeader} />}
      {tab === 'memos' && <MemosTab teamId={id} isLeader={isLeader} />}

      {/* 팀 이름 수정 모달 */}
      {showEdit && (
        <div className="modal-overlay" onClick={() => setShowEdit(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>팀 정보 수정</h2>
            <div className="form-group">
              <label>팀 이름</label>
              <input value={editName} onChange={(e) => setEditName(e.target.value)} />
            </div>
            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setShowEdit(false)}>취소</button>
              <button className="btn btn-primary" disabled={!editName} onClick={() => updateMut.mutate()}>저장</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
