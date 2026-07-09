// Mnestra memory interface — TypeScript binding (mirrors spec/mnestra.idl).
// A substrate driver implements `Memory`; application code is substrate-agnostic.

export type Address = string;

export interface Pattern {
  text: string;
  summary: string;
  value?: Uint8Array;
  meta?: Record<string, string>;
}

export interface Recall { address: Address; score: number; }

export interface GlobalView {
  title: string;
  outline: string[];
  constraints: string[];
  recalled: Recall[];
  filled: number;
  total: number;
}

export enum Substrate { Classical, Photonic, QuantumAfc }

export interface Memory {
  write(addr: string, p: Pattern): Address;
  read(addr: string): Pattern | null;
  query(cue: string, k: number): Recall[];
  reconstruct(): GlobalView;
}

/** Stable content address: BLAKE2b-128 of canonical-encoded payload (see ACF spec). */
export function contentAddress(_payload: string): Address {
  throw new Error("provided by a substrate driver");
}

export function open(_s: Substrate): Memory {
  throw new Error("provided by a substrate driver");
}
