/**
 * Worker API — main-thread interface to compute worker.
 * Implements latest-wins cancellation per TECH_SPEC Section 6.3.
 *
 * Preemption strategy:
 * 1. Cooperative: convolution hot-loop checks a `cancelled` flag every N iterations.
 * 2. Hard timeout: Promise.race kills worker after timeoutMs.
 * 3. Supersede: when a new job arrives while one is running, the old worker is
 *    immediately terminated and a fresh worker is spawned — guaranteeing prompt
 *    preemption regardless of where the synchronous loop is.
 */
import { wrap, type Remote } from 'comlink';
import type { WorkerApi } from './compute.worker';
import type { Base, DigitsLE, ComputeResult, ComputeJobRequest } from '../math/types';
import { v4 as uuid } from 'uuid';

let worker: Worker | null = null;
let api: Remote<WorkerApi> | null = null;
let currentJobId: string | null = null;
/** True while a compute() RPC is in-flight. */
let jobInFlight = false;

function ensureWorker(): { worker: Worker; api: Remote<WorkerApi> } {
  if (!worker || !api) {
    worker = new Worker(new URL('./compute.worker.ts', import.meta.url), { type: 'module' });
    api = wrap<WorkerApi>(worker);
  }
  return { worker, api };
}

/**
 * Submit a compute job. Latest-wins semantics.
 *
 * If a job is currently in-flight the old worker is **terminated** immediately
 * (not just cooperative-cancelled) so the new job starts on a clean worker
 * without waiting for the O(n²) loop to reach a cancellation check.
 */
export async function submitJob(
  base: Base,
  digitsLE: DigitsLE,
  mode: 'preview' | 'exact',
  timeoutMs: number
): Promise<{ result: ComputeResult; jobId: string } | { cancelled: true; jobId: string }> {
  const jobId = uuid();

  // ── Supersede: hard-kill any in-flight job ──
  if (jobInFlight) {
    // Terminate the worker entirely so the old synchronous loop dies instantly.
    terminateWorker();
  }

  currentJobId = jobId;

  const { api: workerApi } = ensureWorker();

  const request: ComputeJobRequest = {
    id: jobId,
    base,
    digitsLE,
    mode,
    timeoutMs
  };

  // Race: compute vs hard timeout
  let hardTimeoutId: ReturnType<typeof setTimeout> | null = null;
  let timedOut = false;

  const hardTimeoutPromise = new Promise<null>((resolve) => {
    hardTimeoutId = setTimeout(() => {
      timedOut = true;
      resolve(null);
    }, timeoutMs);
  });

  jobInFlight = true;
  try {
    const raceResult = await Promise.race([
      workerApi.compute(request),
      hardTimeoutPromise
    ]);

    if (hardTimeoutId) clearTimeout(hardTimeoutId);

    if (timedOut || raceResult === null) {
      terminateWorker();
      return { cancelled: true, jobId };
    }

    // Stale-result suppression: if another job was submitted while we awaited,
    // discard this result even though it completed.
    if (currentJobId !== jobId) {
      return { cancelled: true, jobId };
    }

    return { result: raceResult, jobId };
  } catch (e) {
    if (hardTimeoutId) clearTimeout(hardTimeoutId);
    if (currentJobId !== jobId) {
      return { cancelled: true, jobId };
    }
    throw e;
  } finally {
    // Only clear the flag if we are still the current job.
    if (currentJobId === jobId) {
      jobInFlight = false;
    }
  }
}

/**
 * Cancel the current job.
 */
export async function cancelCurrentJob(): Promise<void> {
  currentJobId = null;
  if (jobInFlight) {
    terminateWorker();
  } else if (api) {
    try {
      await api.cancel();
    } catch {
      terminateWorker();
    }
  }
}

/**
 * Terminate the worker entirely (kill-switch).
 */
export function terminateWorker(): void {
  if (worker) {
    worker.terminate();
    worker = null;
    api = null;
  }
  jobInFlight = false;
  // Note: we do NOT clear currentJobId here — submitJob manages that.
}

/**
 * Get current job ID.
 */
export function getCurrentJobId(): string | null {
  return currentJobId;
}
