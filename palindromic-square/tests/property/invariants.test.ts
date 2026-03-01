/**
 * Property tests for math invariants — TECH_SPEC Section 11.1.
 */
import { describe, it, expect } from 'vitest';
import { computeExactSquare } from '../../src/math/square';
import { selfConvolution, findPeak } from '../../src/math/convolution';
import { validateCarryTrace, validateCarryChain, validateNormalizedDigits } from '../../src/math/invariants';
import { repunitVerdict } from '../../src/math/repunit';

function randomDigits(length: number, base: number): number[] {
  return Array.from({ length }, () => Math.floor(Math.random() * base));
}

function ensureNonZero(digits: number[], base: number): number[] {
  if (digits.every(d => d === 0)) {
    digits[0] = 1;
  }
  return digits;
}

describe('property tests', () => {
  // Deterministic output for same input
  describe('determinism', () => {
    it('same input produces identical output', () => {
      for (let trial = 0; trial < 20; trial++) {
        const base = 2 + Math.floor(Math.random() * 35);
        const len = 1 + Math.floor(Math.random() * 20);
        const digits = ensureNonZero(randomDigits(len, base), base);

        const r1 = computeExactSquare(digits, base);
        const r2 = computeExactSquare(digits, base);

        expect(r1.normalizedDigitsLE).toEqual(r2.normalizedDigitsLE);
        expect(r1.peak).toBe(r2.peak);
        expect(r1.isPalindrome).toBe(r2.isPalindrome);
      }
    });
  });

  // Carry normalization bounds: all digits in 0..b-1
  describe('carry normalization bounds', () => {
    it('all normalized digits are in range 0..b-1', () => {
      for (let trial = 0; trial < 50; trial++) {
        const base = 2 + Math.floor(Math.random() * 35);
        const len = 1 + Math.floor(Math.random() * 15);
        const digits = ensureNonZero(randomDigits(len, base), base);

        const result = computeExactSquare(digits, base);
        expect(validateNormalizedDigits(result.normalizedDigitsLE, base)).toBe(true);
      }
    });
  });

  // Carry trace consistency
  describe('carry trace consistency', () => {
    it('digitOut == (rawCoefficient + incomingCarry) mod base, outgoingCarry == floor((rawCoefficient + incomingCarry) / base)', () => {
      for (let trial = 0; trial < 30; trial++) {
        const base = 2 + Math.floor(Math.random() * 35);
        const len = 1 + Math.floor(Math.random() * 10);
        const digits = ensureNonZero(randomDigits(len, base), base);

        const result = computeExactSquare(digits, base);
        if (result.carryTrace && result.carryTrace.length > 0) {
          expect(validateCarryTrace(result.carryTrace, base)).toBe(true);
          expect(validateCarryChain(result.carryTrace)).toBe(true);
        }
      }
    });
  });

  // Palindrome verdict consistency
  describe('palindrome verdict consistency', () => {
    it('exact mode never returns indeterminate', () => {
      for (let trial = 0; trial < 20; trial++) {
        const base = 2 + Math.floor(Math.random() * 35);
        const len = 1 + Math.floor(Math.random() * 10);
        const digits = ensureNonZero(randomDigits(len, base), base);

        const result = computeExactSquare(digits, base);
        expect(result.isPalindrome).not.toBe('indeterminate');
        expect(result.isApproximate).toBe(false);
      }
    });
  });

  // Repunit cliff behavior across all bases
  describe('repunit cliff behavior across b in [2,36]', () => {
    for (let b = 2; b <= 36; b++) {
      it(`base ${b}: cliff behavior is correct`, () => {
        if (b >= 3) {
          // pre-cliff: n = b-1
          const pre = repunitVerdict(b, b - 1);
          expect(pre.classification).toBe('pre-cliff');
          expect(pre.isPalindrome).toBe(true);

          // post-cliff: n = b
          const post = repunitVerdict(b, b);
          expect(post.classification).toBe('post-cliff');
          expect(post.isPalindrome).toBe(false);

          // Verify with actual computation for small bases
          if (b <= 16 && b - 1 <= 15) {
            const preDigits = Array.from({ length: b - 1 }, () => 1);
            const preResult = computeExactSquare(preDigits, b);
            expect(preResult.isPalindrome).toBe(true);

            const postDigits = Array.from({ length: b }, () => 1);
            const postResult = computeExactSquare(postDigits, b);
            expect(postResult.isPalindrome).toBe(false);
          }
        } else {
          // b = 2
          const pre = repunitVerdict(2, 2);
          expect(pre.classification).toBe('pre-cliff');
          expect(pre.isPalindrome).toBe(true);

          const post = repunitVerdict(2, 3);
          expect(post.classification).toBe('post-cliff');
          expect(post.isPalindrome).toBe(false);

          // Verify with actual computation
          const preResult = computeExactSquare([1, 1], 2);
          expect(preResult.isPalindrome).toBe(true);

          const postResult = computeExactSquare([1, 1, 1], 2);
          expect(postResult.isPalindrome).toBe(false);
        }
      });
    }
  });

  // Repunit peak = n
  describe('repunit peak equals length', () => {
    it('peak equals n for repunits across bases', () => {
      for (let b = 2; b <= 20; b++) {
        for (let n = 1; n <= Math.min(b + 2, 15); n++) {
          const digits = Array.from({ length: n }, () => 1);
          const raw = selfConvolution(digits);
          const peak = findPeak(raw);
          expect(peak).toBe(BigInt(n));
        }
      }
    });
  });
});
