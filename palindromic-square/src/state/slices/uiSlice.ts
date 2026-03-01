/**
 * UI slice — tabs, panels, animator controls, theme prefs.
 */
import type { StateCreator } from 'zustand';

export type ActiveTab = 'explorer' | 'builder' | 'animator' | 'guidance' | 'gallery' | 'exports' | 'data' | 'debug';
export type AnimatorState = 'stopped' | 'playing' | 'paused';

export interface UISlice {
  activeTab: ActiveTab;
  animatorState: AnimatorState;
  animatorStep: number;
  animatorSpeed: number;
  showDebugPanel: boolean;
  showAdvancedBuilder: boolean;
  sidebarOpen: boolean;

  setActiveTab: (tab: ActiveTab) => void;
  setAnimatorState: (state: AnimatorState) => void;
  setAnimatorStep: (step: number) => void;
  setAnimatorSpeed: (speed: number) => void;
  toggleDebugPanel: () => void;
  toggleAdvancedBuilder: () => void;
  toggleSidebar: () => void;
}

export const createUISlice: StateCreator<UISlice, [], [], UISlice> = (set) => ({
  activeTab: 'explorer',
  animatorState: 'stopped',
  animatorStep: 0,
  animatorSpeed: 1,
  showDebugPanel: false,
  showAdvancedBuilder: false,
  sidebarOpen: true,

  setActiveTab: (tab) => set({ activeTab: tab }),
  setAnimatorState: (state) => set({ animatorState: state }),
  setAnimatorStep: (step) => set({ animatorStep: step }),
  setAnimatorSpeed: (speed) => set({ animatorSpeed: speed }),
  toggleDebugPanel: () => set((s) => ({ showDebugPanel: !s.showDebugPanel })),
  toggleAdvancedBuilder: () => set((s) => ({ showAdvancedBuilder: !s.showAdvancedBuilder })),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen }))
});
