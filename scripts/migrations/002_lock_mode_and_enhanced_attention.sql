-- Focus Mate Migration 002: Lock Mode and Enhanced Attention Detection
-- Adds lock mode support and enhanced attention tracking fields

-- Add lock mode fields to attendance table
ALTER TABLE attendance ADD COLUMN IF NOT EXISTS lock_mode BOOLEAN DEFAULT FALSE;

-- Add enhanced attention fields to engagement_events table
ALTER TABLE engagement_events ADD COLUMN IF NOT EXISTS eyes_open_prob REAL DEFAULT 1.0;
ALTER TABLE engagement_events ADD COLUMN IF NOT EXISTS gaze_yaw REAL DEFAULT 0.0;
ALTER TABLE engagement_events ADD COLUMN IF NOT EXISTS gaze_pitch REAL DEFAULT 0.0;
ALTER TABLE engagement_events ADD COLUMN IF NOT EXISTS head_yaw REAL DEFAULT 0.0;
ALTER TABLE engagement_events ADD COLUMN IF NOT EXISTS head_pitch REAL DEFAULT 0.0;

-- Add lock mode fields to tab_switch_events table
ALTER TABLE tab_switch_events ADD COLUMN IF NOT EXISTS tab_visible BOOLEAN DEFAULT TRUE;
ALTER TABLE tab_switch_events ADD COLUMN IF NOT EXISTS lock_mode_active BOOLEAN DEFAULT FALSE;
ALTER TABLE tab_switch_events ADD COLUMN IF NOT EXISTS lock_mode_violation BOOLEAN DEFAULT FALSE;

-- Create index for lock mode violations (for dashboard queries)
CREATE INDEX IF NOT EXISTS idx_tab_switch_lock_violations 
ON tab_switch_events(attendance_id, lock_mode_violation) 
WHERE lock_mode_violation = TRUE;

-- Create index for sleepy events (for dashboard alerts)
CREATE INDEX IF NOT EXISTS idx_engagement_labels 
ON engagement_events(attendance_id, labels);

-- Add comments for documentation
COMMENT ON COLUMN attendance.lock_mode IS 'Whether lock mode is enabled for this student';
COMMENT ON COLUMN tab_switch_events.lock_mode_violation IS 'Whether this tab switch violated lock mode';
COMMENT ON COLUMN engagement_events.eyes_open_prob IS 'Probability that eyes are open (0.0-1.0)';
COMMENT ON COLUMN engagement_events.gaze_yaw IS 'Horizontal gaze angle in degrees';
COMMENT ON COLUMN engagement_events.gaze_pitch IS 'Vertical gaze angle in degrees';
