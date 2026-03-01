/**
 * Repunit fast verdict — O(1) classification per MATH.md Algorithm A.
 * No floating-point, purely integer logic.
 */
import type { Base, RepunitVerdict, CliffClassification } from './types';

/**
 * Classify a repunit of length n in base b.
 * 
 * Rules from MATH.md:
 * - b >= 3: palindromic exactly up to n = b-1, cliff at n = b
 * - b = 2:  palindromic up to n = 2, cliff at n = 3
 */
export function repunitVerdict(base: Base, length: number): RepunitVerdict {
  if (base < 2 || base > 36) {
    throw new RangeError(`Base must be 2..36, got ${base}`);
  }
  if (length < 1) {
    throw new RangeError(`Repunit length must be >= 1, got ${length}`);
  }

  let cliffEdge: number;
  let classification: CliffClassification;
  let isPalindrome: boolean;

  if (base === 2) {
    // Special case: b=2, cliff at n=2->3
    cliffEdge = 2;
    if (length <= 2) {
      classification = 'pre-cliff';
      isPalindrome = true;
    } else {
      classification = 'post-cliff';
      isPalindrome = false;
    }
  } else {
    // General case: b>=3, cliff at n=b-1->b
    cliffEdge = base - 1;
    if (length <= base - 1) {
      classification = 'pre-cliff';
      isPalindrome = true;
    } else {
      classification = 'post-cliff';
      isPalindrome = false;
    }
  }

  // For repunits, peak = n (the length)
  const peak = length;

  return {
    base,
    length,
    classification,
    cliffEdge,
    isPalindrome,
    peak
  };
}

/**
 * Get the cliff edge for a given base.
 */
export function getCliffEdge(base: Base): number {
  if (base === 2) return 2;
  return base - 1;
}

/**
 * Generate a repunit digit array (all 1s) in LE order.
 */
export function makeRepunitDigitsLE(length: number): number[] {
  return Array.from({ length }, () => 1);
}
