import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { authApi, usersApi } from '../api/auth';

export default function AuthPage() {
  const [tab, setTab] = useState<'login' | 'signup'>('login');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [job, setJob] = useState('');
  const [age, setAge] = useState<string>('');
  const [gender, setGender] = useState('');
  const [purpose, setPurpose] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { setToken, setUser } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (tab === 'signup') {
        const ageNum = parseInt(age);
        if (isNaN(ageNum)) throw new Error('나이를 정확히 입력해주세요.');
        await authApi.signup({
          email, username, password,
          job: job || undefined,
          age: ageNum,
          gender: gender || undefined,
          purpose: purpose || undefined,
        });
      }
      const token = await authApi.login(email, password);
      setToken(token);
      const { data: user } = await usersApi.me();
      setUser(user);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || '오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', background: 'var(--bg-base)', padding: '20px',
    }}>
      <div style={{ width: '100%', maxWidth: '420px' }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <div style={{
            fontSize: '32px', fontWeight: 800, letterSpacing: '-1px',
            background: 'linear-gradient(135deg, #6c63ff, #a78bfa)',
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>NextWave</div>
          <p style={{ color: 'var(--text-secondary)', marginTop: '8px', fontSize: '14px' }}>
            팀 협업 플랫폼
          </p>
        </div>

        <div className="card" style={{ padding: '32px' }}>
          {/* Tabs */}
          <div style={{ display: 'flex', marginBottom: '24px', background: 'var(--bg-elevated)', borderRadius: '10px', padding: '4px' }}>
            {(['login', 'signup'] as const).map((t) => (
              <button key={t} onClick={() => { setTab(t); setError(''); }}
                style={{
                  flex: 1, padding: '10px', border: 'none', borderRadius: '8px',
                  fontWeight: 600, fontSize: '14px', transition: 'var(--transition)',
                  background: tab === t ? 'var(--accent)' : 'transparent',
                  color: tab === t ? '#fff' : 'var(--text-muted)',
                  cursor: 'pointer',
                }}>
                {t === 'login' ? '로그인' : '회원가입'}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="form-group">
              <label>이메일</label>
              <input type="email" placeholder="이메일 주소" value={email}
                onChange={(e) => setEmail(e.target.value)} required />
            </div>
            {tab === 'signup' && (
              <>
                <div className="form-group">
                  <label>이름 *</label>
                  <input type="text" placeholder="닉네임" value={username}
                    onChange={(e) => setUsername(e.target.value)} required />
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <div className="form-group" style={{ flex: 1 }}>
                    <label>나이 *</label>
                    <input type="number" placeholder="만 나이" value={age}
                      onChange={(e) => setAge(e.target.value)} required />
                  </div>
                  <div className="form-group" style={{ flex: 1 }}>
                    <label>성별</label>
                    <select value={gender} onChange={(e) => setGender(e.target.value)}
                      style={{ padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg-elevated)', color: 'var(--text-main)', fontSize: '14px' }}>
                      <option value="">성별 선택</option>
                      <option value="남">남성</option>
                      <option value="여">여성</option>
                      <option value="무관">무관</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label>직업</label>
                  <input type="text" placeholder="직장인, 학생 등" value={job}
                    onChange={(e) => setJob(e.target.value)} />
                </div>
                <div className="form-group">
                  <label>사용 목적</label>
                  <textarea placeholder="어떤 용도로 사용하시나요?" value={purpose}
                    onChange={(e) => setPurpose(e.target.value)} rows={2}
                    style={{ padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg-elevated)', color: 'var(--text-main)', fontSize: '14px', resize: 'none' }} />
                </div>
              </>
            )}
            <div className="form-group">
              <label>비밀번호</label>
              <input type="password" placeholder="비밀번호" value={password}
                onChange={(e) => setPassword(e.target.value)} required />
            </div>
            {error && <p className="error-msg">{error}</p>}
            <button type="submit" className="btn btn-primary" disabled={loading}
              style={{ width: '100%', justifyContent: 'center', padding: '12px', marginTop: '4px' }}>
              {loading ? '처리 중...' : tab === 'login' ? '로그인' : '가입하기'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
