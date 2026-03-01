/**
 * Storage repository — CRUD operations for projects and app metadata.
 */
import { db, type ProjectRecord } from './schema';
import type { ProjectData, ProjectSettings, CachedArtifacts } from '../math/types';

/**
 * Convert DB record to ProjectData.
 */
function toProjectData(rec: ProjectRecord): ProjectData {
  return {
    id: rec.id,
    name: rec.name,
    createdAt: rec.createdAt,
    updatedAt: rec.updatedAt,
    base: rec.base,
    rootDigits: rec.rootDigits,
    settings: JSON.parse(rec.settings) as ProjectSettings,
    cachedArtifacts: rec.cachedArtifacts ? JSON.parse(rec.cachedArtifacts) as CachedArtifacts : null
  };
}

/**
 * Convert ProjectData to DB record.
 */
function toRecord(data: ProjectData): ProjectRecord {
  return {
    id: data.id,
    name: data.name,
    createdAt: data.createdAt,
    updatedAt: data.updatedAt,
    base: data.base,
    rootDigits: data.rootDigits,
    settings: JSON.stringify(data.settings),
    cachedArtifacts: data.cachedArtifacts ? JSON.stringify(data.cachedArtifacts) : null
  };
}

export const repository = {
  async getAllProjects(): Promise<ProjectData[]> {
    try {
      const records = await db.projects.orderBy('updatedAt').reverse().toArray();
      return records.map(toProjectData);
    } catch (e) {
      console.error('Failed to load projects:', e);
      return [];
    }
  },

  async getProject(id: string): Promise<ProjectData | null> {
    try {
      const rec = await db.projects.get(id);
      return rec ? toProjectData(rec) : null;
    } catch {
      return null;
    }
  },

  async saveProject(data: ProjectData): Promise<void> {
    await db.projects.put(toRecord(data));
  },

  async deleteProject(id: string): Promise<void> {
    await db.projects.delete(id);
  },

  async clearAllProjects(): Promise<void> {
    await db.projects.clear();
  },

  async getMeta(key: string): Promise<string | null> {
    try {
      const rec = await db.appMeta.get(key);
      return rec?.value ?? null;
    } catch {
      return null;
    }
  },

  async setMeta(key: string, value: string): Promise<void> {
    await db.appMeta.put({ key, value });
  },

  async isFirstRun(): Promise<boolean> {
    const val = await this.getMeta('firstRunComplete');
    return val !== 'true';
  },

  async markFirstRunComplete(): Promise<void> {
    await this.setMeta('firstRunComplete', 'true');
  },

  async clearAll(): Promise<void> {
    await db.projects.clear();
    await db.appMeta.clear();
  },

  /**
   * Try to recover from corrupted database.
   */
  async attemptRecovery(): Promise<{ recovered: boolean; message: string }> {
    try {
      // Try to open and read
      await db.projects.count();
      return { recovered: true, message: 'Database is healthy' };
    } catch (_e) {
      try {
        // Delete and recreate
        await db.delete();
        await db.open();
        return { recovered: true, message: 'Database was corrupted and has been reset' };
      } catch (e2) {
        return { recovered: false, message: `Recovery failed: ${String(e2)}` };
      }
    }
  }
};
