/**
 * Profile slice — desktop/mobile profile, adaptive limits, benchmark results.
 */
import type { StateCreator } from 'zustand';
import type { DeviceProfile, PerformanceLimits } from '../../math/types';

export interface ProfileSlice {
  profile: DeviceProfile;
  limits: PerformanceLimits;
  benchmarkCoeff: number;
  benchmarkComplete: boolean;

  setProfile: (profile: DeviceProfile) => void;
  setLimits: (limits: PerformanceLimits) => void;
  setBenchmarkResult: (coeff: number) => void;
}

const DESKTOP_LIMITS: PerformanceLimits = {
  profile: 'desktop',
  safeDigitsExact: 500,
  inputToPreviewMs: 150,
  exactComputeSoftBudgetMs: 2500,
  warningThresholdMs: 2500,
  workerHardTimeoutMs: 15000,
  autoAbortFpsTrigger: 20,
  autoAbortFpsDurationMs: 2000
};

const MOBILE_LIMITS: PerformanceLimits = {
  profile: 'mobile',
  safeDigitsExact: 200,
  inputToPreviewMs: 300,
  exactComputeSoftBudgetMs: 5000,
  warningThresholdMs: 5000,
  workerHardTimeoutMs: 25000,
  autoAbortFpsTrigger: 15,
  autoAbortFpsDurationMs: 2000
};

export const createProfileSlice: StateCreator<ProfileSlice, [], [], ProfileSlice> = (set) => ({
  profile: 'desktop',
  limits: DESKTOP_LIMITS,
  benchmarkCoeff: 0.001,
  benchmarkComplete: false,

  setProfile: (profile) =>
    set({
      profile,
      limits: profile === 'desktop' ? DESKTOP_LIMITS : MOBILE_LIMITS
    }),
  setLimits: (limits) => set({ limits }),
  setBenchmarkResult: (coeff) =>
    set((state) => {
      const budget = state.limits.exactComputeSoftBudgetMs;
      const safeDigits = Math.max(10, Math.floor(Math.sqrt(budget / coeff)));
      return {
        benchmarkCoeff: coeff,
        benchmarkComplete: true,
        limits: { ...state.limits, safeDigitsExact: safeDigits }
      };
    })
});

export { DESKTOP_LIMITS, MOBILE_LIMITS };
