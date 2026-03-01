/**
 * Root Builder — default sparse tools + advanced digit mode.
 * TECH_SPEC Section 4.1 and 9
 */
import React, { useCallback } from 'react';
import { useStore } from '../../state/store';
import { parseMSBtoLE } from '../../utils/encoding';

const PRESETS = [
  { label: 'Repunit (all 1s)', generate: (base: number, len: number) => '1'.repeat(len) },
  { label: '10...01 (sparse)', generate: (_base: number, len: number) => '1' + '0'.repeat(Math.max(0, len - 2)) + '1' },
  { label: '10...010...01', generate: (_base: number, len: number) => {
    const third = Math.max(1, Math.floor(len / 3));
    return '1' + '0'.repeat(third - 1) + '1' + '0'.repeat(third - 1) + '1';
  }},
];

export function RootBuilder(): React.ReactElement {
  const base = useStore((s) => s.base);
  const rootDigits = useStore((s) => s.rootDigits);
  const setBase = useStore((s) => s.setBase);
  const setRootDigits = useStore((s) => s.setRootDigits);
  const showAdvanced = useStore((s) => s.showAdvancedBuilder);
  const toggleAdvanced = useStore((s) => s.toggleAdvancedBuilder);

  const [sparseLength, setSparseLength] = React.useState(rootDigits.length);

  const handleBaseChange = useCallback((newBase: number) => {
    setBase(newBase);
    // Reset to repunit for the new base
    const cliff = newBase === 2 ? 2 : newBase - 1;
    setRootDigits('1'.repeat(cliff));
    setSparseLength(cliff);
  }, [setBase, setRootDigits]);

  const handlePreset = useCallback((preset: typeof PRESETS[0]) => {
    if (!preset) return;
    const digits = preset.generate(base, sparseLength);
    setRootDigits(digits);
  }, [base, sparseLength, setRootDigits]);

  const handleDigitEdit = useCallback((value: string) => {
    // Validate characters against base
    const upper = value.toUpperCase();
    try {
      if (upper.length > 0) {
        parseMSBtoLE(upper, base); // validate
      }
      setRootDigits(upper || '0');
    } catch {
      // Invalid digit for base, ignore
    }
  }, [base, setRootDigits]);

  const digitCount = rootDigits.length;
  const maxSymbol = base <= 10 ? String(base - 1) : `${base - 1} (${String.fromCharCode(55 + base)})`;

  return (
    <div className="panel builder-panel">
      <h2>Root Builder</h2>
      <p className="panel-description">
        Build a root number to square. Use sparse patterns (0/1 digits) or switch to advanced mode for arbitrary digits.
      </p>

      <div className="control-row">
        <label htmlFor="builder-base">Base:</label>
        <select
          id="builder-base"
          value={base}
          onChange={(e) => handleBaseChange(Number(e.target.value))}
          className="select-input"
        >
          {Array.from({ length: 35 }, (_, i) => i + 2).map((b) => (
            <option key={b} value={b}>{b}</option>
          ))}
        </select>
      </div>

      {!showAdvanced && (
        <>
          <div className="control-row">
            <label htmlFor="sparse-length">Digit count: {sparseLength}</label>
            <input
              id="sparse-length"
              type="range"
              min={1}
              max={100}
              value={sparseLength}
              onChange={(e) => {
                const len = Number(e.target.value);
                setSparseLength(len);
              }}
              className="slider-input"
            />
          </div>

          <div className="preset-buttons">
            {PRESETS.map((p, i) => (
              <button
                key={i}
                className="btn btn-preset"
                onClick={() => handlePreset(p)}
              >
                {p.label}
              </button>
            ))}
          </div>
        </>
      )}

      <button className="btn btn-toggle" onClick={toggleAdvanced}>
        {showAdvanced ? 'Switch to Sparse Builder' : 'Switch to Advanced Mode'}
      </button>

      {showAdvanced && (
        <div className="advanced-input">
          <label htmlFor="digit-input">
            Digits (MSB first, symbols 0-{maxSymbol}):
          </label>
          <input
            id="digit-input"
            type="text"
            value={rootDigits}
            onChange={(e) => handleDigitEdit(e.target.value)}
            className="text-input mono"
            spellCheck={false}
          />
        </div>
      )}

      <div className="builder-summary">
        <div className="info-row">
          <span>Root (base {base}):</span>
          <code className="mono">{rootDigits}</code>
        </div>
        <div className="info-row">
          <span>Digit count:</span>
          <span>{digitCount}</span>
        </div>
      </div>
    </div>
  );
}
