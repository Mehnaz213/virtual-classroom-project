type Props = {
  enabled: boolean;
  attempts: number;
  onReengage: () => void;
};

const LockModeStatus = ({ enabled, attempts, onReengage }: Props) => (
  <div className="card lock-mode">
    <header className="card-header">
      <h3>Lock Mode</h3>
      <span className={enabled ? 'badge badge-green' : 'badge'}>{enabled ? 'Enabled' : 'Off'}</span>
    </header>
    <p className="muted">
      Lock mode keeps the session on top and records tab visibility changes. Attempts: {attempts}
    </p>
    {enabled && (
      <button type="button" onClick={onReengage}>
        Re-focus window
      </button>
    )}
  </div>
);

export default LockModeStatus;

