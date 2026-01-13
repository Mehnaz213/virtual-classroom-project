export type EngagementLevel = 'ENGAGED' | 'PARTIAL' | 'NOT_ENGAGED';

export type AttentionLabel =
  | 'focused'
  | 'looking_left'
  | 'looking_right'
  | 'looking_up'
  | 'looking_down'
  | 'engaged'
  | 'partial_engaged'
  | 'sleepy'
  | 'distracted_by_multi_face'
  | 'no_face'
  | 'unknown';

export type LabelConfidence = {
  name: AttentionLabel;
  confidence: number;
};

export type SessionSummary = {
  id: number;
  code: string;
  topic: string;
  teacher_id: number;
  start_time: string;
  is_live: boolean;
  attendee_count: number;
  avg_engagement: number;
};

export type AttendanceResponse = {
  attendance_id: number;
  student_id: number;
  student_name: string;
  last_seen_at: string;
  lock_mode: boolean;
  latest_level: EngagementLevel;
};

export type TimelinePoint = {
  timestamp: string;
  student_name: string;
  level: EngagementLevel;
  tab_switch: boolean;
  multiple_faces: boolean;
  labels: LabelConfidence[];
};

export type LabelBreakdown = {
  name: AttentionLabel;
  count: number;
  percentage: number;
};

export type DashboardResponse = {
  session_id: number;
  topic: string;
  is_live: boolean;
  start_time: string;
  attendance: AttendanceResponse[];
  engagement_ratio: number;
  tab_switch_alerts: string[];
  timeline: TimelinePoint[];
  label_breakdown: LabelBreakdown[];
  sleepy_alerts: string[];
  lock_violations?: string[];
};

export type JoinResponse = {
  attendance_id: number;
  session_code: string;
  lock_mode: boolean;
};

