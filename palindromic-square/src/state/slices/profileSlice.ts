/**
 * Profile slice — desktop/mobile profile, adaptive limits, benchmark results.
 * Includes override tracking per TECH_SPEC Section 9.
 */
import type { StateCreator } from 'zustand';
import type { DeviceProfile, PerformanceLimits } from '../../math/types';

export interface OverrideState {
  /** Whether the user has manually overridden safety limits */
  isOverridden: boolean;
  /** The overridden digit count (if overridden) */
  overriddenSafeDigits: number | null;
  /** Timestamp of last override */
  overriddenAt: string | null;
}

export interface ProfileSlice {
  profile: DeviceProfile;
  limits: PerformanceLimits;
  benchmarkCoeff: number;
  benchmarkComplete: boolean;
  overrideState: OverrideState;

  setProfile: (profile: DeviceProfile) => void;
  setLimits: (limits: PerformanceLimits) => void;
  setBenchmarkResult: (coeff: number) => void;
  applyOverride: (safeDigits: number) => void;
  clearOverride: () => void;
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

const DEFAULT_OVERRIDE_STATE: OverrideState = {
  isOverridden: false,
  overriddenSafeDigits: null,
  overriddenAt: null
};

export const createProfileSlice: StateCreator<ProfileSlice, [], [], ProfileSlice> = (set) => ({
  profile: 'desktop',
  limits: DESKTOP_LIMITS,
  benchmarkCoeff: 0.001,
  benchmarkComplete: false,
  overrideState: DEFAULT_OVERRIDE_STATE,

  setProfile: (profile) =>
    set({
      profile,
      limits: profile === 'desktop' ? DESKTOP_LIMITS : MOBILE_LIMITS,
      overrideState: DEFAULT_OVERRIDE_STATE
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
    }),
  applyOverride: (safeDigits) =>
    set((state) => ({
      limits: { ...state.limits, safeDigitsExact: safeDigits },
      overrideState: {
        isOverridden: true,
        overriddenSafeDigits: safeDigits,
        overriddenAt: new Date().toISOString()
      }
    })),
  clearOverride: () =>
    set((state) => {
      const budget = state.limits.exactComputeSoftBudgetMs;
      const safeDigits = state.benchmarkComplete
        ? Math.max(10, Math.floor(Math.sqrt(budget / state.benchmarkCoeff)))
        : (state.profile === 'desktop' ? DESKTOP_LIMITS.safeDigitsExact : MOBILE_LIMITS.safeDigitsExact);
      return {
        limits: { ...state.limits, safeDigitsExact: safeDigits },
        overrideState: DEFAULT_OVERRIDE_STATE
      };
    })
});

export { DESKTOP_LIMITS, MOBILE_LIMITS };
