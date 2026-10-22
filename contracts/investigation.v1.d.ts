export type RunStatus = 'PASS' | 'EXECUTED_PARTIAL' | 'INSUFFICIENT_DATA' | 'BLOCKED' | 'ERROR';
export type Variable = 'energy' | 'sleep_hours';
export type Coverage = { variable: Variable; unit: string; start: string; end: string; observed: number; eligible: number; source_record_ids: string[] };
export type Period = Coverage & { mean: number };
export type Series = { variable: Variable; unit: string; points: { local_date: string; value: number | null; source_record_id: string | null }[] };
export type Comparison = { variable: Variable; unit: string; method: 'arithmetic_mean_observed_days'; baseline: Period; comparison: Period; difference: number; source_record_ids: string[]; warning: 'Descriptive only; causality is not established.' };
export type Finding = { finding_id: string; kind: 'observation' | 'association' | 'hypothesis' | 'uncertainty' | 'abstention'; title: string; text: string; source_record_ids: string[]; analysis_evidence_id?: string | null };
export type ToolTrace = { trace_id: string; tool: string; status: 'PASS' | 'BLOCKED' | 'ERROR'; detail: string; source_record_ids: string[] };
export type SponsorProof = { sponsor: 'zetaris' | 'meterless_engine' | 'meterless_runtime' | 'nemotron'; status: 'NOT_CONNECTED' | 'VERIFIED' | 'FAILED'; trace_id: string | null };
export type InvestigationV1 = {
  contract_version: 'investigation.v1'; run_id: string; parent_run_id: string | null;
  dataset_id: string; mode: 'SYNTHETIC_LOCAL_ONLY' | 'LIVE_SYNTHETIC_ZETARIS';
  scenario: 'normal' | 'insufficient' | 'tool_error'; status: RunStatus; reason_code: string | null;
  question: string; timezone: 'Europe/Madrid'; window: { start: string; end: string }; summary: string;
  coverage: Coverage[]; series: Series[]; comparison: Comparison | null;
  findings: Finding[]; tool_trace: ToolTrace[]; sponsor_proofs: SponsorProof[];
};
