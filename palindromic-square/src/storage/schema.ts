/**
 * Dexie database schema per TECH_SPEC Section 7.3.
 */
import Dexie, { type EntityTable } from 'dexie';

export interface ProjectRecord {
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
  base: number;
  rootDigits: string;
  settings: string; // JSON serialized
  cachedArtifacts: string | null; // JSON serialized
}

export interface AppMetaRecord {
  key: string;
  value: string;
}

export class PeakGuardDB extends Dexie {
  projects!: EntityTable<ProjectRecord, 'id'>;
  appMeta!: EntityTable<AppMetaRecord, 'key'>;

  constructor() {
    super('PeakGuardDB');

    // Version 1: Initial schema
    this.version(1).stores({
      projects: 'id, name, updatedAt, base',
      appMeta: 'key'
    });
  }
}

export const db = new PeakGuardDB();
