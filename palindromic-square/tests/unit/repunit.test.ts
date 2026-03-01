/**
 * Unit tests for repunit fast verdict — MATH.md Algorithm A.
 */
import { describe, it, expect } from 'vitest';
import { repunitVerdict, getCliffEdge, makeRepunitDigitsLE } from '../../src/math/repunit';

describe('repunitVerdict', () => {
  // Golden vectors from MATH.md
  describe('base 10 canonical', () => {
    it('n=9 is pre-cliff (palindrome)', () => {
      const v = repunitVerdict(10, 9);
      expect(v.classification).toBe('pre-cliff');
      expect(v.isPalindrome).toBe(true);
      expect(v.peak).toBe(9);
      expect(v.cliffEdge).toBe(9);
    });

    it('n=10 is post-cliff (broken)', () => {
      const v = repunitVerdict(10, 10);
      expect(v.classification).toBe('post-cliff');
      expect(v.isPalindrome).toBe(false);
      expect(v.peak).toBe(10);
    });
  });

  // Base 2 special case from MATH.md
  describe('base 2 special case', () => {
    it('n=1 is pre-cliff', () => {
      const v = repunitVerdict(2, 1);
      expect(v.classification).toBe('pre-cliff');
      expect(v.isPalindrome).toBe(true);
    });

    it('n=2 is pre-cliff (palindrome)', () => {
      const v = repunitVerdict(2, 2);
      expect(v.classification).toBe('pre-cliff');
      expect(v.isPalindrome).toBe(true);
      expect(v.cliffEdge).toBe(2);
    });

    it('n=3 is post-cliff (broken)', () => {
      const v = repunitVerdict(2, 3);
      expect(v.classification).toBe('post-cliff');
      expect(v.isPalindrome).toBe(false);
    });
  });

  // Cliff behavior across all bases 2..36
  describe('cliff behavior across bases', () => {
    for (let b = 3; b <= 36; b++) {
      it(`base ${b}: n=${b - 1} is pre-cliff, n=${b} is post-cliff`, () => {
        const pre = repunitVerdict(b, b - 1);
        expect(pre.classification).toBe('pre-cliff');
        expect(pre.isPalindrome).toBe(true);

        const post = repunitVerdict(b, b);
        expect(post.classification).toBe('post-cliff');
        expect(post.isPalindrome).toBe(false);
      });
    }

    it('base 2: n=2 is pre-cliff, n=3 is post-cliff', () => {
      const pre = repunitVerdict(2, 2);
      expect(pre.classification).toBe('pre-cliff');
      expect(pre.isPalindrome).toBe(true);

      const post = repunitVerdict(2, 3);
      expect(post.classification).toBe('post-cliff');
      expect(post.isPalindrome).toBe(false);
    });
  });

  describe('edge cases', () => {
    it('throws for base < 2', () => {
      expect(() => repunitVerdict(1, 1)).toThrow();
    });

    it('throws for base > 36', () => {
      expect(() => repunitVerdict(37, 1)).toThrow();
    });

    it('throws for length < 1', () => {
      expect(() => repunitVerdict(10, 0)).toThrow();
    });

    it('n=1 is always pre-cliff for any base', () => {
      for (let b = 2; b <= 36; b++) {
        const v = repunitVerdict(b, 1);
        expect(v.classification).toBe('pre-cliff');
        expect(v.isPalindrome).toBe(true);
      }
    });
  });
});

describe('getCliffEdge', () => {
  it('base 2 returns 2', () => {
    expect(getCliffEdge(2)).toBe(2);
  });

  it('base 10 returns 9', () => {
    expect(getCliffEdge(10)).toBe(9);
  });

  it('base 36 returns 35', () => {
    expect(getCliffEdge(36)).toBe(35);
  });
});

describe('makeRepunitDigitsLE', () => {
  it('returns array of all 1s', () => {
    expect(makeRepunitDigitsLE(5)).toEqual([1, 1, 1, 1, 1]);
  });

  it('length 1', () => {
    expect(makeRepunitDigitsLE(1)).toEqual([1]);
  });
});
