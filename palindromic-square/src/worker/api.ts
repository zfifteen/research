/**
 * Worker API — main-thread interface to compute worker.
 * Implements latest-wins cancellation per TECH_SPEC Section 6.3.
 */
import { wrap, type Remote } from 'comlink';
import type { WorkerApi } from './compute.worker';
import type { Base, DigitsLE, ComputeResult, ComputeJobRequest } from '../math/types';
import { v4 as uuid } from 'uuid';

let worker: Worker | null = null;
let api: Remote<WorkerApi> | null = null;
let currentJobId: string | null = null;

function getWorker(): { worker: Worker; api: Remote<WorkerApi> } {
  if (!worker || !api) {
    worker = new Worker(new URL('./compute.worker.ts', import.meta.url), { type: 'module' });
    api = wrap<WorkerApi>(worker);
  }
  return { worker, api };
}

/**
 * Submit a compute job. Latest-wins semantics: cancels any in-flight job.
 */
export async function submitJob(
  base: Base,
  digitsLE: DigitsLE,
  mode: 'preview' | 'exact',
  timeoutMs: number
): Promise<{ result: ComputeResult; jobId: string } | { cancelled: true; jobId: string }> {
  const jobId = uuid();
  currentJobId = jobId;

  const { api: workerApi } = getWorker();

  // Cancel previous job
  try {
    await workerApi.cancel();
  } catch {
    // Ignore cancel errors
  }

  const request: ComputeJobRequest = {
    id: jobId,
    base,
    digitsLE,
    mode,
    timeoutMs
  };

  try {
    const result = await workerApi.compute(request);

    // Check if this is still the latest job
    if (currentJobId !== jobId) {
      return { cancelled: true, jobId };
    }

    return { result, jobId };
  } catch (e) {
    if (currentJobId !== jobId) {
      return { cancelled: true, jobId };
    }
    throw e;
  }
}

/**
 * Cancel the current job.
 */
export async function cancelCurrentJob(): Promise<void> {
  currentJobId = null;
  if (api) {
    try {
      await api.cancel();
    } catch {
      // Worker might be unresponsive, terminate and recreate
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
    currentJobId = null;
  }
}

/**
 * Get current job ID.
 */
export function getCurrentJobId(): string | null {
  return currentJobId;
}
