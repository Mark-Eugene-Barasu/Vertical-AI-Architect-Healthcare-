import axios from "axios";
import { fetchAuthSession } from "aws-amplify/auth";
import type {
  ClinicalNote,
  NoteListResponse,
  DrugCheckResult,
  MedicationExtractResult,
  DecisionSupportResult,
  TimelineResponse,
  Metrics,
  TrendResponse,
  AlertSummary,
  ComplianceStatus,
  AuditReport,
} from "../types";

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL });

api.interceptors.request.use(async (config) => {
  try {
    const session = await fetchAuthSession();
    const token = session.tokens?.idToken?.toString();
    if (token) config.headers.Authorization = `Bearer ${token}`;
  } catch {
    // User not authenticated -- let request proceed without auth header
  }
  return config;
});

// ── Clinical Notes ───────────────────────────────────────────────────────────
export const notesApi = {
  generate: (transcript: string, patient_id: string) =>
    api.post<ClinicalNote>("/api/notes/generate", { transcript, patient_id }),

  transcribe: (audio: File, patient_id: string) => {
    const form = new FormData();
    form.append("audio", audio);
    form.append("patient_id", patient_id);
    return api.post<ClinicalNote>("/api/notes/transcribe", form);
  },

  list: (patient_id: string) =>
    api.get<NoteListResponse>(`/api/notes/${patient_id}`),

  get: (patient_id: string, note_id: string) =>
    api.get<ClinicalNote>(`/api/notes/${patient_id}/${note_id}`),

  update: (patient_id: string, note_id: string, clinical_note: object) =>
    api.put(`/api/notes/${patient_id}/${note_id}`, { clinical_note }),
};

// ── Drug Interactions ────────────────────────────────────────────────────────
export const drugsApi = {
  check: (medications: string[], clinical_text?: string) =>
    api.post<DrugCheckResult>("/api/drugs/check", { medications, clinical_text }),

  extract: (text: string) =>
    api.post<MedicationExtractResult>("/api/drugs/extract", { text }),
};

// ── Decision Support ─────────────────────────────────────────────────────────
export const decisionApi = {
  suggest: (patient_context: string, query: string) =>
    api.post<DecisionSupportResult>("/api/decision/suggest", { patient_context, query }),
};

// ── Patient Timeline ─────────────────────────────────────────────────────────
export const timelineApi = {
  get: (patient_id: string) =>
    api.get<TimelineResponse>(`/api/timeline/${patient_id}`),

  getByType: (patient_id: string, event_type: string) =>
    api.get<TimelineResponse>(`/api/timeline/${patient_id}/${event_type}`),

  addEvent: (patient_id: string, event_type: string, title: string, data: object) =>
    api.post(`/api/timeline/${patient_id}/event`, { event_type, title, data }),
};

// ── Analytics ────────────────────────────────────────────────────────────────
export const analyticsApi = {
  metrics: () =>
    api.get<Metrics>("/api/analytics/metrics"),

  trend: (months?: number) =>
    api.get<TrendResponse>("/api/analytics/trend", { params: months ? { months } : undefined }),

  alerts: () =>
    api.get<AlertSummary>("/api/analytics/alerts"),
};

// ── Compliance ───────────────────────────────────────────────────────────────
export const complianceApi = {
  status: () =>
    api.get<ComplianceStatus>("/api/compliance/compliance-status"),

  auditReport: (days: number = 30) =>
    api.get<AuditReport>(`/api/compliance/audit-report`, { params: { days } }),
};

export default api;
