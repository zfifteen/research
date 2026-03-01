/**
 * Built-in gallery of example families per TECH_SPEC Section 4.5.
 * Includes canonical examples from MATH.md.
 */
import type { GalleryEntry } from '../../math/types';

export const galleryEntries: GalleryEntry[] = [
  // Base 10 canonical examples (MATH.md test vectors)
  {
    id: 'base10-repunit-9',
    name: 'Base 10 Repunit (n=9) — Pre-cliff',
    description: '111111111² = 12345678987654321. The last palindromic repunit square in base 10. Peak = 9 < 10.',
    base: 10,
    rootDigits: '111111111',
    family: 'repunit',
    tags: ['canonical', 'pre-cliff', 'palindrome']
  },
  {
    id: 'base10-repunit-10',
    name: 'Base 10 Repunit (n=10) — Post-cliff',
    description: '1111111111² = 1234567900987654321. Central accumulation (10) exceeds symbol capacity (9). Carries break palindrome.',
    base: 10,
    rootDigits: '1111111111',
    family: 'repunit',
    tags: ['canonical', 'post-cliff', 'broken']
  },
  // Base 2 special case (MATH.md test vectors)
  {
    id: 'base2-repunit-2',
    name: 'Base 2 Repunit (n=2) — Pre-cliff',
    description: '11² = 1001 in binary. Last palindromic binary repunit square.',
    base: 2,
    rootDigits: '11',
    family: 'repunit',
    tags: ['canonical', 'pre-cliff', 'palindrome', 'binary']
  },
  {
    id: 'base2-repunit-3',
    name: 'Base 2 Repunit (n=3) — Post-cliff',
    description: '111² = 110001 in binary. Palindrome breaks at n=3 in base 2.',
    base: 2,
    rootDigits: '111',
    family: 'repunit',
    tags: ['canonical', 'post-cliff', 'broken', 'binary']
  },
  // 10^k + 1 style patterns
  {
    id: 'base10-sparse-101',
    name: 'Sparse: 101 (base 10)',
    description: '101² = 10201. Sparse digit pattern with bounded peak growth.',
    base: 10,
    rootDigits: '101',
    family: 'sparse',
    tags: ['sparse', 'palindrome']
  },
  {
    id: 'base10-sparse-10001',
    name: 'Sparse: 10001 (base 10)',
    description: '10001² = 100020001. Widely separated 1s keep peak bounded.',
    base: 10,
    rootDigits: '10001',
    family: 'sparse',
    tags: ['sparse', 'palindrome']
  },
  {
    id: 'base10-sparse-1001001',
    name: 'Sparse: 1001001 (base 10)',
    description: '1001001² = 1002003002001. Three separated 1s, peak stays low.',
    base: 10,
    rootDigits: '1001001',
    family: 'sparse',
    tags: ['sparse', 'palindrome']
  },
  // Cross-base repunit examples
  {
    id: 'base3-repunit-2',
    name: 'Base 3 Repunit (n=2) — Pre-cliff',
    description: '11₃² = 121₃. Pre-cliff in base 3 (cliff at n=2).',
    base: 3,
    rootDigits: '11',
    family: 'repunit',
    tags: ['pre-cliff', 'palindrome']
  },
  {
    id: 'base3-repunit-3',
    name: 'Base 3 Repunit (n=3) — Post-cliff',
    description: '111₃² = 11001₃. Post-cliff in base 3.',
    base: 3,
    rootDigits: '111',
    family: 'repunit',
    tags: ['post-cliff', 'broken']
  },
  {
    id: 'base16-repunit-15',
    name: 'Base 16 Repunit (n=15) — Pre-cliff',
    description: 'Repunit of length 15 in hexadecimal. Last palindromic hex repunit square.',
    base: 16,
    rootDigits: '111111111111111',
    family: 'repunit',
    tags: ['pre-cliff', 'palindrome', 'hex']
  },
  {
    id: 'base5-repunit-4',
    name: 'Base 5 Repunit (n=4) — Pre-cliff',
    description: '1111₅² = 1234321₅. Pre-cliff in base 5.',
    base: 5,
    rootDigits: '1111',
    family: 'repunit',
    tags: ['pre-cliff', 'palindrome']
  },
  {
    id: 'base10-repunit-5',
    name: 'Base 10 Repunit (n=5)',
    description: '11111² = 123454321. Well within safe zone, palindromic.',
    base: 10,
    rootDigits: '11111',
    family: 'repunit',
    tags: ['pre-cliff', 'palindrome']
  }
];

/**
 * Get the default first-run gallery entry.
 */
export function getDefaultGalleryEntry(): GalleryEntry {
  return galleryEntries[0]!; // Base 10, n=9 — the canonical example
}
