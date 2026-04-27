// ── SOAP Note ────────────────────────────────────────────────────────────────
export interface SOAPNote {
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
  follow_up: string;
}

// ── Clinical Notes ───────────────────────────────────────────────────────────
export interface ClinicalNote {
  patient_id: string;
  note_id: string;
  transcript: string;
  clinical_note: SOAPNote;
  clinician_id: string;
  created_at: string;
  updated_at?: string;
  status: "active" | "archived";
}

export interface NoteListResponse {
  patient_id: string;
  notes: ClinicalNote[];
}

// ── Drug Interactions ────────────────────────────────────────────────────────
export interface DrugInteraction {
  severity: "HIGH" | "MEDIUM" | "LOW";
  drugs: string[];
  warning: string;
}

export interface DrugCheckResult {
  medications: string[];
  interactions: DrugInteraction[];
}

export interface MedicationExtractResult {
  medications: string[];
}

// ── Decision Support ─────────────────────────────────────────────────────────
export interface DecisionSupportResult {
  query: string;
  suggestions: string;
}

// ── Patient Timeline ─────────────────────────────────────────────────────────
export interface TimelineEvent {
  timestamp: string;
  event_type: string;
  title: string;
  data: Record<string, unknown>;
  clinician_id: string;
}

export interface TimelineResponse {
  patient_id: string;
  timeline: TimelineEvent[];
}

// ── Analytics ────────────────────────────────────────────────────────────────
export interface Metrics {
  month: string;
  notes_generated: number;
  drug_checks_performed: number;
  decision_queries: number;
  transcriptions: number;
  estimated_time_saved_hours: number;
  estimated_errors_prevented: number;
}

export interface TrendPoint {
  month: string;
  notes: number;
  drug_checks: number;
  decision_queries: number;
}

export interface TrendResponse {
  trend: TrendPoint[];
}

export interface AlertSummary {
  total_alerts: number;
  critical: number;
  high: number;
  medium: number;
}

// ── Compliance ───────────────────────────────────────────────────────────────
export interface ComplianceCheck {
  status: "pass" | "fail";
  detail: string;
}

export interface ComplianceStatus {
  status: string;
  checks: Record<string, ComplianceCheck>;
}

export interface AuditReportPeriod {
  start: string;
  end: string;
}

export interface AuditEvent {
  event_name: string;
  user: string;
  event_time: string;
}

export interface AuditReport {
  report_id: string;
  period: AuditReportPeriod;
  summary: Record<string, number>;
  events: AuditEvent[];
}

// ── Alerts ───────────────────────────────────────────────────────────────────
export interface Alert {
  alert_type: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "INFO";
  patient_id: string;
  message: string;
  details: Record<string, unknown>;
  timestamp: string;
}

// ── Health ───────────────────────────────────────────────────────────────────
export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}
