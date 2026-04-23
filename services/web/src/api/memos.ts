import apiClient from './client';
import type { Memo, MemoDetail, Comment } from '../types';

export const memosApi = {
  listByTeam: (teamId: number) =>
    apiClient.get<Memo[]>(`/teams/${teamId}/memos`),
  get: (id: number) => apiClient.get<MemoDetail>(`/memos/${id}`),
  create: (data: { team_id: number; title: string; content?: string; schedule_id?: number }) =>
    apiClient.post<Memo>('/memos/', data),
  update: (id: number, data: { title?: string; content?: string }) =>
    apiClient.put<Memo>(`/memos/${id}`, data),
  delete: (id: number) => apiClient.delete(`/memos/${id}`),

  // Comments
  createComment: (memoId: number, content: string) =>
    apiClient.post<Comment>(`/memos/${memoId}/comments`, { content }),
  deleteComment: (memoId: number, commentId: number) =>
    apiClient.delete(`/memos/${memoId}/comments/${commentId}`),
};

export const notificationsApi = {
  listMine: () => apiClient.get('/notifications/me'),
  create: (scheduleId: number, remindAt: string) =>
    apiClient.post('/notifications/', { schedule_id: scheduleId, remind_at: remindAt }),
  update: (id: number, data: { remind_at?: string; is_enabled?: boolean }) =>
    apiClient.put(`/notifications/${id}`, data),
  delete: (id: number) => apiClient.delete(`/notifications/${id}`),
};
