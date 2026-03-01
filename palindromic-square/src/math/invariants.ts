/**
 * Invariant checks and validation utilities for the math engine.
 * Used by tests and runtime assertions.
 */
import type { Base, DigitsLE, CarryTraceEntry } from './types';

/**
 * Validate that all digits are in valid range for the base.
 */
export function validateDigits(digitsLE: DigitsLE, base: Base): boolean {
  return digitsLE.every(d => d >= 0 && d < base);
}

/**
 * Validate base is in supported range.
 */
export function validateBase(base: Base): boolean {
  return Number.isInteger(base) && base >= 2 && base <= 36;
}

/**
 * Validate carry trace consistency.
 * digitOut == (rawCoefficient + incomingCarry) mod base
 * outgoingCarry == floor((rawCoefficient + incomingCarry) / base)
 */
export function validateCarryTrace(trace: CarryTraceEntry[], base: Base): boolean {
  const b = BigInt(base);
  for (const entry of trace) {
    const t = entry.rawCoefficient + entry.incomingCarry;
    const expectedDigit = Number(t % b);
    const expectedCarry = t / b;

    if (entry.digitOut !== expectedDigit) return false;
    if (entry.outgoingCarry !== expectedCarry) return false;
  }
  return true;
}

/**
 * Validate that carry trace chain is consistent (outgoing carry of position k = incoming carry of position k+1).
 */
export function validateCarryChain(trace: CarryTraceEntry[]): boolean {
  for (let i = 0; i < trace.length - 1; i++) {
    if (trace[i]!.outgoingCarry !== trace[i + 1]!.incomingCarry) {
      return false;
    }
  }
  // First position should have incoming carry of 0
  if (trace.length > 0 && trace[0]!.incomingCarry !== 0n) {
    return false;
  }
  return true;
}

/**
 * Validate all normalized digits are in range 0..b-1.
 */
export function validateNormalizedDigits(digitsLE: DigitsLE, base: Base): boolean {
  return digitsLE.every(d => d >= 0 && d < base);
}

/**
 * Serialize an object to canonical JSON with lexicographically sorted keys
 * and no insignificant whitespace, per TECH_SPEC Section 11.2.
 * Recursively sorts keys at all levels.
 */
export function canonicalJSON(obj: unknown): string {
  if (obj === null || obj === undefined) return JSON.stringify(obj);
  if (typeof obj !== 'object') return JSON.stringify(obj);
  if (Array.isArray(obj)) {
    return '[' + obj.map(canonicalJSON).join(',') + ']';
  }
  const record = obj as Record<string, unknown>;
  const sortedKeys = Object.keys(record).sort();
  const pairs = sortedKeys.map(
    (key) => JSON.stringify(key) + ':' + canonicalJSON(record[key])
  );
  return '{' + pairs.join(',') + '}';
}

/**
 * Compute SHA-256 determinism digest per TECH_SPEC Section 11.2.
 * Fields: schemaVersion, base, rootDigits, normalizedSquareDigits, peak, isPalindrome
 * Serialized as canonical JSON with lexicographically sorted keys, no whitespace.
 * Digest output: lowercase hex string.
 */
export async function computeDeterminismDigest(
  base: Base,
  rootDigitsMSB: string,
  normalizedSquareDigitsMSB: string,
  peak: bigint,
  isPalindrome: boolean
): Promise<string> {
  const obj = {
    base,
    isPalindrome,
    normalizedSquareDigits: normalizedSquareDigitsMSB,
    peak: peak.toString(),
    rootDigits: rootDigitsMSB,
    schemaVersion: 'v1'
  };

  // Explicit key-sorted canonical JSON serialization
  const json = canonicalJSON(obj);
  const encoder = new TextEncoder();
  const data = encoder.encode(json);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}
