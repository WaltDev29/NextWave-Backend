import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

// Nginx 리버스 프록시를 통해 같은 도메인으로 API 접근
const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

// 요청 인터셉터: JWT 토큰 자동 주입
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// 응답 인터셉터: 401 시 로그아웃 처리
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 || err.response?.status === 403) {
      const msg = err.response?.data?.detail || '';
      // 토큰 만료 오류 시 자동 로그아웃
      if (msg.includes('토큰') || err.response?.status === 401) {
        useAuthStore.getState().logout();
        window.location.href = '/auth';
      }
    }
    return Promise.reject(err);
  }
);

export default apiClient;
