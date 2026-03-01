/**
 * Phase Transition Explorer — shows cliff behavior for repunits.
 * TECH_SPEC Section 4.2
 */
import React, { useMemo } from 'react';
import { useStore } from '../../state/store';
import { repunitVerdict, getCliffEdge } from '../../math/repunit';
import { computeExactSquare } from '../../math/square';
import { serializeLEtoMSB } from '../../utils/encoding';

export function PhaseExplorer(): React.ReactElement {
  const base = useStore((s) => s.base);
  const setBase = useStore((s) => s.setBase);

  const [repunitLength, setRepunitLength] = React.useState(() => {
    const cliff = getCliffEdge(base);
    return cliff;
  });

  React.useEffect(() => {
    const cliff = getCliffEdge(base);
    setRepunitLength(cliff);
  }, [base]);

  const cliffEdge = getCliffEdge(base);
  const maxLen = Math.min(cliffEdge + 3, 36);

  const verdict = useMemo(() => repunitVerdict(base, repunitLength), [base, repunitLength]);

  const squareResult = useMemo(() => {
    if (repunitLength > 50) return null; // too large for inline compute
    const digits = Array.from({ length: repunitLength }, () => 1);
    return computeExactSquare(digits, base);
  }, [base, repunitLength]);

  const rootStr = '1'.repeat(repunitLength);
  const squareStr = squareResult
    ? serializeLEtoMSB(squareResult.normalizedDigitsLE, base)
    : '(too large to display)';

  return (
    <div className="panel explorer-panel">
      <h2>Phase Transition Explorer</h2>
      <p className="panel-description">
        See when repunit-square palindromes fail. The transition is sharp, not gradual.
      </p>

      <div className="control-row">
        <label htmlFor="base-select">Base (b):</label>
        <select
          id="base-select"
          value={base}
          onChange={(e) => setBase(Number(e.target.value))}
          className="select-input"
        >
          {Array.from({ length: 35 }, (_, i) => i + 2).map((b) => (
            <option key={b} value={b}>
              {b}
            </option>
          ))}
        </select>
      </div>

      <div className="control-row">
        <label htmlFor="repunit-slider">Repunit length (n = {repunitLength}):</label>
        <input
          id="repunit-slider"
          type="range"
          min={1}
          max={maxLen}
          value={repunitLength}
          onChange={(e) => setRepunitLength(Number(e.target.value))}
          className="slider-input"
        />
      </div>

      <div className="cliff-info">
        <div className="info-badge">
          Cliff edge: n = {cliffEdge}
          {base === 2 ? ' (base-2 special case)' : ` (b−1 = ${base - 1})`}
        </div>
      </div>

      <div className="result-card">
        <div className="result-row">
          <span className="label">Root:</span>
          <code className="mono">{rootStr}<sub>{base}</sub></code>
        </div>
        <div className="result-row">
          <span className="label">Square:</span>
          <code className="mono">{squareStr}<sub>{base}</sub></code>
        </div>
        <div className="result-row">
          <span className="label">Peak:</span>
          <span className={`peak-value ${verdict.peak >= base ? 'overflow' : 'safe'}`}>
            {verdict.peak} {verdict.peak >= base ? `≥ ${base} (overflow)` : `< ${base} (safe)`}
          </span>
        </div>
        <div className="result-row">
          <span className="label">Classification:</span>
          <span className={`classification ${verdict.classification}`}>
            {verdict.classification === 'pre-cliff' ? '✓ Pre-cliff (palindrome)' : '✗ Post-cliff (broken)'}
          </span>
        </div>
        <div className="result-row">
          <span className="label">Palindrome:</span>
          <span className={`verdict ${verdict.isPalindrome ? 'yes' : 'no'}`}>
            {verdict.isPalindrome ? 'Yes' : 'No'}
          </span>
        </div>
      </div>

      {/* Convolution triangle visualization */}
      {squareResult && (
        <div className="convolution-preview">
          <h3>Convolution Coefficients (pre-carry)</h3>
          <div className="coeff-bar-chart">
            {squareResult.rawCoefficients.map((c, i) => {
              const maxVal = Number(squareResult.peak);
              const height = maxVal > 0 ? (Number(c) / maxVal) * 100 : 0;
              const isCentral = i === Math.floor(squareResult.rawCoefficients.length / 2);
              return (
                <div
                  key={i}
                  className={`coeff-bar ${isCentral ? 'central' : ''} ${Number(c) >= base ? 'overflow' : ''}`}
                  style={{ height: `${Math.max(height, 2)}%` }}
                  title={`c[${i}] = ${c.toString()}`}
                >
                  <span className="bar-label">{c.toString()}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="threshold-rule">
        <h3>Threshold Rule</h3>
        {base >= 3 ? (
          <p>
            For base {base}: last palindromic repunit length is <strong>n = {base - 1}</strong>.
            At n = {base}, central accumulation ({base}) exceeds symbol capacity ({base - 1}) and
            carries propagate asymmetrically, breaking the mirror.
          </p>
        ) : (
          <p>
            For base 2 (special case): last palindromic repunit length is <strong>n = 2</strong>.
            At n = 3, the palindrome breaks. This transition does not follow the simple peak ≥ base cutoff.
          </p>
        )}
      </div>
    </div>
  );
}
