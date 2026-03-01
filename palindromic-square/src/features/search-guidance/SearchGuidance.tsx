/**
 * Search Guidance Panel — classifies candidate root families by peak-growth behavior.
 * TECH_SPEC Section 4.8
 */
import React from 'react';
import { useStore } from '../../state/store';
import { getCliffEdge } from '../../math/repunit';

interface GuidanceFamily {
  name: string;
  pattern: string;
  peakGrowth: string;
  viability: 'viable' | 'finite-ceiling' | 'immediate-break';
  description: string;
}

const FAMILIES: GuidanceFamily[] = [
  {
    name: 'Repunits (111...1)',
    pattern: 'All digits are 1',
    peakGrowth: 'Linear (peak = n)',
    viability: 'finite-ceiling',
    description: 'Peak grows linearly with length. Palindromic structure has a finite ceiling determined by the base.'
  },
  {
    name: 'Sparse (10...01)',
    pattern: 'Two 1s separated by zeros',
    peakGrowth: 'Bounded (peak ≤ 2)',
    viability: 'viable',
    description: 'Peak stays bounded regardless of length. This is the viable region for longer-lived symmetry.'
  },
  {
    name: 'Triple Sparse (10...010...01)',
    pattern: 'Three 1s with zero gaps',
    peakGrowth: 'Bounded (peak ≤ 3)',
    viability: 'viable',
    description: 'Peak remains bounded. Wider gaps between digits keep peak low, preserving palindrome potential.'
  },
  {
    name: 'Dense non-uniform',
    pattern: 'Mixed digits, many non-zero',
    peakGrowth: 'Potentially superlinear',
    viability: 'immediate-break',
    description: 'Dense digit patterns can produce fast-growing peaks that exceed symbol capacity quickly.'
  },
  {
    name: '10^k + 1 style',
    pattern: '10...01 with specific gap sizes',
    peakGrowth: 'Sublinear/bounded',
    viability: 'viable',
    description: 'Carefully constructed sparse patterns maintain bounded peaks. The viable region for longer-lived symmetry.'
  }
];

export function SearchGuidance(): React.ReactElement {
  const base = useStore((s) => s.base);
  const cliffEdge = getCliffEdge(base);

  return (
    <div className="panel guidance-panel">
      <h2>Search Guidance</h2>
      <p className="panel-description">
        Not all root families are worth exploring. Peak growth rate under self-multiplication
        determines whether palindromic structure can survive.
      </p>

      <div className="guidance-rule">
        <h3>Core Principle</h3>
        <ul>
          <li>
            <strong>Linear or faster peak growth</strong> implies a <em>finite symmetry ceiling</em> —
            the palindrome will eventually break as length increases.
          </li>
          <li>
            <strong>Sublinear or bounded growth</strong> is the <em>viable region</em> for
            longer-lived symmetry.
          </li>
        </ul>
      </div>

      <div className="repunit-threshold">
        <h3>Repunit Threshold Rule</h3>
        {base >= 3 ? (
          <p>
            For base {base}: the last palindromic repunit length is <strong>n = {cliffEdge}</strong> (= b − 1).
            Beyond this, central accumulation exceeds symbol capacity.
          </p>
        ) : (
          <p>
            For base 2 (special case): the last palindromic repunit length is <strong>n = 2</strong>.
            Beyond n = 2, the palindrome breaks.
          </p>
        )}
      </div>

      <div className="family-cards">
        <h3>Candidate Root Families</h3>
        {FAMILIES.map((family) => (
          <div key={family.name} className={`family-card ${family.viability}`}>
            <div className="family-header">
              <h4>{family.name}</h4>
              <span className={`viability-badge ${family.viability}`}>
                {family.viability === 'viable'
                  ? '✓ Viable'
                  : family.viability === 'finite-ceiling'
                  ? '⚠ Finite ceiling'
                  : '✗ Quick break'}
              </span>
            </div>
            <div className="family-details">
              <div className="detail-row">
                <span className="label">Pattern:</span>
                <code>{family.pattern}</code>
              </div>
              <div className="detail-row">
                <span className="label">Peak growth:</span>
                <span>{family.peakGrowth}</span>
              </div>
              <p className="family-description">{family.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
