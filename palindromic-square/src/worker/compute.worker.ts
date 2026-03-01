/**
 * Compute Web Worker — runs math operations off the main thread.
 * Exposed via Comlink RPC interface per TECH_SPEC Section 8.2.
 */
import type { ComputeResult, ComputeJobRequest } from '../math/types';
import { computeExactSquare, computePreviewSquare } from '../math/square';

let currentJobId: string | null = null;
let cancelled = false;

const workerApi = {
  /**
   * Run a compute job (exact or preview).
   */
  compute(request: ComputeJobRequest): ComputeResult {
    currentJobId = request.id;
    cancelled = false;

    // Set up timeout
    const timeoutId = setTimeout(() => {
      cancelled = true;
    }, request.timeoutMs);

    try {
      let result: ComputeResult;

      if (request.mode === 'exact') {
        result = computeExactSquare(request.digitsLE, request.base);
      } else {
        result = computePreviewSquare(request.digitsLE, request.base);
      }

      if (cancelled) {
        throw new Error('Job cancelled or timed out');
      }

      return result;
    } finally {
      clearTimeout(timeoutId);
      currentJobId = null;
    }
  },

  /**
   * Cancel the current running job.
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
