/// <reference types="vite/client" />

declare module 'comlink' {
  export type Remote<T> = T;
  export function wrap<T>(endpoint: MessagePort | Worker): Remote<T>;
  export function expose(obj: unknown, endpoint?: MessagePort | Worker): void;
  export function proxy<T extends Function>(callback: T): T;
  export function transfer<T>(obj: T, transfers: Transferable[]): T;
}
