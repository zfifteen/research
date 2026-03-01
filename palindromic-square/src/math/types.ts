/**
 * Core types for the palindromic square math engine.
 * All types follow MATH.md canonical terminology.
 * No `any` types allowed in math/worker modules.
 */

/** Valid base range: 2..36 */
export type Base = number;

/** Digits in little-endian order (index 0 = least significant). digitsLE per MATH.md */
export type DigitsLE = number[];

/** Canonical MSB-first string representation per TECH_SPEC Section 8.4 */
export type DigitsMSB = string;

/** Carry trace entry for animator input */
export interface CarryTraceEntry {
  position: number;
  rawCoefficient: bigint;
  incomingCarry: bigint;
  digitOut: number;
  outgoingCarry: bigint;
}

/** Palindrome verdict */
export type PalindromeVerdict = true | false | 'indeterminate';

/** Repunit cliff classification */
export type CliffClassification = 'pre-cliff' | 'post-cliff';

/** Preview peak estimate */
export interface PeakEstimate {
  exact: bigint | null;
  peakMin: bigint | null;
  peakMax: bigint | null;
}

/** Compute result from worker */
export interface ComputeResult {
  /** Normalized square digits in LE order */
  normalizedDigitsLE: DigitsLE;
  /** Raw convolution coefficients (pre-carry) */
  rawCoefficients: bigint[];
  /** Peak raw coefficient value */
  peak: bigint;
  /** Peak estimate for preview mode */
  peakEstimate: PeakEstimate | null;
  /** Palindrome verdict */
  isPalindrome: PalindromeVerdict;
  /** Whether this result is approximate (preview mode) */
  isApproximate: boolean;
  /** Carry trace for animator (exact mode only) */
  carryTrace: CarryTraceEntry[] | null;
  /** If carry trace was omitted for size reasons */
  carryTraceOmitted: boolean;
  carryTraceOmissionReason: string | null;
  /** Mode that produced this result */
  mode: 'preview' | 'exact';
  /** Timing diagnostics */
  timing: {
    convolutionMs: number;
    carryMs: number;
    totalMs: number;
  };
}

/** Repunit verdict (O(1) fast path) */
export interface RepunitVerdict {
  base: Base;
  length: number;
  classification: CliffClassification;
  cliffEdge: number;
  isPalindrome: boolean;
  peak: number;
}

/** Project data for persistence */
export interface ProjectData {
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
  base: Base;
  rootDigits: DigitsMSB;
  settings: ProjectSettings;
  cachedArtifacts: CachedArtifacts | null;
}

export interface ProjectSettings {
  advancedMode: boolean;
  animatorSpeed: number;
}

export interface CachedArtifacts {
  mode: 'preview' | 'exact';
  isApproximate: boolean;
  computedAt: string;
}

/** JSON export schema per TECH_SPEC Section 4.7 */
export interface ExportPayload {
  schemaVersion: 'v1';
  exportedAt: string;
  project: {
    base: Base;
    rootDigits: DigitsMSB;
    name: string;
  };
  result: {
    mode: 'preview' | 'exact';
    isApproximate: boolean;
    normalizedSquareDigits: DigitsMSB;
    peak: string; // BigInt as base-10 string
    isPalindrome: PalindromeVerdict;
    rawCoefficients: string[]; // BigInt[] as base-10 strings
  };
}

/** URL state payload */
export interface URLStatePayload {
  v: number;
  b: Base;
  r: DigitsMSB;
}

/** Worker job request */
export interface ComputeJobRequest {
  id: string;
  base: Base;
  digitsLE: DigitsLE;
  mode: 'preview' | 'exact';
  timeoutMs: number;
}

/** Worker job status */
export type JobStatus = 'idle' | 'running' | 'completed' | 'cancelled' | 'error' | 'timeout';

/** Device performance profile */
export type DeviceProfile = 'desktop' | 'mobile';

/** Adaptive performance limits */
export interface PerformanceLimits {
  profile: DeviceProfile;
  safeDigitsExact: number;
  inputToPreviewMs: number;
  exactComputeSoftBudgetMs: number;
  warningThresholdMs: number;
  workerHardTimeoutMs: number;
  autoAbortFpsTrigger: number;
  autoAbortFpsDurationMs: number;
}

/** Gallery example entry */
export interface GalleryEntry {
  id: string;
  name: string;
  description: string;
  base: Base;
  rootDigits: DigitsMSB;
  family: string;
  tags: string[];
}
