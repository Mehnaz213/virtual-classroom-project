import type { EngagementLevel } from '../types';

export const levelToScore = (level: EngagementLevel) => {
  switch (level) {
    case 'ENGAGED':
      return 1;
    case 'PARTIAL':
      return 0.6;
    default:
      return 0.2;
  }
};

export const levelToColor = (level: EngagementLevel) => {
  switch (level) {
    case 'ENGAGED':
      return '#16a34a';
    case 'PARTIAL':
      return '#f97316';
    default:
      return '#dc2626';
  }
};

export const getEngagementLabel = (ratio: number) => {
  if (ratio >= 0.75) return 'High';
  if (ratio >= 0.4) return 'Medium';
  return 'Low';
};

