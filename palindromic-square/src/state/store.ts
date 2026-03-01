/**
 * Zustand store combining all slices.
 */
import { create } from 'zustand';
import { createProjectSlice, type ProjectSlice } from './slices/projectSlice';
import { createComputeSlice, type ComputeSlice } from './slices/computeSlice';
import { createUISlice, type UISlice } from './slices/uiSlice';
import { createProfileSlice, type ProfileSlice } from './slices/profileSlice';

export type AppStore = ProjectSlice & ComputeSlice & UISlice & ProfileSlice;

export const useStore = create<AppStore>()((...a) => ({
  ...createProjectSlice(...a),
  ...createComputeSlice(...a),
  ...createUISlice(...a),
  ...createProfileSlice(...a)
}));
