import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useAuthStore } from '../../stores/authStore';
import { notificationsApi } from '../../api/memos';
import type { Notification } from '../../types';

export default function Header() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const [notifOpen, setNotifOpen] = useState(false);

  const { data: notifs = [] } = useQuery<Notification[]>({
    queryKey: ['notifications'],
    queryFn: () => notificationsApi.listMine().then((r) => r.data),
    refetchInterval: 60_000, // 1분마다 폴링
  });

  const enabledCount = notifs.filter((n) => n.is_enabled).length;

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  return (
    <>
      <header style={{
        height: '60px', background: 'var(--bg-surface)',
        borderBottom: '1px solid var(--border-subtle)',
        display: 'flex', alignItems: 'center',
        padding: '0 24px', gap: '24px', flexShrink: 0,
        position: 'sticky', top: 0, zIndex: 99,
      }}>
        {/* 로고 */}
        <Link to="/" style={{
          fontSize: '18px', fontWeight: 800, letterSpacing: '-0.5px',
          background: 'linear-gradient(135deg, #6c63ff, #a78bfa)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
        }}>NextWave</Link>

        <div style={{ flex: 1 }} />

        {/* 알림 버튼 */}
        <button onClick={() => setNotifOpen((v) => !v)} style={{
          position: 'relative', background: 'none', border: 'none',
          color: 'var(--text-secondary)', fontSize: '20px', cursor: 'pointer',
          padding: '4px 8px', borderRadius: '8px', transition: 'var(--transition)',
        }}
          onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-elevated)')}
          onMouseLeave={(e) => (e.currentTarget.style.background = 'none')}>
          🔔
          {enabledCount > 0 && (
            <span style={{
              position: 'absolute', top: 0, right: 0,
              background: 'var(--accent)', color: '#fff',
              fontSize: '10px', fontWeight: 700,
              width: '16px', height: '16px', borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>{enabledCount}</span>
          )}
        </button>

        {/* 프로필 */}
        <Link to="/profile" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none' }}>
          <div style={{
            width: 32, height: 32, borderRadius: '50%', background: 'var(--accent-dim)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '13px', fontWeight: 700, color: 'var(--accent-light)',
            border: '1px solid var(--border)', overflow: 'hidden',
          }}>
            {user?.image_path
              ? <img src={user.image_path} alt="me" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              : (user?.username || '?').slice(0, 2).toUpperCase()}
          </div>
          <span style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-primary)' }}>{user?.username}</span>
        </Link>

        <button className="btn btn-ghost btn-sm" onClick={handleLogout}>로그아웃</button>
      </header>

      {/* 알림 사이드바 */}
      <div className={`notif-sidebar ${notifOpen ? 'open' : ''}`}>
        <div className="notif-header">
          <span style={{ fontWeight: 700 }}>🔔 알림</span>
          <button onClick={() => setNotifOpen(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '20px', cursor: 'pointer' }}>✕</button>
        </div>
        <div className="notif-body">
          {notifs.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '40px', fontSize: '13px' }}>알림이 없습니다.</p>
          ) : (
            notifs.map((n) => (
              <div key={n.id} className={`notif-item ${n.is_enabled ? '' : 'disabled'}`}>
                <div style={{ fontWeight: 600, fontSize: '13px' }}>📅 일정 알림</div>
                <div className="notif-time">{new Date(n.remind_at).toLocaleString('ko-KR')}</div>
                {!n.is_enabled && <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>비활성화됨</div>}
              </div>
            ))
          )}
        </div>
      </div>
      {notifOpen && <div onClick={() => setNotifOpen(false)} style={{ position: 'fixed', inset: 0, zIndex: 199 }} />}
    </>
  );
}
