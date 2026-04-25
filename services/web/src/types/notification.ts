export type NotificationType = 
  | 'TEAM_INVITE' 
  | 'INVITE_ACCEPTED' 
  | 'INVITE_REJECTED' 
  | 'SCHEDULE_ASSIGN' 
  | 'MEMO_MENTION' 
  | 'COMMENT' 
  | 'REMINDER';

export interface AppNotification {
  id: number;
  receiver_id: number;
  sender_id: number | null;
  sender_name: string | null;
  type: NotificationType;
  title: string;
  content: string;
  related_id: number | null;
  is_read: boolean;
  created_at: string;
}
