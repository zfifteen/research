/**
 * Compute slice — job state, preview/exact status, approximation flags, cancellation.
 */
import type { StateCreator } from 'zustand';
import type { ComputeResult, JobStatus } from '../../math/types';

export interface ComputeSlice {
  jobId: string | null;
  jobStatus: JobStatus;
  computeResult: ComputeResult | null;
  isApproximate: boolean;
  error: string | null;
  progress: number;

  setJobId: (id: string | null) => void;
  setJobStatus: (status: JobStatus) => void;
  setComputeResult: (result: ComputeResult | null) => void;
  setError: (error: string | null) => void;
  setProgress: (progress: number) => void;
  clearCompute: () => void;
}

export const createComputeSlice: StateCreator<ComputeSlice, [], [], ComputeSlice> = (set) => ({
  jobId: null,
  jobStatus: 'idle',
  computeResult: null,
  isApproximate: false,
  error: null,
  progress: 0,

  setJobId: (id) => set({ jobId: id }),
  setJobStatus: (status) => set({ jobStatus: status }),
  setComputeResult: (result) =>
    set({
      computeResult: result,
      isApproximate: result?.isApproximate ?? false
    }),
  setError: (error) => set({ error, jobStatus: error ? 'error' : 'idle' }),
  setProgress: (progress) => set({ progress }),
  clearCompute: () =>
    set({
      jobId: null,
      jobStatus: 'idle',
      computeResult: null,
      isApproximate: false,
      error: null,
      progress: 0
    })
});
