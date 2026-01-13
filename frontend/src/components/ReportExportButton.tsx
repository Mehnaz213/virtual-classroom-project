import { useState } from 'react';

import api from '../services/api';

type Props = {
  sessionId: number;
};

const ReportExportButton = ({ sessionId }: Props) => {
  const [loading, setLoading] = useState(false);

  const download = async (format: 'csv' | 'pdf') => {
    setLoading(true);
    try {
      const response = await api.get(`/reports/${sessionId}`, {
        params: { format },
        responseType: 'blob',
      });
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `session-${sessionId}.${format}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="report-buttons">
      <button type="button" disabled={loading} onClick={() => download('csv')}>
        {loading ? 'Preparing…' : 'Download CSV'}
      </button>
      <button type="button" disabled={loading} onClick={() => download('pdf')}>
        {loading ? 'Preparing…' : 'Download PDF'}
      </button>
    </div>
  );
};

export default ReportExportButton;

