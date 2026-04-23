import apiClient from './client';
import type { Schedule, ScheduleAssignee, ScheduleStatus } from '../types';

export const schedulesApi = {
  listByTeam: (teamId: number) =>
    apiClient.get<Schedule[]>(`/teams/${teamId}/schedules`),
  get: (id: number) => apiClient.get<Schedule>(`/schedules/${id}`),
  create: (data: {
    team_id: number; title: string; start_time: string;
    end_time?: string; description?: string; status?: ScheduleStatus;
  }) => apiClient.post<Schedule>('/schedules/', data),
  update: (id: number, data: Partial<Omit<Schedule, 'id' | 'team_id' | 'created_at'>>) =>
    apiClient.put<Schedule>(`/schedules/${id}`, data),
  patchStatus: (id: number, status: ScheduleStatus) =>
    apiClient.patch<Schedule>(`/schedules/${id}/status`, { status }),
  delete: (id: number) => apiClient.delete(`/schedules/${id}`),

  // Assignees
  getAssignees: (scheduleId: number) =>
    apiClient.get<ScheduleAssignee[]>(`/schedules/${scheduleId}/assignees`),
  addAssignees: (scheduleId: number, userIds: number[]) =>
    apiClient.post(`/schedules/${scheduleId}/assignees`, { user_ids: userIds }),
  removeAssignee: (scheduleId: number, userId: number) =>
    apiClient.delete(`/schedules/${scheduleId}/assignees/${userId}`),
};
