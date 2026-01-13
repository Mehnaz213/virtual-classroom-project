import type { LabelBreakdown } from '../types';
import { formatLabel, getLabelColor } from '../utils/labels';

type Props = {
  data: LabelBreakdown[];
};

const LabelLegend = ({ data }: Props) => {
  if (!data.length) {
    return (
      <div className="card">
        <header className="card-header">
          <h3>Attention Labels</h3>
        </header>
        <p className="muted">No events yet.</p>
      </div>
    );
  }

  return (
    <div className="card">
      <header className="card-header">
        <h3>Attention Labels</h3>
      </header>
      <ul className="label-legend">
        {data.map((entry) => (
          <li key={entry.name}>
            <span>
              <span className="swatch" style={{ backgroundColor: getLabelColor(entry.name) }} />
              {formatLabel(entry.name)}
            </span>
            <strong>{entry.percentage}%</strong>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default LabelLegend;


