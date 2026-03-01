/**
 * Main App component — orchestrates all features.
 */
import React, { useEffect, useCallback, useRef, useState } from 'react';
import { useStore } from '../state/store';
import { PhaseExplorer } from '../features/explorer/PhaseExplorer';
import { ConvolutionHeatmap } from '../features/explorer/ConvolutionHeatmap';
import { RootBuilder } from '../features/builder/RootBuilder';
import { CarryAnimator } from '../features/animator/CarryAnimator';
import { SearchGuidance } from '../features/search-guidance/SearchGuidance';
import { Gallery } from '../features/gallery/Gallery';
import { ExportPanel } from '../features/exports/ExportPanel';
import { DataManagement } from '../features/data-management/DataManagement';
import { DebugPanel } from '../features/data-management/DebugPanel';
import { StartupRecoveryModal, type RecoveryOutcome } from '../features/recovery/StartupRecoveryModal';
import { submitJob, cancelCurrentJob } from '../worker/api';
import { parseMSBtoLE, decodeURLState, serializeLEtoMSB } from '../utils/encoding';
import { detectProfile, runBenchmark, estimateComputeTimeMs } from '../utils/timing';
import { isRepunit } from '../math/square';
import { repository } from '../storage/repository';
import { getDefaultGalleryEntry } from '../features/gallery/galleryData';
import { v4 as uuid } from 'uuid';
import type { ActiveTab } from '../state/slices/uiSlice';

const TABS: { id: ActiveTab; label: string }[] = [
  { id: 'explorer', label: 'Explorer' },
  { id: 'builder', label: 'Builder' },
  { id: 'animator', label: 'Animator' },
  { id: 'guidance', label: 'Guidance' },
  { id: 'gallery', label: 'Gallery' },
  { id: 'exports', label: 'Export' },
  { id: 'data', label: 'Data' },
  { id: 'debug', label: 'Debug' },
];

/**
 * FPS monitor — measures real frame rate and triggers auto-abort
 * when sustained frame drops exceed the profile threshold.
 * Per TECH_SPEC Section 6.3: desktop <20 FPS for 2s, mobile <15 FPS for 2s.
 */
function useFpsMonitor(
  isRunning: boolean,
  fpsThreshold: number,
  durationMs: number,
  onAutoAbort: () => void
) {
  const frameTimesRef = useRef<number[]>([]);
  const rafRef = useRef<number | null>(null);
  const lowFpsSinceRef = useRef<number | null>(null);

  useEffect(() => {
    if (!isRunning) {
      // Reset when not computing
      frameTimesRef.current = [];
      lowFpsSinceRef.current = null;
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
      return;
    }

    const measure = (now: number) => {
      const times = frameTimesRef.current;
      times.push(now);

      // Keep only the last 1 second of frame times
      while (times.length > 1 && times[0]! < now - 1000) {
        times.shift();
      }

      // Need at least 2 frames to compute FPS
      if (times.length >= 2) {
        const fps = (times.length - 1) / ((now - times[0]!) / 1000);

        if (fps < fpsThreshold) {
          if (lowFpsSinceRef.current === null) {
            lowFpsSinceRef.current = now;
          } else if (now - lowFpsSinceRef.current >= durationMs) {
            // Sustained frame drops — auto abort
            onAutoAbort();
            lowFpsSinceRef.current = null;
            return; // Stop monitoring
          }
        } else {
          lowFpsSinceRef.current = null;
        }
      }

      rafRef.current = requestAnimationFrame(measure);
    };

    rafRef.current = requestAnimationFrame(measure);

    return () => {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
    };
  }, [isRunning, fpsThreshold, durationMs, onAutoAbort]);
}

