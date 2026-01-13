import Plot from 'react-plotly.js';
import type { Layout, PlotData } from 'plotly.js';

import type { TimelinePoint } from '../types';
import { getLabelColor } from '../utils/labels';

type Props = {
  data: TimelinePoint[];
};

const TimelineChart = ({ data }: Props) => {
  if (!data.length) {
    return (
      <div className="card">
        <header className="card-header">
          <h3>Engagement Timeline</h3>
        </header>
        <p className="muted">No events yet. Student telemetry will appear here.</p>
      </div>
    );
  }

  const topLabels = data.map((point) => point.labels?.[0]?.name ?? 'unknown');
  
  // Map labels to attention scores for wavy line
  const getAttentionScore = (label: string): number => {
    const scores: Record<string, number> = {
      'focused': 100,
      'engaged': 90,
      'partial_engaged': 60,
      'looking_left': 50,
      'looking_right': 50,
      'looking_up': 45,
      'looking_down': 45,
      'sleepy': 20,
      'distracted_by_multi_face': 15,
      'no_face': 0,
      'unknown': 40,
    };
    return scores[label] ?? 40;
  };

  // Group data by student for separate lines
  const studentData = new Map<string, typeof data>();
  data.forEach((point) => {
    const studentName = point.student_name;
    if (!studentData.has(studentName)) {
      studentData.set(studentName, []);
    }
    studentData.get(studentName)!.push(point);
  });

  // Create a trace for each student
  const traces: Partial<PlotData>[] = Array.from(studentData.entries()).map(([studentName, points]) => {
    const labels = points.map((point) => point.labels?.[0]?.name ?? 'unknown');
    const scores = labels.map(getAttentionScore);
    
    return {
      x: points.map((point) => point.timestamp),
      y: scores,
      mode: 'lines+markers' as const,
      type: 'scatter' as const,
      name: studentName,
      line: {
        shape: 'spline' as const,
        smoothing: 1.3,
        width: 3,
      },
      marker: {
        color: labels.map((label) => getLabelColor(label)),
        size: points.map((point) => (point.tab_switch ? 12 : 8)),
        symbol: points.map((point) => (point.multiple_faces ? 'diamond' : 'circle')),
        line: {
          color: 'white',
          width: 1,
        },
      },
      text: points.map((point, index) => {
        const labelText = labels[index];
        return `${studentName}<br>${labelText}<br>Score: ${scores[index]}%${point.tab_switch ? '<br>(tab switch)' : ''}`;
      }),
      hovertemplate: '%{text}<extra></extra>',
    };
  });

  return (
    <div className="card">
      <header className="card-header">
        <h3>Engagement Timeline</h3>
        <span className="muted">Wavy line shows attention level over time</span>
      </header>
      <Plot
        data={traces}
        layout={
          {
            autosize: true,
            margin: { t: 20, b: 60, l: 60, r: 20 },
            yaxis: { 
              title: { text: 'Attention Level (%)' },
              range: [0, 105],
              gridcolor: 'rgba(128, 128, 128, 0.2)',
              tickvals: [0, 20, 40, 60, 80, 100],
              ticktext: ['No Face', 'Low', 'Partial', 'Engaged', 'High', 'Focused'],
            },
            xaxis: { 
              title: { text: 'Time' },
              gridcolor: 'rgba(128, 128, 128, 0.2)',
            },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'rgba(0, 0, 0, 0.05)',
            showlegend: true,
            legend: {
              x: 1,
              xanchor: 'right',
              y: 1,
            },
            hovermode: 'closest',
            shapes: [
              // Add reference zones
              {
                type: 'rect',
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: 80,
                y1: 105,
                fillcolor: 'rgba(0, 255, 0, 0.1)',
                line: { width: 0 },
                layer: 'below',
              },
              {
                type: 'rect',
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: 40,
                y1: 80,
                fillcolor: 'rgba(255, 255, 0, 0.1)',
                line: { width: 0 },
                layer: 'below',
              },
              {
                type: 'rect',
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: 0,
                y1: 40,
                fillcolor: 'rgba(255, 0, 0, 0.1)',
                line: { width: 0 },
                layer: 'below',
              },
            ],
          } satisfies Partial<Layout>
        }
        style={{ width: '100%', height: '400px' }}
        config={{ displayModeBar: false, responsive: true }}
      />
    </div>
  );
};

export default TimelineChart;

