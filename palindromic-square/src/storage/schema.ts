/**
 * Dexie database schema per TECH_SPEC Section 7.3.
 * Includes forward migration scaffolding for v2+ schema upgrades.
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

    // Version 2: Migration scaffolding for forward compatibility.
    // Same indexes (no structural change yet), but provides the
    // upgrade hook so existing v1 data is preserved and future
    // v2 additions can be implemented here.
    this.version(2).stores({
      projects: 'id, name, updatedAt, base',
      appMeta: 'key'
    }).upgrade((tx) => {
      // Ensure all existing projects retain their timestamps
      // and settings are valid JSON.
      return tx.table('projects').toCollection().modify((project: ProjectRecord) => {
        // Ensure createdAt is present (fill from updatedAt if missing)
        if (!project.createdAt) {
          project.createdAt = project.updatedAt || new Date().toISOString();
        }
        // Ensure settings is valid JSON
        if (!project.settings) {
          project.settings = JSON.stringify({ advancedMode: false, animatorSpeed: 1 });
        }
      });
    });
  }
}

export const db = new PeakGuardDB();
