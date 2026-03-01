/**
 * Startup Recovery Modal — shown when IndexedDB is corrupted/unreadable.
 * Gives the user explicit choices per TECH_SPEC §4.6:
 *   1. Retry recovery (attempt again)
 *   2. Clear local data (delete DB and start fresh)
 *   3. Continue with defaults (ignore error, use default state)
 *
 * Displays the outcome of whichever action the user picks.
 */
import React, { useState } from 'react';

export type RecoveryChoice = 'retry' | 'clear' | 'defaults';
export type RecoveryOutcome = {
  action: RecoveryChoice;
  success: boolean;
  message: string;
};

interface Props {
  error: unknown;
  onRetry: () => Promise<{ recovered: boolean; message: string }>;
  onClear: () => Promise<void>;
  onContinueDefaults: () => void;
  onDismiss: (outcome: RecoveryOutcome) => void;
}

export function StartupRecoveryModal({
  error,
  onRetry,
  onClear,
  onContinueDefaults,
  onDismiss
}: Props): React.ReactElement {
  const [busy, setBusy] = useState(false);
  const [outcome, setOutcome] = useState<RecoveryOutcome | null>(null);

  const handleRetry = async () => {
    setBusy(true);
    try {
      const result = await onRetry();
      const o: RecoveryOutcome = {
        action: 'retry',
        success: result.recovered,
        message: result.message
      };
      setOutcome(o);
      if (result.recovered) {
        setTimeout(() => onDismiss(o), 1500);
      }
    } catch (e) {
      setOutcome({
        action: 'retry',
        success: false,
        message: `Retry failed: ${String(e)}`
      });
    } finally {
      setBusy(false);
    }
  };

  const handleClear = async () => {
    setBusy(true);
    try {
      await onClear();
      const o: RecoveryOutcome = {
        action: 'clear',
        success: true,
        message: 'Local data cleared. Starting fresh.'
      };
      setOutcome(o);
      setTimeout(() => onDismiss(o), 1500);
    } catch (e) {
      setOutcome({
        action: 'clear',
        success: false,
        message: `Clear failed: ${String(e)}`
      });
    } finally {
      setBusy(false);
    }
  };

  const handleDefaults = () => {
    onContinueDefaults();
    const o: RecoveryOutcome = {
      action: 'defaults',
      success: true,
      message: 'Continuing with default project settings.'
    };
    setOutcome(o);
    setTimeout(() => onDismiss(o), 1000);
  };

  return (
    <div className="recovery-modal-overlay" role="dialog" aria-modal="true" aria-label="Startup recovery">
      <div className="recovery-modal">
        <h2>Storage Recovery Required</h2>
        <p className="recovery-error">
          PeakGuard encountered an error reading your saved data:
        </p>
        <code className="recovery-error-detail">
          {String(error)}
        </code>

        {outcome && (
          <div className={`recovery-outcome ${outcome.success ? 'recovery-success' : 'recovery-failure'}`}>
            {outcome.message}
          </div>
        )}

        {!outcome?.success && (
          <div className="recovery-actions">
            <button
              className="btn btn-primary"
              onClick={handleRetry}
              disabled={busy}
            >
              {busy ? 'Working\u2026' : 'Retry Recovery'}
            </button>
            <button
              className="btn btn-danger"
              onClick={handleClear}
              disabled={busy}
            >
              Clear Local Data
            </button>
            <button
              className="btn"
              onClick={handleDefaults}
              disabled={busy}
            >
              Continue with Defaults
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
