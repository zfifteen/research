/**
 * Gallery panel — built-in example families.
 * TECH_SPEC Section 4.5
 */
import React from 'react';
import { useStore } from '../../state/store';
import { galleryEntries } from './galleryData';

export function Gallery(): React.ReactElement {
  const setBase = useStore((s) => s.setBase);
  const setRootDigits = useStore((s) => s.setRootDigits);
  const setProjectName = useStore((s) => s.setProjectName);
  const setActiveTab = useStore((s) => s.setActiveTab);

  const handleLoad = (entry: typeof galleryEntries[0]) => {
    if (!entry) return;
    setBase(entry.base);
    setRootDigits(entry.rootDigits);
    setProjectName(entry.name);
    setActiveTab('explorer');
  };

  return (
    <div className="panel gallery-panel">
      <h2>Example Gallery</h2>
      <p className="panel-description">
        Pre-built examples demonstrating palindromic square behavior across bases and root families.
      </p>

      <div className="gallery-grid">
        {galleryEntries.map((entry) => (
          <div key={entry.id} className={`gallery-card ${entry.tags.includes('post-cliff') ? 'broken' : 'safe'}`}>
            <h3>{entry.name}</h3>
            <p className="gallery-desc">{entry.description}</p>
            <div className="gallery-meta">
              <span className="meta-item">Base {entry.base}</span>
              <span className="meta-item">Family: {entry.family}</span>
              <div className="gallery-tags">
                {entry.tags.map((tag) => (
                  <span key={tag} className={`tag ${tag}`}>{tag}</span>
                ))}
              </div>
            </div>
            <button
              className="btn btn-load"
              onClick={() => handleLoad(entry)}
            >
              Load Example
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
