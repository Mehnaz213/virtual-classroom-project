import { describe, expect, it } from 'vitest';

import { getEngagementLabel, levelToColor, levelToScore } from '../utils/engagement';

describe('engagement helpers', () => {
  it('maps levels to scores', () => {
    expect(levelToScore('ENGAGED')).toBe(1);
    expect(levelToScore('PARTIAL')).toBeCloseTo(0.6);
    expect(levelToScore('NOT_ENGAGED')).toBeCloseTo(0.2);
  });

  it('maps levels to colors', () => {
    expect(levelToColor('ENGAGED')).toBe('#16a34a');
    expect(levelToColor('PARTIAL')).toBe('#f97316');
    expect(levelToColor('NOT_ENGAGED')).toBe('#dc2626');
  });

  it('labels engagement ratio buckets', () => {
    expect(getEngagementLabel(0.8)).toBe('High');
    expect(getEngagementLabel(0.5)).toBe('Medium');
    expect(getEngagementLabel(0.1)).toBe('Low');
  });
});

