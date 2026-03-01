/**
 * Unit tests for full square pipeline — golden vectors from MATH.md.
 */
import { describe, it, expect } from 'vitest';
import { computeExactSquare } from '../../src/math/square';
import { checkPalindrome } from '../../src/math/palindrome';
import { serializeLEtoMSB } from '../../src/utils/encoding';

describe('computeExactSquare', () => {
  // Golden vector: base 10, n=9
  it('base-10 repunit n=9: 111111111^2 = 12345678987654321 (palindrome)', () => {
    const digits = Array.from({ length: 9 }, () => 1);
    const result = computeExactSquare(digits, 10);

    const squareMSB = serializeLEtoMSB(result.normalizedDigitsLE, 10);
    expect(squareMSB).toBe('12345678987654321');
    expect(result.isPalindrome).toBe(true);
    expect(result.peak).toBe(9n);
    expect(result.isApproximate).toBe(false);
    expect(result.mode).toBe('exact');
  });

  // Golden vector: base 10, n=10
  it('base-10 repunit n=10: 1111111111^2 = 1234567900987654321 (not palindrome)', () => {
    const digits = Array.from({ length: 10 }, () => 1);
    const result = computeExactSquare(digits, 10);

    const squareMSB = serializeLEtoMSB(result.normalizedDigitsLE, 10);
    expect(squareMSB).toBe('1234567900987654321');
    expect(result.isPalindrome).toBe(false);
    expect(result.peak).toBe(10n);
  });

  // Golden vector: base 2, n=2
  it('base-2 repunit n=2: 11^2 = 1001 (palindrome)', () => {
    const digits = [1, 1];
    const result = computeExactSquare(digits, 2);

    const squareMSB = serializeLEtoMSB(result.normalizedDigitsLE, 2);
    expect(squareMSB).toBe('1001');
    expect(result.isPalindrome).toBe(true);
  });

  // Golden vector: base 2, n=3
  it('base-2 repunit n=3: 111^2 = 110001 (not palindrome)', () => {
    const digits = [1, 1, 1];
    const result = computeExactSquare(digits, 2);

    const squareMSB = serializeLEtoMSB(result.normalizedDigitsLE, 2);
    expect(squareMSB).toBe('110001');
    expect(result.isPalindrome).toBe(false);
  });

  // Sparse pattern
  it('base-10 sparse 101^2 = 10201 (palindrome)', () => {
    const digits = [1, 0, 1]; // LE
    const result = computeExactSquare(digits, 10);

    const squareMSB = serializeLEtoMSB(result.normalizedDigitsLE, 10);
    expect(squareMSB).toBe('10201');
    expect(result.isPalindrome).toBe(true);
    expect(result.peak).toBe(2n);
  });

  // Single digit
  it('single digit: 7^2 = 49 in base 10', () => {
    const result = computeExactSquare([7], 10);
    const squareMSB = serializeLEtoMSB(result.normalizedDigitsLE, 10);
    expect(squareMSB).toBe('49');
  });

  // Carry trace availability
  it('carry trace is available for small exact computations', () => {
    const digits = Array.from({ length: 9 }, () => 1);
    const result = computeExactSquare(digits, 10);
    expect(result.carryTrace).not.toBeNull();
    expect(result.carryTraceOmitted).toBe(false);
  });

  // Timing diagnostics
  it('includes timing diagnostics', () => {
    const result = computeExactSquare([1, 1], 10);
    expect(result.timing.totalMs).toBeGreaterThanOrEqual(0);
    expect(result.timing.convolutionMs).toBeGreaterThanOrEqual(0);
    expect(result.timing.carryMs).toBeGreaterThanOrEqual(0);
  });
});

describe('checkPalindrome', () => {
  it('true for palindromic digits', () => {
    expect(checkPalindrome([1, 2, 3, 2, 1], false)).toBe(true);
  });

  it('false for non-palindromic digits', () => {
    expect(checkPalindrome([1, 2, 3, 4, 5], false)).toBe(false);
  });

  it('indeterminate when approximate', () => {
    expect(checkPalindrome([1, 2, 3, 2, 1], true)).toBe('indeterminate');
  });

  it('handles trailing zeros (MSB)', () => {
    // [1, 0, 0, 1, 0, 0] -> trimmed to [1, 0, 0, 1] -> palindrome
    expect(checkPalindrome([1, 0, 0, 1, 0, 0], false)).toBe(true);
  });

  it('single digit is palindrome', () => {
    expect(checkPalindrome([5], false)).toBe(true);
  });
});
