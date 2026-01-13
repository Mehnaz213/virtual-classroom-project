import { getEngagementLabel } from '../utils/engagement';

type Props = {
  ratio: number;
};

const EngagementMeter = ({ ratio }: Props) => {
  const percentage = Math.round(ratio * 100);
  const label = getEngagementLabel(ratio);

  return (
    <div className="card">
      <header className="card-header">
        <h3>Engagement</h3>
        <span>{label}</span>
      </header>
      <div className="meter">
        <div className="meter-fill" style={{ width: `${percentage}%` }} />
      </div>
      <p className="muted">{percentage}% of attendees are actively engaged.</p>
    </div>
  );
};

export default EngagementMeter;