export function App(): React.ReactElement {
  const base = useStore((s) => s.base);
  const rootDigits = useStore((s) => s.rootDigits);
  const projectName = useStore((s) => s.projectName);
  const activeTab = useStore((s) => s.activeTab);
  const setActiveTab = useStore((s) => s.setActiveTab);
  const jobStatus = useStore((s) => s.jobStatus);
  const computeResult = useStore((s) => s.computeResult);
  const isApproximate = useStore((s) => s.isApproximate);
  const _showDebugPanel = useStore((s) => s.showDebugPanel);
  const setComputeResult = useStore((s) => s.setComputeResult);
  const setJobStatus = useStore((s) => s.setJobStatus);
  const setJobId = useStore((s) => s.setJobId);
  const setError = useStore((s) => s.setError);
  const setProfile = useStore((s) => s.setProfile);
  const setBenchmarkResult = useStore((s) => s.setBenchmarkResult);
  const limits = useStore((s) => s.limits);
  const benchmarkCoeff = useStore((s) => s.benchmarkCoeff);
  const setBase = useStore((s) => s.setBase);
  const setRootDigits = useStore((s) => s.setRootDigits);
  const setProjectName = useStore((s) => s.setProjectName);
  const isDirty = useStore((s) => s.isDirty);
  const activeProjectId = useStore((s) => s.activeProjectId);
  const settings = useStore((s) => s.settings);
  const markClean = useStore((s) => s.markClean);
  const setActiveProject = useStore((s) => s.setActiveProject);
  const setProjects = useStore((s) => s.setProjects);
  const toasts = useStore((s) => s.toasts);
  const addToast = useStore((s) => s.addToast);
  const dismissToast = useStore((s) => s.dismissToast);

  // Startup recovery state
  const [recoveryError, setRecoveryError] = useState<unknown>(null);
  const [showRecovery, setShowRecovery] = useState(false);

  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  /** Stores the original createdAt for the active project. */
  const originalCreatedAtRef = useRef<string | null>(null);

  // Gap 2: FPS auto-abort
  const handleAutoAbort = useCallback(async () => {
    await cancelCurrentJob();
    setJobStatus('cancelled');
    addToast('Compute cancelled: frame rate dropped below threshold', 'warning');
  }, [setJobStatus, addToast]);

  useFpsMonitor(
    jobStatus === 'running',
    limits.autoAbortFpsTrigger,
    limits.autoAbortFpsDurationMs,
    handleAutoAbort
  );

  // Initialization: profile detection, benchmark, first-run, URL state
  useEffect(() => {
    const init = async () => {
      // Detect profile
      const profile = detectProfile();
      setProfile(profile);

      // Run benchmark
      const coeff = runBenchmark();
      setBenchmarkResult(coeff);

      // Check URL state
      const hash = window.location.hash;
      if (hash.startsWith('#state=')) {
        const encoded = hash.slice(7);
        const state = decodeURLState(encoded);
        if (state) {
          setBase(state.base);
          setRootDigits(state.rootDigits);
          window.location.hash = '';
          return;
        } else {
          // Gap 6: Show user-visible toast for invalid URL state
          addToast('Invalid or unsupported share link. Loading default project.', 'warning');
        }
      }

      // Check for first run
      try {
        const isFirst = await repository.isFirstRun();
        if (isFirst) {
          const sample = getDefaultGalleryEntry();
          setBase(sample.base);
          setRootDigits(sample.rootDigits);
          setProjectName(sample.name);
          await repository.markFirstRunComplete();
        } else {
          // Load most recent project
          const projects = await repository.getAllProjects();
          setProjects(projects);
          if (projects.length > 0 && projects[0]) {
            const latest = projects[0];
            setBase(latest.base);
            setRootDigits(latest.rootDigits);
            setProjectName(latest.name);
            setActiveProject(latest.id);
            // Gap 4: preserve original createdAt
            originalCreatedAtRef.current = latest.createdAt;
          }
        }
      } catch (e) {
        console.error('DB initialization error:', e);
        setRecoveryError(e);
        setShowRecovery(true);
      }
    };

    init();
  }, []);

  // Auto-save with debounce (500ms) per TECH_SPEC Section 4.6
  useEffect(() => {
    if (!isDirty) return;

    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(async () => {
      const now = new Date().toISOString();
      const isExistingProject = !!activeProjectId;
      const id = activeProjectId || uuid();

      // Gap 4: preserve createdAt for existing projects
      const createdAt = isExistingProject && originalCreatedAtRef.current
        ? originalCreatedAtRef.current
        : now;

      await repository.saveProject({
        id,
        name: projectName,
        createdAt,
        updatedAt: now,
        base,
        rootDigits,
        settings,
        cachedArtifacts: null
      });

      // For new projects, store the createdAt for future saves
      if (!isExistingProject) {
        originalCreatedAtRef.current = createdAt;
      }

      setActiveProject(id);
      markClean();
      const projects = await repository.getAllProjects();
      setProjects(projects);
    }, 500);

    return () => {
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    };
  }, [isDirty, activeProjectId, projectName, base, rootDigits, settings, setActiveProject, markClean, setProjects]);

  // Flush on page hide (best effort)
  useEffect(() => {
    const flush = () => {
      if (isDirty && saveTimerRef.current) {
        clearTimeout(saveTimerRef.current);
        const now = new Date().toISOString();
        const isExistingProject = !!activeProjectId;
        const id = activeProjectId || uuid();

        // Gap 4: preserve createdAt for existing projects
        const createdAt = isExistingProject && originalCreatedAtRef.current
          ? originalCreatedAtRef.current
          : now;

        repository.saveProject({
          id,
          name: projectName,
          createdAt,
          updatedAt: now,
          base,
          rootDigits,
          settings,
          cachedArtifacts: null
        }).catch(() => {});
      }
    };

    document.addEventListener('visibilitychange', flush);
    window.addEventListener('pagehide', flush);

    return () => {
      document.removeEventListener('visibilitychange', flush);
      window.removeEventListener('pagehide', flush);
    };
  }, [isDirty, activeProjectId, projectName, base, rootDigits, settings]);

  // Compute on input change
  const handleCompute = useCallback(async (mode: 'preview' | 'exact') => {
    try {
      const digitsLE = parseMSBtoLE(rootDigits, base);
      const estimatedTime = estimateComputeTimeMs(digitsLE.length, benchmarkCoeff);

      if (mode === 'exact' && digitsLE.length > limits.safeDigitsExact) {
        if (estimatedTime > limits.warningThresholdMs) {
          const proceed = confirm(
            `This computation may take ~${(estimatedTime / 1000).toFixed(1)}s. ` +
            `The safe limit for exact mode is ${limits.safeDigitsExact} digits. Continue?`
          );
          if (!proceed) return;
        }
      }

      setJobStatus('running');
      const jobId = uuid();
      setJobId(jobId);
      setError(null);

      const response = await submitJob(
        base,
        digitsLE,
        mode,
        limits.workerHardTimeoutMs
      );

      if ('cancelled' in response) {
        setJobStatus('cancelled');
        return;
      }

      setComputeResult(response.result);
      setJobStatus('completed');
    } catch (e) {
      setError(String(e));
      setJobStatus('error');
    }
  }, [base, rootDigits, benchmarkCoeff, limits, setJobStatus, setJobId, setError, setComputeResult]);

  const handleCancel = useCallback(async () => {
    await cancelCurrentJob();
    setJobStatus('cancelled');
  }, [setJobStatus]);

  // Auto-compute on input change
  // Gap 3: gate on BOTH safeDigitsExact AND estimateComputeTimeMs > inputToPreviewMs
  // Gap 2 (repunit): detect repunit roots and force exact mode for O(1) verdict
  useEffect(() => {
    const timer = setTimeout(() => {
      try {
        const digitsLE = parseMSBtoLE(rootDigits, base);
        const estimatedTime = estimateComputeTimeMs(digitsLE.length, benchmarkCoeff);

        // Repunit fast-path: always use exact mode since the worker
        // will detect the repunit and return an O(1) verdict.
        if (isRepunit(digitsLE)) {
          handleCompute('exact');
          return;
        }

        // Use preview if EITHER the digit count exceeds safe limit
        // OR the estimated time exceeds the input-to-preview budget
        if (digitsLE.length <= limits.safeDigitsExact && estimatedTime <= limits.inputToPreviewMs) {
          handleCompute('exact');
        } else {
          handleCompute('preview');
        }
      } catch {
        // Invalid digits, don't compute
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [base, rootDigits, benchmarkCoeff, limits, handleCompute]);

  // Recovery modal handlers
  const handleRecoveryRetry = useCallback(async () => {
    return repository.attemptRecovery();
  }, []);

  const handleRecoveryClear = useCallback(async () => {
    await repository.clearAll();
    await repository.markFirstRunComplete();
  }, []);

  const handleRecoveryDefaults = useCallback(() => {
    const sample = getDefaultGalleryEntry();
    setBase(sample.base);
    setRootDigits(sample.rootDigits);
    setProjectName(sample.name);
  }, [setBase, setRootDigits, setProjectName]);

  const handleRecoveryDismiss = useCallback((outcome: RecoveryOutcome) => {
    setShowRecovery(false);
    addToast(
      `Storage recovery: ${outcome.message}`,
      outcome.success ? 'info' : 'warning'
    );
    // If recovery or clear succeeded, reload projects
    if (outcome.success && outcome.action !== 'defaults') {
      repository.getAllProjects().then(setProjects).catch(() => {});
    }
  }, [addToast, setProjects]);

  const squareDisplay = computeResult
    ? serializeLEtoMSB(computeResult.normalizedDigitsLE, base)
    : '';

  const palindromeDisplay =
    computeResult?.isPalindrome === true
      ? 'Yes'
      : computeResult?.isPalindrome === false
      ? 'No'
      : computeResult?.isPalindrome === 'indeterminate'
      ? 'Unknown (exact computation required)'
      : '';

  return (
    <div className="app" data-reduced-motion={
      typeof window !== 'undefined' && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
    }>
      {/* Startup Recovery Modal */}
      {showRecovery && (
        <StartupRecoveryModal
          error={recoveryError}
          onRetry={handleRecoveryRetry}
          onClear={handleRecoveryClear}
          onContinueDefaults={handleRecoveryDefaults}
          onDismiss={handleRecoveryDismiss}
        />
      )}

      <header className="app-header">
        <h1>PeakGuard</h1>
        <p className="subtitle">Palindromic Square Phase Transition Explorer</p>
      </header>

      {/* Toast notifications */}
      {toasts.length > 0 && (
        <div className="toast-container" role="alert" aria-live="polite">
          {toasts.map((toast) => (
            <div key={toast.id} className={`toast toast-${toast.type}`}>
              <span>{toast.text}</span>
              <button className="toast-dismiss" onClick={() => dismissToast(toast.id)} aria-label="Dismiss">&times;</button>
            </div>
          ))}
        </div>
      )}

      {/* Result summary bar */}
      {computeResult && (
        <div className="result-summary">
          <span className="summary-item">
            <strong>Root:</strong> <code className="mono">{rootDigits}<sub>{base}</sub></code>
          </span>
          <span className="summary-item">
            <strong>Square:</strong> <code className="mono">{squareDisplay.length > 40 ? squareDisplay.slice(0, 37) + '...' : squareDisplay}<sub>{base}</sub></code>
          </span>
          <span className="summary-item">
            <strong>Peak:</strong> {computeResult.peak.toString()}
          </span>
          <span className={`summary-item verdict-display ${computeResult.isPalindrome === true ? 'pal-yes' : computeResult.isPalindrome === false ? 'pal-no' : 'pal-unknown'}`}>
            <strong>Palindrome:</strong> {palindromeDisplay}
          </span>
          {isApproximate && <span className="approx-badge">Approximate</span>}
          <span className="timing">
            {computeResult.timing.totalMs.toFixed(1)} ms
          </span>
        </div>
      )}

      {/* Compute controls */}
      <div className="compute-bar">
        <button
          className="btn btn-primary"
          onClick={() => handleCompute('exact')}
          disabled={jobStatus === 'running'}
        >
          Compute Exact
        </button>
        <button
          className="btn"
          onClick={() => handleCompute('preview')}
          disabled={jobStatus === 'running'}
        >
          Preview
        </button>
        {jobStatus === 'running' && (
          <button className="btn btn-danger" onClick={handleCancel}>
            Cancel
          </button>
        )}
        {jobStatus === 'running' && <span className="spinner" />}
      </div>

      {/* Tab navigation */}
      <nav className="tab-nav" role="tablist">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            role="tab"
            aria-selected={activeTab === tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      {/* Tab content */}
      <main className="tab-content">
        {activeTab === 'explorer' && (
          <div className="explorer-view">
            <PhaseExplorer />
            <ConvolutionHeatmap />
          </div>
        )}
        {activeTab === 'builder' && <RootBuilder />}
        {activeTab === 'animator' && <CarryAnimator />}
        {activeTab === 'guidance' && <SearchGuidance />}
        {activeTab === 'gallery' && <Gallery />}
        {activeTab === 'exports' && <ExportPanel />}
        {activeTab === 'data' && <DataManagement />}
        {activeTab === 'debug' && <DebugPanel />}
      </main>

      <footer className="app-footer">
        <p>PeakGuard v1 · Local-only · No telemetry · <a href="#" onClick={(e) => { e.preventDefault(); setActiveTab('debug'); }}>Debug</a></p>
      </footer>
    </div>
  );
}
