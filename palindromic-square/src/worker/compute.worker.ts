/**
 * Compute Web Worker — runs math operations off the main thread.
 * Exposed via Comlink RPC interface per TECH_SPEC Section 8.2.
 * Uses cooperative cancellation: the hot convolution loop periodically
 * checks a `cancelled` flag rather than relying on async interrupts.
 */
import type { ComputeResult, ComputeJobRequest } from '../math/types';
import { computeExactSquare, computePreviewSquare, isRepunit } from '../math/square';

let currentJobId: string | null = null;
let cancelled = false;

/** Cooperative cancellation callback passed into hot loops. */
function isCancelled(): boolean {
  return cancelled;
}

const workerApi = {
  /**
   * Run a compute job (exact or preview).
   * The convolution hot loop checks isCancelled() periodically,
   * enabling preemption even in synchronous O(n²) work.
   */
  compute(request: ComputeJobRequest): ComputeResult {
    currentJobId = request.id;
    cancelled = false;

    try {
      let result: ComputeResult;
      // Guard at worker boundary: repunits must always use exact classification.
      const effectiveMode = request.mode === 'preview' && isRepunit(request.digitsLE)
        ? 'exact'
        : request.mode;

      if (effectiveMode === 'exact') {
        result = computeExactSquare(request.digitsLE, request.base, isCancelled);
      } else {
        result = computePreviewSquare(request.digitsLE, request.base);
      }

      if (cancelled) {
        throw new Error('Job cancelled or timed out');
      }

      return result;
    } finally {
      currentJobId = null;
    }
  },

  /**
   * Cancel the current running job.
   * Sets the flag that the cooperative cancellation loop checks.
   */
  cancel(): void {
    cancelled = true;
  },

  /**
   * Get the current job ID (for latest-wins check).
   */
  getCurrentJobId(): string | null {
    return currentJobId;
  },

  /**
   * Ping for health check.
   */
  ping(): string {
    return 'pong';
  }
};

// Expose via Comlink
import { expose } from 'comlink';
expose(workerApi);

export type WorkerApi = typeof workerApi;
