/**
 * Full square computation pipeline per MATH.md Algorithm B.
 * Orchestrates convolution -> carry normalization -> palindrome check.
 */
import type { Base, DigitsLE, ComputeResult } from './types';
import { selfConvolution, findPeak, stridedSample } from './convolution';
import { carryNormalize } from './carry';
import { checkPalindrome } from './palindrome';

/**
 * Compute the exact square of a number given its digit representation.
 * Full pipeline: convolution -> carry -> palindrome check.
 */
export function computeExactSquare(digitsLE: DigitsLE, base: Base): ComputeResult {
  const t0 = performance.now();

  // Step 1: Self-convolution
  const raw = selfConvolution(digitsLE);
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
