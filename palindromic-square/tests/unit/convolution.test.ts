/**
 * Unit tests for self-convolution — MATH.md convolution formula.
 */
import { describe, it, expect } from 'vitest';
import { selfConvolution, findPeak } from '../../src/math/convolution';

describe('selfConvolution', () => {
  it('empty array yields [0n]', () => {
    expect(selfConvolution([])).toEqual([0n]);
  });

  it('single digit [1] yields [1n]', () => {
    expect(selfConvolution([1])).toEqual([1n]);
  });

  it('repunit [1,1] yields triangular [1,2,1]', () => {
    const raw = selfConvolution([1, 1]);
    expect(raw).toEqual([1n, 2n, 1n]);
  });

  it('repunit [1,1,1] yields [1,2,3,2,1]', () => {
    const raw = selfConvolution([1, 1, 1]);
    expect(raw).toEqual([1n, 2n, 3n, 2n, 1n]);
  });

  it('repunit n=9 peak is 9', () => {
    const digits = Array.from({ length: 9 }, () => 1);
    const raw = selfConvolution(digits);
    expect(findPeak(raw)).toBe(9n);
    // Verify triangular shape
    expect(raw.length).toBe(17);
    expect(raw[8]).toBe(9n); // center
  });

  it('repunit n=10 peak is 10', () => {
    const digits = Array.from({ length: 10 }, () => 1);
    const raw = selfConvolution(digits);
    expect(findPeak(raw)).toBe(10n);
  });

  // Verify triangular formula: c_k = min(k+1, 2n-1-k) for repunits
  it('repunit convolution matches triangular formula', () => {
    for (let n = 1; n <= 15; n++) {
      const digits = Array.from({ length: n }, () => 1);
      const raw = selfConvolution(digits);
      expect(raw.length).toBe(2 * n - 1);
      for (let k = 0; k < raw.length; k++) {
        const expected = BigInt(Math.min(k + 1, 2 * n - 1 - k));
        expect(raw[k]).toBe(expected);
      }
    }
  });

  it('non-uniform digits [2, 3] yields [4, 12, 9]', () => {
    const raw = selfConvolution([2, 3]);
    // (2+3x)^2 = 4 + 12x + 9x^2
    expect(raw).toEqual([4n, 12n, 9n]);
  });

  it('[1, 0, 1] yields [1, 0, 2, 0, 1]', () => {
    const raw = selfConvolution([1, 0, 1]);
    // (1 + x^2)^2 = 1 + 2x^2 + x^4
    expect(raw).toEqual([1n, 0n, 2n, 0n, 1n]);
  });
});

describe('findPeak', () => {
  it('returns max value', () => {
    expect(findPeak([1n, 5n, 3n])).toBe(5n);
  });

  it('single value', () => {
    expect(findPeak([7n])).toBe(7n);
  });

  it('all zeros', () => {
    expect(findPeak([0n, 0n])).toBe(0n);
  });
});
