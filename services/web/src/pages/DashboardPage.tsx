import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { teamsApi } from '../api/teams';
import { useAuthStore } from '../stores/authStore';
import type { Team } from '../types';

function Avatar({ name, src, size = 56 }: { name: string; src?: string | null; size?: number }) {
  const initials = name.slice(0, 2).toUpperCase();
  return (
    <div style={{
      width: size, height: size, borderRadius: '14px',
      background: src ? 'none' : 'var(--accent-dim)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: size * 0.35, fontWeight: 700, color: 'var(--accent-light)',
      overflow: 'hidden', flexShrink: 0, border: '2px solid var(--border)',
    }}>
      {src ? <img src={src} alt={name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} /> : initials}
    </div>
  );
}

function CreateTeamModal({ onClose }: { onClose: () => void }) {
  const [name, setName] = useState('');
  const [desc, setDesc] = useState('');
  const qc = useQueryClient();
  const { mutate, isPending } = useMutation({
    mutationFn: () => teamsApi.create(name, desc || undefined),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['teams'] }); onClose(); },
  });
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>새 팀 만들기</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="form-group">
            <label>팀 이름 *</label>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="팀 이름 입력" />
          </div>
          <div className="form-group">
            <label>설명 (선택)</label>
            <textarea value={desc} onChange={(e) => setDesc(e.target.value)}
              placeholder="팀 설명을 입력하세요" rows={3}
              style={{ resize: 'vertical' }} />
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose}>취소</button>
          <button className="btn btn-primary" disabled={!name || isPending}
            onClick={() => mutate()}>
            {isPending ? '생성 중...' : '팀 만들기'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const navigate = useNavigate();
  const [showCreate, setShowCreate] = useState(false);

  const { data: teams = [], isLoading } = useQuery({
    queryKey: ['teams'],
    queryFn: () => teamsApi.list().then((r) => r.data),
  });

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '40px 24px' }}>
      {/* 헤더 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '40px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 800 }}>
            안녕하세요, <span style={{ color: 'var(--accent-light)' }}>{user?.username}</span> 님 👋
          </h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: '4px' }}>내가 소속된 팀 목록입니다.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreate(true)}>
          + 새 팀 만들기
        </button>
      </div>

      {/* 팀 카드 그리드 */}
      {isLoading ? (
        <p style={{ color: 'var(--text-muted)' }}>불러오는 중...</p>
      ) : teams.length === 0 ? (
        <div className="empty-state">
          <div style={{ fontSize: '48px' }}>🏖️</div>
          <p>아직 소속된 팀이 없습니다. 새 팀을 만들어 보세요!</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '20px' }}>
          {teams.map((team: Team) => (
            <div key={team.id} className="card" onClick={() => navigate(`/teams/${team.id}`)}
              style={{ cursor: 'pointer', transition: 'var(--transition)', display: 'flex', flexDirection: 'column', gap: '16px' }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'var(--accent)')}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--border-subtle)')}>
              <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                <Avatar name={team.name} src={team.image_path} size={52} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 700, fontSize: '16px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {team.name}
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '12px', marginTop: '2px' }}>
                    {new Date(team.created_at).toLocaleDateString('ko-KR')} 생성
                  </div>
                </div>
              </div>
              {team.description && (
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>{team.description}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {showCreate && <CreateTeamModal onClose={() => setShowCreate(false)} />}
    </div>
  );
}
