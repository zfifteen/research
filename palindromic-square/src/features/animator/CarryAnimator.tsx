/**
 * Carry Animator — full step-through controls for carry normalization.
 * TECH_SPEC Section 4.3 and 9
 */
import React, { useCallback, useEffect, useRef } from 'react';
import { useStore } from '../../state/store';
import type { CarryTraceEntry } from '../../math/types';

export function CarryAnimator(): React.ReactElement {
  const computeResult = useStore((s) => s.computeResult);
  const isApproximate = useStore((s) => s.isApproximate);
  const base = useStore((s) => s.base);
  const animatorState = useStore((s) => s.animatorState);
  const animatorStep = useStore((s) => s.animatorStep);
  const animatorSpeed = useStore((s) => s.animatorSpeed);
  const setAnimatorState = useStore((s) => s.setAnimatorState);
  const setAnimatorStep = useStore((s) => s.setAnimatorStep);
  const setAnimatorSpeed = useStore((s) => s.setAnimatorSpeed);

  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const trace = computeResult?.carryTrace ?? null;
  const traceOmitted = computeResult?.carryTraceOmitted ?? false;
  const totalSteps = trace?.length ?? 0;

  // Auto-play logic
  useEffect(() => {
    if (animatorState === 'playing' && trace) {
      timerRef.current = setInterval(() => {
        setAnimatorStep(Math.min(animatorStep + 1, totalSteps - 1));
      }, 1000 / animatorSpeed);

      if (animatorStep >= totalSteps - 1) {
        setAnimatorState('stopped');
      }
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [animatorState, animatorStep, animatorSpeed, totalSteps, trace, setAnimatorStep, setAnimatorState]);

  const handlePlay = useCallback(() => {
    if (animatorStep >= totalSteps - 1) {
      setAnimatorStep(0);
    }
    setAnimatorState('playing');
  }, [animatorStep, totalSteps, setAnimatorStep, setAnimatorState]);

  const handlePause = useCallback(() => {
    setAnimatorState('paused');
  }, [setAnimatorState]);

  const handleStepForward = useCallback(() => {
    setAnimatorState('paused');
    setAnimatorStep(Math.min(animatorStep + 1, totalSteps - 1));
  }, [animatorStep, totalSteps, setAnimatorStep, setAnimatorState]);

  const handleStepBackward = useCallback(() => {
    setAnimatorState('paused');
    setAnimatorStep(Math.max(animatorStep - 1, 0));
  }, [animatorStep, setAnimatorStep, setAnimatorState]);

  const handleRestart = useCallback(() => {
    setAnimatorStep(0);
    setAnimatorState('stopped');
  }, [setAnimatorStep, setAnimatorState]);

  if (!computeResult) {
    return (
      <div className="panel animator-panel">
        <h2>Carry Animator</h2>
        <p className="empty-state">Compute a square to animate the carry propagation.</p>
      </div>
    );
  }

  if (traceOmitted || !trace) {
    return (
      <div className="panel animator-panel">
        <h2>Carry Animator</h2>
        {isApproximate && <span className="approx-badge">Approximate</span>}
        <p className="warning-state">
          {traceOmitted
            ? `Full carry trace unavailable for this input size. ${computeResult.carryTraceOmissionReason ?? ''}`
            : 'Carry trace not available in preview mode.'}
        </p>
      </div>
    );
  }

  const currentEntry: CarryTraceEntry | undefined = trace[animatorStep];
  const centralPosition = Math.floor((computeResult.rawCoefficients.length - 1) / 2);

  return (
    <div className="panel animator-panel">
      <h2>
        Carry Animator
        {isApproximate && <span className="approx-badge">Approximate</span>}
      </h2>
      <p className="panel-description">
        Step through carry normalization to see how overflow at the center propagates asymmetrically.
      </p>

      {/* Transport controls */}
      <div className="animator-controls">
        <button className="btn btn-control" onClick={handleRestart} title="Restart">
          ⏮
        </button>
        <button className="btn btn-control" onClick={handleStepBackward} title="Step back">
          ⏪
        </button>
        {animatorState === 'playing' ? (
          <button className="btn btn-control btn-primary" onClick={handlePause} title="Pause">
            ⏸
          </button>
        ) : (
          <button className="btn btn-control btn-primary" onClick={handlePlay} title="Play">
            ▶
          </button>
        )}
        <button className="btn btn-control" onClick={handleStepForward} title="Step forward">
          ⏩
        </button>
        <div className="speed-control">
          <label htmlFor="speed-slider">Speed: {animatorSpeed}x</label>
          <input
            id="speed-slider"
            type="range"
            min={0.25}
            max={4}
            step={0.25}
            value={animatorSpeed}
            onChange={(e) => setAnimatorSpeed(Number(e.target.value))}
            className="slider-input"
          />
        </div>
        <span className="step-counter">
          Step {animatorStep + 1} / {totalSteps}
        </span>
      </div>

      {/* Current step details */}
      {currentEntry && (
        <div className={`carry-step-detail ${currentEntry.position === centralPosition ? 'central-highlight' : ''}`}>
          <h3>
            Position {currentEntry.position}
            {currentEntry.position === centralPosition && ' (CENTER — overflow event)'}
          </h3>
          <div className="step-grid">
            <div className="step-item">
              <span className="label">Raw coefficient:</span>
              <span className="mono">{currentEntry.rawCoefficient.toString()}</span>
            </div>
            <div className="step-item">
              <span className="label">+ Incoming carry:</span>
              <span className="mono">{currentEntry.incomingCarry.toString()}</span>
            </div>
            <div className="step-item total">
              <span className="label">= Total:</span>
              <span className="mono">
                {(currentEntry.rawCoefficient + currentEntry.incomingCarry).toString()}
              </span>
            </div>
            <div className="step-item">
              <span className="label">Digit out (mod {base}):</span>
              <span className="mono">{currentEntry.digitOut}</span>
            </div>
            <div className="step-item">
              <span className="label">Outgoing carry:</span>
              <span className={`mono ${currentEntry.outgoingCarry > 0n ? 'carry-active' : ''}`}>
                {currentEntry.outgoingCarry.toString()}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Carry propagation visualization */}
      <div className="carry-viz">
        <h3>Carry Propagation Path</h3>
        <div className="carry-cells">
          {trace.slice(0, Math.min(trace.length, 50)).map((entry, i) => {
            const isActive = i <= animatorStep;
            const isCurrent = i === animatorStep;
            const isCentral = entry.position === centralPosition;
            const hasCarry = entry.outgoingCarry > 0n;

            return (
              <div
                key={i}
                className={`carry-cell ${isActive ? 'active' : ''} ${isCurrent ? 'current' : ''} ${isCentral ? 'central' : ''} ${hasCarry ? 'has-carry' : ''}`}
                title={`pos ${entry.position}: ${entry.digitOut} (carry: ${entry.outgoingCarry.toString()})`}
              >
                <span className="cell-digit">{entry.digitOut}</span>
                {hasCarry && isActive && (
                  <span className="cell-carry">↑{entry.outgoingCarry.toString()}</span>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
