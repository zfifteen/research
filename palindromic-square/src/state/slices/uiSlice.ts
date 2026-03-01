/**
 * UI slice — tabs, panels, animator controls, theme prefs, toast notifications.
 */
import type { StateCreator } from 'zustand';

export type ActiveTab = 'explorer' | 'builder' | 'animator' | 'guidance' | 'gallery' | 'exports' | 'data' | 'debug';
export type AnimatorState = 'stopped' | 'playing' | 'paused';

export interface ToastMessage {
  id: string;
  text: string;
  type: 'info' | 'warning' | 'error';
}

export interface UISlice {
  activeTab: ActiveTab;
  animatorState: AnimatorState;
  animatorStep: number;
  animatorSpeed: number;
  showDebugPanel: boolean;
  showAdvancedBuilder: boolean;
  sidebarOpen: boolean;
  toasts: ToastMessage[];

  setActiveTab: (tab: ActiveTab) => void;
  setAnimatorState: (state: AnimatorState) => void;
  setAnimatorStep: (step: number) => void;
  setAnimatorSpeed: (speed: number) => void;
  toggleDebugPanel: () => void;
  toggleAdvancedBuilder: () => void;
  toggleSidebar: () => void;
  addToast: (text: string, type: ToastMessage['type']) => void;
  dismissToast: (id: string) => void;
}

let toastCounter = 0;

export const createUISlice: StateCreator<UISlice, [], [], UISlice> = (set) => ({
  activeTab: 'explorer',
  animatorState: 'stopped',
  animatorStep: 0,
  animatorSpeed: 1,
  showDebugPanel: false,
  showAdvancedBuilder: false,
  sidebarOpen: true,
  toasts: [],

  setActiveTab: (tab) => set({ activeTab: tab }),
  setAnimatorState: (state) => set({ animatorState: state }),
  setAnimatorStep: (step) => set({ animatorStep: step }),
  setAnimatorSpeed: (speed) => set({ animatorSpeed: speed }),
  toggleDebugPanel: () => set((s) => ({ showDebugPanel: !s.showDebugPanel })),
  toggleAdvancedBuilder: () => set((s) => ({ showAdvancedBuilder: !s.showAdvancedBuilder })),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  addToast: (text, type) => {
    const id = `toast-${++toastCounter}`;
    set((s) => ({ toasts: [...s.toasts, { id, text, type }] }));
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
    }, 5000);
  },
  dismissToast: (id) =>
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }))
});
