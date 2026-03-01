/**
 * Main App component — orchestrates all features.
 */
import React, { useEffect, useCallback, useRef } from 'react';
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
import { submitJob, cancelCurrentJob } from '../worker/api';
import { parseMSBtoLE, decodeURLState, serializeLEtoMSB } from '../utils/encoding';
import { detectProfile, runBenchmark, estimateComputeTimeMs } from '../utils/timing';
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

  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

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
          console.warn('Invalid URL state, falling back to default');
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
          }
        }
      } catch (e) {
        console.error('DB initialization error, attempting recovery:', e);
        const recovery = await repository.attemptRecovery();
        console.log('Recovery result:', recovery.message);
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
      const id = activeProjectId || uuid();
      await repository.saveProject({
        id,
        name: projectName,
        createdAt: now,
        updatedAt: now,
        base,
        rootDigits,
        settings,
        cachedArtifacts: null
      });
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
        // Best-effort synchronous-ish save attempt
        const now = new Date().toISOString();
        const id = activeProjectId || uuid();
        repository.saveProject({
          id,
          name: projectName,
          createdAt: now,
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

      // Determine if we should use preview
      const actualMode = mode;
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
        actualMode,
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

  // Auto-compute on input change (preview for safety)
  useEffect(() => {
    const timer = setTimeout(() => {
      try {
        const digitsLE = parseMSBtoLE(rootDigits, base);
        if (digitsLE.length <= limits.safeDigitsExact) {
          handleCompute('exact');
        } else {
          handleCompute('preview');
        }
      } catch {
        // Invalid digits, don't compute
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [base, rootDigits]);

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
      <header className="app-header">
        <h1>PeakGuard</h1>
        <p className="subtitle">Palindromic Square Phase Transition Explorer</p>
      </header>

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
