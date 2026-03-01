/**
 * Timing utilities for performance measurement and adaptive profiling.
 */

/**
 * Estimate compute time for a given digit count using O(m^2) model.
 * Calibrated from benchmark.
 */
export function estimateComputeTimeMs(digitCount: number, benchmarkCoeff: number): number {
  return benchmarkCoeff * digitCount * digitCount;
}

/**
 * Run a simple benchmark to calibrate compute speed.
 * Returns a coefficient for the O(m^2) model.
 */
export function runBenchmark(): number {
  const testSize = 50;
  const digits = new Array(testSize).fill(1);
  const raw = new Array(2 * testSize - 1).fill(0n) as bigint[];

  const start = performance.now();
  for (let i = 0; i < testSize; i++) {
    const ai = BigInt(digits[i]!);
    for (let j = 0; j < testSize; j++) {
      const aj = BigInt(digits[j]!);
      raw[i + j] = (raw[i + j] ?? 0n) + ai * aj;
    }
  }
  const elapsed = performance.now() - start;

  // Coefficient = time / m^2
  return elapsed / (testSize * testSize);
}

/**
 * Detect device profile based on available features and screen.
 */
export function detectProfile(): 'desktop' | 'mobile' {
  if (typeof window === 'undefined') return 'desktop';

  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  );
  const isSmallScreen = window.innerWidth < 768;

  return (isMobile || isSmallScreen) ? 'mobile' : 'desktop';
}

/**
 * Debounce helper.
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  fn: T,
  ms: number
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout> | null = null;
  return (...args: Parameters<T>) => {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };
}
