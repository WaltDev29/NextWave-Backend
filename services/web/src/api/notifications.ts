import client from './client';
import type { AppNotification } from '../types/notification';

export const appNotificationsApi = {
  // 통합 인박스 알림 목록 조회
  getInbox: async (): Promise<AppNotification[]> => {
    const response = await client.get('/inbox/');
    return response.data;
  },

  // 알림 읽음 처리
  markAsRead: async (id: number): Promise<AppNotification> => {
    const response = await client.patch(`/inbox/${id}/read`);
    return response.data;
  },

  // 팀 초대 수락
  acceptInvite: async (id: number): Promise<{ message: string }> => {
    const response = await client.post(`/inbox/${id}/accept`);
    return response.data;
  },

  // 팀 초대 거절
  rejectInvite: async (id: number): Promise<{ message: string }> => {
    const response = await client.post(`/inbox/${id}/reject`);
    return response.data;
  },

  // 기존 일정 리마인더 (기존 notificationsApi 기능 통합)
  listReminders: () => client.get('/notifications/me'),
  createReminder: (scheduleId: number, remindAt: string) =>
    client.post('/notifications/', { schedule_id: scheduleId, remind_at: remindAt }),
  updateReminder: (id: number, data: { remind_at?: string; is_enabled?: boolean }) =>
    client.put(`/notifications/${id}`, data),
  deleteReminder: (id: number) => client.delete(`/notifications/${id}`),
};
