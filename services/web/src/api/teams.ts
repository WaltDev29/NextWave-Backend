import apiClient from './client';
import type { Team, TeamMember } from '../types';

export const teamsApi = {
  list: () => apiClient.get<Team[]>('/teams/'),
  get: (id: number) => apiClient.get<Team>(`/teams/${id}`),
  create: (name: string, description?: string) =>
    apiClient.post<Team>('/teams/', { name, description }),
  update: (id: number, data: { name?: string; description?: string }) =>
    apiClient.put<Team>(`/teams/${id}`, data),
  delete: (id: number) => apiClient.delete(`/teams/${id}`),
  uploadImage: (id: number, file: File) => {
    const form = new FormData();
    form.append('file', file);
    return apiClient.patch<Team>(`/teams/${id}/image`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Members
  getMembers: (teamId: number) =>
    apiClient.get<TeamMember[]>(`/teams/${teamId}/members`),
  addMember: (teamId: number, email: string, role: string) =>
    apiClient.post<TeamMember>(`/teams/${teamId}/members`, { email, role }),
  removeMember: (teamId: number, userId: number) =>
    apiClient.delete(`/teams/${teamId}/members/${userId}`),
};
