// Focus Mate - Attention Label Utilities

import type { AttentionLabel } from '../types';

/**
 * All 11 attention labels supported by Focus Mate
 */
export const ATTENTION_LABELS: AttentionLabel[] = [
  'focused',
  'looking_left',
  'looking_right',
  'looking_up',
  'looking_down',
  'engaged',
  'partial_engaged',
  'sleepy',
  'distracted_by_multi_face',
  'no_face',
  'unknown',
];

/**
 * Color mapping for each attention label
 */
export const ATTENTION_LABEL_COLORS: Record<AttentionLabel, string> = {
  focused: '#10B981',                    // green - best state
  engaged: '#34D399',                    // light green
  partial_engaged: '#F59E0B',            // amber
  looking_left: '#3B82F6',               // blue
  looking_right: '#8B5CF6',              // purple
  looking_up: '#06B6D4',                 // cyan
  looking_down: '#14B8A6',               // teal
  sleepy: '#EF4444',                     // red - alert
  distracted_by_multi_face: '#F97316',  // orange - warning
  no_face: '#6B7280',                    // gray
  unknown: '#9CA3AF',                    // light gray
};

/**
 * Get hex color for a given attention label
 */
export const getLabelColor = (label: AttentionLabel): string => {
  return ATTENTION_LABEL_COLORS[label] ?? '#6B7280';
};

/**
 * Format label for human-readable display
 */
export const formatLabel = (label: AttentionLabel): string => {
  const formatted: Record<AttentionLabel, string> = {
    focused: 'Focused',
    engaged: 'Engaged',
    partial_engaged: 'Partially Engaged',
    looking_left: 'Looking Left',
    looking_right: 'Looking Right',
    looking_up: 'Looking Up',
    looking_down: 'Looking Down',
    sleepy: 'Sleepy',
    distracted_by_multi_face: 'Multiple Faces',
    no_face: 'No Face',
    unknown: 'Unknown',
  };
  return formatted[label] ?? label;
};

/**
 * Get label category for grouping
 */
export const getLabelCategory = (label: AttentionLabel): 'positive' | 'neutral' | 'negative' => {
  if (label === 'focused' || label === 'engaged') return 'positive';
  if (label === 'sleepy' || label === 'no_face' || label === 'distracted_by_multi_face') return 'negative';
  return 'neutral';
};

/**
 * Get label priority for sorting (higher = more important)
 */
export const getLabelPriority = (label: AttentionLabel): number => {
  const priorities: Record<AttentionLabel, number> = {
    sleepy: 10,                      // Highest priority - needs attention
    distracted_by_multi_face: 9,
    no_face: 8,
    looking_down: 7,
    looking_up: 6,
    looking_left: 5,
    looking_right: 5,
    partial_engaged: 4,
    unknown: 3,
    engaged: 2,
    focused: 1,                      // Lowest priority - everything is good
  };
  return priorities[label] ?? 0;
};

/**
 * Check if label indicates student needs attention
 */
export const isAlertLabel = (label: AttentionLabel): boolean => {
  return label === 'sleepy' || label === 'no_face' || label === 'distracted_by_multi_face';
};

/**
 * Check if label indicates good engagement
 */
export const isEngagedLabel = (label: AttentionLabel): boolean => {
  return label === 'focused' || label === 'engaged';
};
