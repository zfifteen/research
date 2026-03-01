/**
 * Project slice — active project input, metadata, dirty state.
 */
import type { StateCreator } from 'zustand';
import type { Base, DigitsMSB, ProjectSettings, ProjectData } from '../../math/types';

export interface ProjectSlice {
  // Active project state
  activeProjectId: string | null;
  projectName: string;
  base: Base;
  rootDigits: DigitsMSB;
  settings: ProjectSettings;
  isDirty: boolean;
  projects: ProjectData[];

  // Actions
  setBase: (base: Base) => void;
  setRootDigits: (digits: DigitsMSB) => void;
  setProjectName: (name: string) => void;
  setSettings: (settings: Partial<ProjectSettings>) => void;
  setActiveProject: (id: string | null) => void;
  setProjects: (projects: ProjectData[]) => void;
  markClean: () => void;
  resetProject: () => void;
}

export const createProjectSlice: StateCreator<ProjectSlice, [], [], ProjectSlice> = (set) => ({
  activeProjectId: null,
  projectName: 'Untitled Project',
  base: 10,
  rootDigits: '111111111',
  settings: { advancedMode: false, animatorSpeed: 1 },
  isDirty: false,
  projects: [],

  setBase: (base) => set({ base, isDirty: true }),
  setRootDigits: (digits) => set({ rootDigits: digits, isDirty: true }),
  setProjectName: (name) => set({ projectName: name, isDirty: true }),
  setSettings: (settings) =>
    set((state) => ({
      settings: { ...state.settings, ...settings },
      isDirty: true
    })),
  setActiveProject: (id) => set({ activeProjectId: id }),
  setProjects: (projects) => set({ projects }),
  markClean: () => set({ isDirty: false }),
  resetProject: () =>
    set({
      activeProjectId: null,
      projectName: 'Untitled Project',
      base: 10,
      rootDigits: '111111111',
      settings: { advancedMode: false, animatorSpeed: 1 },
      isDirty: false
    })
});
