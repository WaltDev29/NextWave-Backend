import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '../../stores/authStore';
import { appNotificationsApi } from '../../api/notifications';
import type { AppNotification, NotificationType } from '../../types/notification';

export default function Header() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [notifOpen, setNotifOpen] = useState(false);

  // 알림 목록 가져오기
  const { data: notifications = [] } = useQuery<AppNotification[]>({
    queryKey: ['notifications-inbox'],
    queryFn: () => appNotificationsApi.getInbox(),
    refetchInterval: 10_000, 
    enabled: !!user,
  });

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  // 알림 읽음 처리 Mutation
  const markReadMutation = useMutation({
    mutationFn: (id: number) => appNotificationsApi.markAsRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications-inbox'] });
    },
  });

  // 초대 수락 Mutation
  const acceptMutation = useMutation({
    mutationFn: (id: number) => appNotificationsApi.acceptInvite(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications-inbox'] });
      queryClient.invalidateQueries({ queryKey: ['teams'] }); 
      queryClient.invalidateQueries({ queryKey: ['members'] });
      alert('팀 초대를 수락했습니다!');
    },
  });

  // 초대 거절 Mutation
  const rejectMutation = useMutation({
    mutationFn: (id: number) => appNotificationsApi.rejectInvite(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications-inbox'] });
      alert('팀 초대를 거절했습니다.');
    },
  });

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };

  const getNotifIcon = (type: NotificationType) => {
    switch (type) {
      case 'TEAM_INVITE': return '✉️';
      case 'SCHEDULE_ASSIGN': return '📅';
      case 'MEMO_MENTION': return '🏷️';
      case 'COMMENT': return '💬';
      case 'INVITE_ACCEPTED': return '✅';
      case 'INVITE_REJECTED': return '❌';
      default: return '🔔';
    }
  };

  const getTagClass = (type: NotificationType) => {
    if (type === 'TEAM_INVITE') return 'invite';
    if (type === 'MEMO_MENTION') return 'memo';
    if (type === 'COMMENT') return 'comment';
    return '';
  };

  const handleNotifClick = (noti: AppNotification) => {
    if (!noti.is_read) {
      markReadMutation.mutate(noti.id);
    }
    if (noti.type === 'MEMO_MENTION' || noti.type === 'COMMENT') {
      if (noti.related_id) navigate(`/memos/${noti.related_id}`);
    } else if (noti.type === 'SCHEDULE_ASSIGN') {
      if (noti.related_id) navigate(`/teams/schedules/${noti.related_id}`);
    }
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
        <Link to="/" style={{
          fontSize: '18px', fontWeight: 800, letterSpacing: '-0.5px',
          background: 'linear-gradient(135deg, #6c63ff, #a78bfa)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
        }}>NextWave</Link>

        <div style={{ flex: 1 }} />

        <button onClick={() => setNotifOpen((v) => !v)} style={{
          position: 'relative', background: 'none', border: 'none',
          color: 'var(--text-secondary)', fontSize: '20px', cursor: 'pointer',
          padding: '4px 8px', borderRadius: '8px', transition: 'var(--transition)',
        }}
          onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-elevated)')}
          onMouseLeave={(e) => (e.currentTarget.style.background = 'none')}>
          🔔
          {unreadCount > 0 && <span className="notif-badge">{unreadCount}</span>}
        </button>

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

      <div className={`notif-sidebar ${notifOpen ? 'open' : ''}`}>
        <div className="notif-header">
          <span style={{ fontWeight: 700, fontSize: '16px' }}>🔔 알림 센터</span>
          <button onClick={() => setNotifOpen(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '20px', cursor: 'pointer' }}>✕</button>
        </div>
        <div className="notif-body">
          {notifications.length === 0 ? (
            <div className="empty-state">
              <p>아직 도착한 알림이 없습니다.</p>
            </div>
          ) : (
            notifications.map((n) => (
              <div 
                key={n.id} 
                className={`notif-item ${n.is_read ? '' : 'unread'}`}
                onClick={() => handleNotifClick(n)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <span className={`notif-type-tag ${getTagClass(n.type)}`}>
                    {getNotifIcon(n.type)} {n.type}
                  </span>
                  <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                    {new Date(n.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div style={{ fontWeight: 600, fontSize: '14px', marginBottom: '2px' }}>{n.title}</div>
                <div className="notif-content">{n.content}</div>
                
                {n.type === 'TEAM_INVITE' && !n.is_read && (
                  <div className="notif-actions" onClick={e => e.stopPropagation()}>
                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={() => acceptMutation.mutate(n.id)}
                      disabled={acceptMutation.isPending}
                    >
                      {acceptMutation.isPending ? '처리중...' : '수락'}
                    </button>
                    <button 
                      className="btn btn-ghost btn-sm"
                      onClick={() => rejectMutation.mutate(n.id)}
                      disabled={rejectMutation.isPending}
                    >
                      거절
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
      {notifOpen && <div onClick={() => setNotifOpen(false)} style={{ position: 'fixed', inset: 0, zIndex: 199 }} />}
    </>
  );
}
