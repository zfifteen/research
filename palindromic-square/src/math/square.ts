/**
 * Full square computation pipeline per MATH.md Algorithm B.
 * Orchestrates convolution -> carry normalization -> palindrome check.
 * Supports cooperative cancellation via shouldCancel callback.
 */
import type { Base, DigitsLE, ComputeResult } from './types';
import { selfConvolution, findPeak, stridedSample } from './convolution';
import { carryNormalize } from './carry';
import { checkPalindrome } from './palindrome';
import { repunitVerdict } from './repunit';

/**
 * Detect whether a LE digit array is a repunit (all digits are 1).
 */
export function isRepunit(digitsLE: DigitsLE): boolean {
  return digitsLE.length > 0 && digitsLE.every(d => d === 1);
}

/**
 * O(1) fast path for repunit inputs per TECH_SPEC §8.3.
 * Returns an exact ComputeResult with O(1) repunit classification.
 * Note: for full digit materialization we still compute exact coefficients/carry.
 * Returns null if the input is not a repunit.
 */
export function tryRepunitFastPath(digitsLE: DigitsLE, base: Base): ComputeResult | null {
  if (!isRepunit(digitsLE)) return null;

  const t0 = performance.now();
  const verdict = repunitVerdict(base, digitsLE.length);
  const t1 = performance.now();

  // We use O(1) repunitVerdict() for exact classification.
  // The exact square digits and raw coefficients are still materialized
  // so downstream views/exports receive a full exact ComputeResult.
  const raw = selfConvolution(digitsLE);
  const peak = findPeak(raw);
  const carryResult = carryNormalize(raw, base, digitsLE.length <= 5000);
  const t2 = performance.now();

  return {
    normalizedDigitsLE: carryResult.digitsLE,
    rawCoefficients: raw,
    peak,
    peakEstimate: null,
    isPalindrome: verdict.isPalindrome,  // Always boolean, never 'indeterminate'
    isApproximate: false,                // Always exact for repunit fast path
    carryTrace: carryResult.carryTrace.length > 0 ? carryResult.carryTrace : null,
    carryTraceOmitted: carryResult.carryTraceOmitted,
    carryTraceOmissionReason: carryResult.carryTraceOmissionReason,
    mode: 'exact',
    timing: {
      convolutionMs: t2 - t1,
      carryMs: 0,
      totalMs: t2 - t0
    }
  };
}

/**
 * Compute the exact square of a number given its digit representation.
 * Full pipeline: convolution -> carry -> palindrome check.
 * @param shouldCancel Optional callback checked periodically during hot loops
 */
export function computeExactSquare(
  digitsLE: DigitsLE,
  base: Base,
  shouldCancel?: () => boolean
): ComputeResult {
  // Repunit fast-path: O(1) verdict, skip cooperative cancellation overhead
  const repunitResult = tryRepunitFastPath(digitsLE, base);
  if (repunitResult) return repunitResult;

  const t0 = performance.now();

  // Step 1: Self-convolution (cancellation-aware)
  const raw = selfConvolution(digitsLE, shouldCancel);
  const t1 = performance.now();

  // Step 2: Find peak
  const peak = findPeak(raw);

  // Step 3-4: Carry normalization
  const carryResult = carryNormalize(raw, base, true);
  const t2 = performance.now();

  // Step 5: Palindrome check
  const isPalindrome = checkPalindrome(carryResult.digitsLE, false);

  return {
    normalizedDigitsLE: carryResult.digitsLE,
    rawCoefficients: raw,
    peak,
    peakEstimate: null,
    isPalindrome,
    isApproximate: false,
    carryTrace: carryResult.carryTrace.length > 0 ? carryResult.carryTrace : null,
    carryTraceOmitted: carryResult.carryTraceOmitted,
    carryTraceOmissionReason: carryResult.carryTraceOmissionReason,
    mode: 'exact',
    timing: {
      convolutionMs: t1 - t0,
      carryMs: t2 - t1,
      totalMs: t2 - t0
    }
  };
}

/**
 * Compute a preview of the square using strided sampling.
 * Used when exact computation would be too expensive.
 */
export function computePreviewSquare(digitsLE: DigitsLE, base: Base): ComputeResult {
  const t0 = performance.now();

  const maxSamples = 200;
  const centerWindowSize = Math.min(digitsLE.length * 2 - 1, 50);
  const { samples, centerWindow, centerStart } = stridedSample(digitsLE, maxSamples, centerWindowSize);

  const t1 = performance.now();

  // Estimate peak from center window
  let peakMin = 0n;
  let peakMax = 0n;
  for (const v of centerWindow) {
    if (v > peakMax) peakMax = v;
  }
  for (const s of samples) {
    if (s.value > peakMax) peakMax = s.value;
  }
  peakMin = peakMax; // In practice our sampling includes the center

  // Build approximate raw coefficients from samples
  const rawLen = 2 * digitsLE.length - 1;
  const rawApprox: bigint[] = new Array(rawLen).fill(0n) as bigint[];
  for (const s of samples) {
    if (s.position < rawApprox.length) {
      rawApprox[s.position] = s.value;
    }
  }
  for (let i = 0; i < centerWindow.length; i++) {
    const pos = centerStart + i;
    if (pos < rawApprox.length) {
      rawApprox[pos] = centerWindow[i]!;
    }
  }

  // Carry normalize for approximate digits
  const carryResult = carryNormalize(rawApprox, base, false);

  const t2 = performance.now();

  return {
    normalizedDigitsLE: carryResult.digitsLE,
    rawCoefficients: rawApprox,
    peak: peakMax,
    peakEstimate: { exact: null, peakMin, peakMax },
    isPalindrome: 'indeterminate',
    isApproximate: true,
    carryTrace: null,
    carryTraceOmitted: true,
    carryTraceOmissionReason: 'Preview mode: full carry trace not computed',
    mode: 'preview',
    timing: {
      convolutionMs: t1 - t0,
      carryMs: t2 - t1,
      totalMs: t2 - t0
    }
  };
}
