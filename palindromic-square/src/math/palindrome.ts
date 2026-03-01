/**
 * Palindrome checking for digit arrays.
 */
import type { DigitsLE, PalindromeVerdict } from './types';

/**
 * Check if a digit array (LE order) represents a palindrome.
 * Trims leading zeros at MSB end before checking.
 * 
 * Returns true/false for exact verdict, 'indeterminate' if approximate.
 */
export function checkPalindrome(digitsLE: DigitsLE, isApproximate: boolean): PalindromeVerdict {
  if (isApproximate) return 'indeterminate';

  // Trim MSB trailing zeros (since LE, MSB is at end)
  let end = digitsLE.length - 1;
  while (end > 0 && digitsLE[end] === 0) {
    end--;
  }

  const trimmed = digitsLE.slice(0, end + 1);
  const len = trimmed.length;

  for (let i = 0; i < Math.floor(len / 2); i++) {
    if (trimmed[i] !== trimmed[len - 1 - i]) {
      return false;
    }
  }

  return true;
}

/**
 * Format digits as palindrome display string (MSB first).
 */
export function digitsToDisplayString(digitsLE: DigitsLE, _base: number): string {
  // Trim MSB trailing zeros
  let end = digitsLE.length - 1;
  while (end > 0 && digitsLE[end] === 0) {
    end--;
  }

  const trimmed = digitsLE.slice(0, end + 1);
  // MSB first for display
  return trimmed.reverse().map(d => digitToSymbol(d)).join('');
}

const SYMBOLS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';

export function digitToSymbol(d: number): string {
  if (d < 0 || d >= 36) throw new RangeError(`Digit ${d} out of range`);
  return SYMBOLS[d]!;
}

export function symbolToDigit(s: string): number {
  const upper = s.toUpperCase();
  const idx = SYMBOLS.indexOf(upper);
  if (idx === -1) throw new RangeError(`Invalid digit symbol: ${s}`);
  return idx;
}
