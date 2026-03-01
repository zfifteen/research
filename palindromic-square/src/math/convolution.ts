/**
 * Self-convolution of digit arrays per MATH.md Algorithm B step 1.
 * Uses BigInt for exact integer arithmetic.
 * Supports cooperative cancellation via periodic checks.
 */
import type { DigitsLE } from './types';

/** Check interval for cooperative cancellation (every N outer iterations). */
const CANCEL_CHECK_INTERVAL = 64;

/**
 * Cancellation-aware self-convolution.
 * Checks `shouldCancel()` every CANCEL_CHECK_INTERVAL outer iterations.
 * Throws if cancelled.
 *
 * raw[k] = sum_{i} a[i] * a[k-i] for valid i ranges.
 * Input: digits in LE order.
 * Output: raw coefficients array of length 2*m - 1 (or 1 if m=0).
 * Time: O(m^2)
 */
export function selfConvolution(
  digitsLE: DigitsLE,
  shouldCancel?: () => boolean
): bigint[] {
  const m = digitsLE.length;
  if (m === 0) return [0n];

  const rawLen = 2 * m - 1;
  const raw: bigint[] = new Array(rawLen).fill(0n) as bigint[];

  for (let i = 0; i < m; i++) {
    // Cooperative cancellation check
    if (shouldCancel && i % CANCEL_CHECK_INTERVAL === 0 && shouldCancel()) {
      throw new Error('Job cancelled');
    }

    const ai = BigInt(digitsLE[i]!);
    for (let j = 0; j < m; j++) {
      const aj = BigInt(digitsLE[j]!);
      raw[i + j] = (raw[i + j] ?? 0n) + ai * aj;
    }
  }

  return raw;
}

/**
 * Find the peak (maximum) raw convolution coefficient.
 */
export function findPeak(raw: bigint[]): bigint {
  let peak = 0n;
  for (const v of raw) {
    if (v > peak) peak = v;
  }
  return peak;
}

/**
 * Strided sampling of convolution for preview mode.
 * Returns sampled coefficients at evenly-spaced positions plus a center window.
 */
export function stridedSample(
  digitsLE: DigitsLE,
  maxSamples: number,
  centerWindowSize: number
): { samples: Array<{ position: number; value: bigint }>; centerWindow: bigint[]; centerStart: number } {
  const m = digitsLE.length;
  if (m === 0) {
    return { samples: [], centerWindow: [0n], centerStart: 0 };
  }

  const rawLen = 2 * m - 1;
  const centerPos = m - 1;
  const halfWindow = Math.floor(centerWindowSize / 2);
  const centerStart = Math.max(0, centerPos - halfWindow);
  const centerEnd = Math.min(rawLen - 1, centerPos + halfWindow);

  // Compute exact center window
  const centerWindow: bigint[] = [];
  for (let k = centerStart; k <= centerEnd; k++) {
    let sum = 0n;
    const iMin = Math.max(0, k - (m - 1));
    const iMax = Math.min(m - 1, k);
    for (let i = iMin; i <= iMax; i++) {
      sum += BigInt(digitsLE[i]!) * BigInt(digitsLE[k - i]!);
    }
    centerWindow.push(sum);
  }

  // Strided samples across the full range
  const stride = Math.max(1, Math.floor(rawLen / maxSamples));
  const samples: Array<{ position: number; value: bigint }> = [];
  for (let k = 0; k < rawLen; k += stride) {
    let sum = 0n;
    const iMin = Math.max(0, k - (m - 1));
    const iMax = Math.min(m - 1, k);
    for (let i = iMin; i <= iMax; i++) {
      sum += BigInt(digitsLE[i]!) * BigInt(digitsLE[k - i]!);
    }
    samples.push({ position: k, value: sum });
  }

  return { samples, centerWindow, centerStart };
}
