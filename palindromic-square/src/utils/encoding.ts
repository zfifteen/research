/**
 * Canonical encoding/decoding per TECH_SPEC Section 8.4.
 * MSB-first uppercase string <-> LE digit array conversions.
 */
import type { Base, DigitsLE, DigitsMSB } from '../math/types';

const SYMBOLS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';

/**
 * Parse canonical MSB string to LE digit array.
 * Case-insensitive parse, validates against base.
 */
export function parseMSBtoLE(msb: DigitsMSB, base: Base): DigitsLE {
  if (msb.length === 0) throw new Error('Empty digit string');

  const digits: DigitsLE = [];
  for (let i = msb.length - 1; i >= 0; i--) {
    const ch = msb[i]!.toUpperCase();
    const val = SYMBOLS.indexOf(ch);
    if (val === -1 || val >= base) {
      throw new Error(`Invalid digit '${msb[i]}' for base ${base}`);
    }
    digits.push(val);
  }
  return digits;
}

/**
 * Serialize LE digit array to canonical MSB string.
 * Uppercase, no prefix, no leading zeros except "0".
 */
export function serializeLEtoMSB(digitsLE: DigitsLE, _base: Base): DigitsMSB {
  if (digitsLE.length === 0) return '0';

  // Find last non-zero digit (MSB end in LE = highest index)
  let end = digitsLE.length - 1;
  while (end > 0 && digitsLE[end] === 0) {
    end--;
  }

  let msb = '';
  for (let i = end; i >= 0; i--) {
    msb += SYMBOLS[digitsLE[i]!];
  }
  return msb || '0';
}

/**
 * Encode URL state payload.
 */
export function encodeURLState(base: Base, rootDigits: DigitsMSB): string {
  const payload = { v: 1, b: base, r: rootDigits };
  return btoa(JSON.stringify(payload));
}

/**
 * Decode URL state payload.
 * Returns null on invalid/unknown versions (non-blocking).
 */
export function decodeURLState(encoded: string): { base: Base; rootDigits: DigitsMSB } | null {
  try {
    const json = atob(encoded);
    const payload = JSON.parse(json) as Record<string, unknown>;

    if (payload['v'] !== 1) {
      console.warn(`Unknown URL state version: ${String(payload['v'])}`);
      return null;
    }

    const base = payload['b'];
    const rootDigits = payload['r'];

    if (typeof base !== 'number' || base < 2 || base > 36) return null;
    if (typeof rootDigits !== 'string' || rootDigits.length === 0) return null;

    // Validate digits against base
    try {
      parseMSBtoLE(rootDigits, base);
    } catch {
      return null;
    }

    return { base, rootDigits };
  } catch {
    return null;
  }
}
