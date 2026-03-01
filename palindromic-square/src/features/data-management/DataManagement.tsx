/**
 * Data Management panel — project CRUD, clear all, cache refresh.
 * TECH_SPEC Sections 4.6 and 10
 */
import React, { useCallback, useEffect, useState } from 'react';
import { useStore } from '../../state/store';
import { repository } from '../../storage/repository';
import type { ProjectData } from '../../math/types';
import { v4 as uuid } from 'uuid';

export function DataManagement(): React.ReactElement {
  const projects = useStore((s) => s.projects);
  const setProjects = useStore((s) => s.setProjects);
  const activeProjectId = useStore((s) => s.activeProjectId);
  const setActiveProject = useStore((s) => s.setActiveProject);
  const setBase = useStore((s) => s.setBase);
  const setRootDigits = useStore((s) => s.setRootDigits);
  const setProjectName = useStore((s) => s.setProjectName);
  const base = useStore((s) => s.base);
  const rootDigits = useStore((s) => s.rootDigits);
  const projectName = useStore((s) => s.projectName);
  const settings = useStore((s) => s.settings);
  const markClean = useStore((s) => s.markClean);

  const [recoveryStatus, setRecoveryStatus] = useState<string | null>(null);

  // Load projects on mount
  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    const loaded = await repository.getAllProjects();
    setProjects(loaded);
  };

  const handleSaveProject = useCallback(async () => {
    const now = new Date().toISOString();
    const project: ProjectData = {
      id: activeProjectId || uuid(),
      name: projectName,
      createdAt: activeProjectId ? (projects.find(p => p.id === activeProjectId)?.createdAt ?? now) : now,
      updatedAt: now,
      base,
      rootDigits,
      settings,
      cachedArtifacts: null
    };
    await repository.saveProject(project);
    setActiveProject(project.id);
    markClean();
    await loadProjects();
  }, [activeProjectId, projectName, base, rootDigits, settings, projects, setActiveProject, markClean, setProjects]);

  const handleLoadProject = useCallback(async (id: string) => {
    const project = await repository.getProject(id);
    if (!project) return;
    setActiveProject(project.id);
    setBase(project.base);
    setRootDigits(project.rootDigits);
    setProjectName(project.name);
    markClean();
  }, [setActiveProject, setBase, setRootDigits, setProjectName, markClean]);

  const handleDeleteProject = useCallback(async (id: string) => {
    if (!confirm('Delete this project?')) return;
    await repository.deleteProject(id);
    if (activeProjectId === id) {
      setActiveProject(null);
    }
    await loadProjects();
  }, [activeProjectId, setActiveProject]);

  const handleClearAll = useCallback(async () => {
    if (!confirm('Delete ALL local data? This cannot be undone.')) return;
    await repository.clearAll();
    setActiveProject(null);
    setProjects([]);
  }, [setActiveProject, setProjects]);

  const handleRefreshCache = useCallback(async () => {
    if (!confirm('Clear offline cache and reload? Your saved projects will be preserved.')) return;
    if ('serviceWorker' in navigator) {
      const registrations = await navigator.serviceWorker.getRegistrations();
      for (const reg of registrations) {
        await reg.unregister();
      }
    }
    if ('caches' in window) {
      const names = await caches.keys();
      for (const name of names) {
        await caches.delete(name);
      }
    }
    window.location.reload();
  }, []);

  const handleRecovery = useCallback(async () => {
    const result = await repository.attemptRecovery();
    setRecoveryStatus(result.message);
    if (result.recovered) {
      await loadProjects();
    }
  }, []);

  return (
    <div className="panel data-panel">
      <h2>Data Management</h2>

      <div className="project-actions">
        <button className="btn btn-primary" onClick={handleSaveProject}>
          Save Current Project
        </button>
      </div>

      <h3>Saved Projects</h3>
      {projects.length === 0 ? (
        <p className="empty-state">No saved projects yet.</p>
      ) : (
        <div className="project-list">
          {projects.map((project) => (
            <div
              key={project.id}
              className={`project-item ${project.id === activeProjectId ? 'active' : ''}`}
            >
              <div className="project-info">
                <strong>{project.name}</strong>
                <span className="project-meta">
                  Base {project.base} · {project.rootDigits} · {new Date(project.updatedAt).toLocaleDateString()}
                </span>
              </div>
              <div className="project-buttons">
                <button className="btn btn-small" onClick={() => handleLoadProject(project.id)}>
                  Load
                </button>
                <button
                  className="btn btn-small btn-danger"
                  onClick={() => handleDeleteProject(project.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <h3>Maintenance</h3>
      <div className="maintenance-actions">
        <button className="btn btn-warning" onClick={handleClearAll}>
          Clear All Local Data
        </button>
        <button className="btn btn-warning" onClick={handleRefreshCache}>
          Refresh App (clear offline cache)
        </button>
        <button className="btn" onClick={handleRecovery}>
          Attempt Data Recovery
        </button>
      </div>

      {recoveryStatus && (
        <div className="recovery-status">
          <p>{recoveryStatus}</p>
        </div>
      )}
    </div>
  );
}
