import { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usersApi } from '../api/auth';
import { useAuthStore } from '../stores/authStore';

export default function ProfilePage() {
  const { user, setUser } = useAuthStore();
  const qc = useQueryClient();
  const [username, setUsername] = useState(user?.username || '');
  const [password, setPassword] = useState('');
  const [msg, setMsg] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);

  const { data: meData } = useQuery({
    queryKey: ['me'],
    queryFn: () => usersApi.me().then((r) => r.data),
  });
  const me = meData || user;

  const updateMut = useMutation({
    mutationFn: () => usersApi.updateMe({ username: username || undefined, password: password || undefined }),
    onSuccess: ({ data }) => { setUser(data); setPassword(''); setMsg('저장되었습니다!'); setTimeout(() => setMsg(''), 2000); },
    onError: (e: any) => setMsg(e.response?.data?.detail || '오류가 발생했습니다.'),
  });

  const uploadMut = useMutation({
    mutationFn: (file: File) => usersApi.uploadImage(file),
    onSuccess: ({ data }) => { setUser(data); qc.invalidateQueries({ queryKey: ['me'] }); },
  });

  return (
    <div style={{ maxWidth: 600, margin: '0 auto', padding: '40px 24px' }}>
      <div className="page-header">
        <h1>내 프로필</h1>
        <p>계정 정보를 수정합니다.</p>
      </div>

      {/* 프로필 이미지 */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px', marginBottom: '24px', padding: '32px' }}>
        <div onClick={() => fileRef.current?.click()} style={{ cursor: 'pointer', position: 'relative' }}>
          <div style={{
            width: 100, height: 100, borderRadius: '50%', overflow: 'hidden',
            background: me?.image_path ? 'none' : 'var(--accent-dim)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '38px', fontWeight: 800, color: 'var(--accent-light)',
            border: '3px solid var(--accent)',
          }}>
            {me?.image_path
              ? <img src={me.image_path} alt="profile" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              : (me?.username || '?').slice(0, 2).toUpperCase()}
          </div>
          <div style={{
            position: 'absolute', bottom: 0, right: 0,
            width: 28, height: 28, borderRadius: '50%',
            background: 'var(--accent)', display: 'flex', alignItems: 'center',
            justifyContent: 'center', fontSize: '14px', border: '2px solid var(--bg-surface)',
          }}>✏️</div>
        </div>
        <input ref={fileRef} type="file" accept="image/*" style={{ display: 'none' }}
          onChange={(e) => e.target.files?.[0] && uploadMut.mutate(e.target.files[0])} />
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontWeight: 700, fontSize: '20px' }}>{me?.username}</div>
          <div style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '4px' }}>{me?.email}</div>
        </div>
      </div>

      {/* 정보 수정 폼 */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 700 }}>정보 수정</h2>
        <div className="form-group">
          <label>닉네임</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="변경할 닉네임" />
        </div>
        <div className="form-group">
          <label>새 비밀번호</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="변경할 비밀번호 (입력 시 변경)" />
        </div>
        {msg && <p style={{ fontSize: '13px', color: msg.includes('저장') ? 'var(--success)' : 'var(--danger)' }}>{msg}</p>}
        <button className="btn btn-primary" disabled={updateMut.isPending || (!username && !password)}
          onClick={() => updateMut.mutate()} style={{ alignSelf: 'flex-end' }}>
          {updateMut.isPending ? '저장 중...' : '저장'}
        </button>
      </div>
    </div>
  );
}
