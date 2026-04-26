import apiClient from './client';
import type { User } from '../types';

export const authApi = {
  signup: (data: { email: string; username: string; password: string; job?: string; age: number; gender?: string; purpose?: string }) =>
    apiClient.post<User>('/users/signup', data),

  login: async (email: string, password: string): Promise<string> => {
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', password);
    const res = await apiClient.post<{ access_token: string; token_type: string }>(
      '/login/access-token',
      form,
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
    );
    return res.data.access_token;
  },
};

export const usersApi = {
  me: () => apiClient.get<User>('/users/me'),

  updateMe: (data: { username?: string; password?: string; job?: string; age?: number; gender?: string }) =>
    apiClient.put<User>('/users/me', data),

  uploadImage: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return apiClient.patch<User>('/users/me/image', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};
