/**
 * Debug panel — performance profile, limits, job timing, memory, override state.
 * TECH_SPEC Section 9
 */
import React from 'react';
import { useStore } from '../../state/store';

export function DebugPanel(): React.ReactElement {
  const profile = useStore((s) => s.profile);
  const limits = useStore((s) => s.limits);
  const benchmarkCoeff = useStore((s) => s.benchmarkCoeff);
  const benchmarkComplete = useStore((s) => s.benchmarkComplete);
  const jobStatus = useStore((s) => s.jobStatus);
  const jobId = useStore((s) => s.jobId);
  const computeResult = useStore((s) => s.computeResult);
  const overrideState = useStore((s) => s.overrideState);

  const memoryEstimate = (performance as unknown as { memory?: { usedJSHeapSize?: number } })
    ?.memory?.usedJSHeapSize;

  return (
    <div className="panel debug-panel">
      <h2>Debug Panel</h2>

      <table className="debug-table">
        <tbody>
          <tr>
            <td>Profile</td>
            <td>{profile}</td>
          </tr>
          <tr>
            <td>Safe digits (exact)</td>
            <td>
              {limits.safeDigitsExact}
              {overrideState.isOverridden && (
                <span className="override-badge"> (overridden)</span>
              )}
            </td>
          </tr>
          <tr>
            <td>Override active</td>
            <td>{overrideState.isOverridden ? 'Yes' : 'No'}</td>
          </tr>
          {overrideState.isOverridden && overrideState.overriddenSafeDigits !== null && (
            <tr>
              <td>Override value</td>
              <td>{overrideState.overriddenSafeDigits} digits</td>
            </tr>
          )}
          {overrideState.isOverridden && overrideState.overriddenAt && (
            <tr>
              <td>Override set at</td>
              <td>{new Date(overrideState.overriddenAt).toLocaleTimeString()}</td>
            </tr>
          )}
          <tr>
            <td>Input-to-preview budget</td>
            <td>{limits.inputToPreviewMs} ms</td>
          </tr>
          <tr>
            <td>Exact compute soft budget</td>
            <td>{limits.exactComputeSoftBudgetMs} ms</td>
          </tr>
          <tr>
            <td>Warning threshold</td>
            <td>{limits.warningThresholdMs} ms</td>
          </tr>
          <tr>
            <td>Worker hard timeout</td>
            <td>{limits.workerHardTimeoutMs} ms</td>
          </tr>
          <tr>
            <td>Auto-abort FPS trigger</td>
            <td>&lt; {limits.autoAbortFpsTrigger} FPS for {limits.autoAbortFpsDurationMs} ms</td>
          </tr>
          <tr>
            <td>Benchmark coefficient</td>
            <td>{benchmarkComplete ? benchmarkCoeff.toFixed(6) : 'Not run'}</td>
          </tr>
          <tr>
            <td>Job status</td>
            <td>{jobStatus}</td>
          </tr>
          <tr>
            <td>Job ID</td>
            <td className="mono">{jobId ?? 'none'}</td>
          </tr>
          <tr>
            <td>Queue depth</td>
            <td>{jobStatus === 'running' ? 1 : 0}</td>
          </tr>
          <tr>
            <td>Last compute time</td>
            <td>{computeResult ? `${computeResult.timing.totalMs.toFixed(1)} ms` : 'N/A'}</td>
          </tr>
          <tr>
            <td>Memory estimate</td>
            <td>
              {memoryEstimate
                ? `${(memoryEstimate / 1024 / 1024).toFixed(1)} MB`
                : 'Not available'}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
