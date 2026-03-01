/**
 * Convolution Heatmap View — SVG visualization of raw coefficients.
 * TECH_SPEC Section 9
 */
import React from 'react';
import { useStore } from '../../state/store';

export function ConvolutionHeatmap(): React.ReactElement {
  const computeResult = useStore((s) => s.computeResult);
  const base = useStore((s) => s.base);
  const isApproximate = useStore((s) => s.isApproximate);

  if (!computeResult) {
    return (
      <div className="panel heatmap-panel">
        <h2>Convolution View</h2>
        <p className="empty-state">Compute a square to see the convolution coefficients.</p>
      </div>
    );
  }

  const { rawCoefficients, peak } = computeResult;
  const peakNum = Number(peak);
  const centerIdx = Math.floor(rawCoefficients.length / 2);

  return (
    <div className="panel heatmap-panel">
      <h2>
        Convolution View
        {isApproximate && <span className="approx-badge">Approximate</span>}
      </h2>
      <p className="panel-description">
        Raw self-convolution coefficients before carry normalization. The peak value determines
        whether carries will break palindrome symmetry.
      </p>

      <div className="peak-summary">
        <span className="label">Peak coefficient:</span>
        <span className={`value ${peakNum >= base ? 'overflow' : 'safe'}`}>
          {peak.toString()}
          {peakNum >= base
            ? ` ≥ ${base} (forces carry)`
            : ` < ${base} (single symbol)`
          }
        </span>
      </div>

      <div className="heatmap-container">
        <svg
          viewBox={`0 0 ${rawCoefficients.length * 24 + 20} 200`}
          className="heatmap-svg"
          role="img"
          aria-label="Convolution coefficient bar chart"
        >
          {rawCoefficients.map((c, i) => {
            const val = Number(c);
            const height = peakNum > 0 ? (val / peakNum) * 150 : 0;
            const x = i * 24 + 10;
            const isCentral = i === centerIdx;
            const isOverflow = val >= base;

            return (
              <g key={i}>
                <rect
                  x={x}
                  y={190 - height}
                  width={20}
                  height={Math.max(height, 2)}
                  className={`heatmap-bar ${isCentral ? 'central' : ''} ${isOverflow ? 'overflow' : 'safe'}`}
                  rx={2}
                />
                <text
                  x={x + 10}
                  y={185 - height}
                  textAnchor="middle"
                  className="bar-text"
                  fontSize={10}
                >
                  {val}
                </text>
                <text
                  x={x + 10}
                  y={198}
                  textAnchor="middle"
                  className="position-text"
                  fontSize={8}
                >
                  {i}
                </text>
              </g>
            );
          })}
          {/* Base threshold line */}
          {peakNum > 0 && (
            <line
              x1={0}
              y1={190 - ((base - 1) / peakNum) * 150}
              x2={rawCoefficients.length * 24 + 20}
              y2={190 - ((base - 1) / peakNum) * 150}
              className="threshold-line"
              strokeDasharray="4 4"
            />
          )}
        </svg>
      </div>

      <div className="coeff-table">
        <h3>Coefficient Table</h3>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Position</th>
                <th>Coefficient</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {rawCoefficients.map((c, i) => {
                const val = Number(c);
                const isCentral = i === centerIdx;
                return (
                  <tr key={i} className={isCentral ? 'central-row' : ''}>
                    <td>{i}{isCentral ? ' (center)' : ''}</td>
                    <td className="mono">{c.toString()}</td>
                    <td className={val >= base ? 'overflow' : 'safe'}>
                      {val >= base ? 'Overflow' : 'OK'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
