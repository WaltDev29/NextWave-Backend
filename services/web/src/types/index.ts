// API 타입 정의

export interface User {
  id: number;
  email: string;
  username: string;
  job: string | null;
  age: number;
  gender: string | null;
  image_path: string | null;
  created_at: string;
}

export interface Team {
  id: number;
  name: string;
  description: string | null;
  image_path: string | null;
  created_at: string;
}

export interface TeamMember {
  id: number;
  team_id: number;
  user_id: number;
  team_name: string;
  user_name: string;
  role: 'leader' | 'member' | 'guest';
}

export type ScheduleStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';

export interface Schedule {
  id: number;
  team_id: number;
  created_by: number;
  title: string;
  description: string | null;
  start_time: string;
  end_time: string | null;
  status: ScheduleStatus;
  assignees: ScheduleAssignee[];
  created_at: string;
}

export interface ScheduleAssignee {
  id: number;
  schedule_id: number;
  user_id: number;
  user_name: string;
}

export interface Memo {
  id: number;
  team_id: number;
  schedule_id: number | null;
  author_id: number;
  author_name: string;
  title: string;
  content: string | null;
  created_at: string;
}

export interface MemoMention {
  id: number;
  user_id: number;
  user_name: string;
}

export interface Comment {
  id: number;
  memo_id: number;
  author_id: number;
  author_name: string;
  content: string;
  created_at: string;
}

export interface MemoDetail extends Memo {
  mentions: MemoMention[];
  comments: Comment[];
}

export interface Notification {
  id: number;
  user_id: number;
  schedule_id: number;
  remind_at: string;
  is_enabled: boolean;
  created_at: string;
}

export * from './notification';
