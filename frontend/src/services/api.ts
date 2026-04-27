import axios from "axios";
import { fetchAuthSession } from "aws-amplify/auth";
import type { ClinicalNote, DrugCheckResult, DecisionSupportResult } from "../types";

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL });

api.interceptors.request.use(async (config) => {
  const session = await fetchAuthSession();
  const token = session.tokens?.idToken?.toString();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

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
    api.get<{ notes: ClinicalNote[] }>(`/api/notes/${patient_id}`),

  get: (patient_id: string, note_id: string) =>
    api.get<ClinicalNote>(`/api/notes/${patient_id}/${note_id}`),

  update: (patient_id: string, note_id: string, clinical_note: object) =>
    api.put(`/api/notes/${patient_id}/${note_id}`, { clinical_note }),
};

export const drugsApi = {
  check: (medications: string[], clinical_text?: string) =>
    api.post<DrugCheckResult>("/api/drugs/check", { medications, clinical_text }),

  extract: (text: string) =>
    api.post<{ medications: string[] }>("/api/drugs/extract", { text }),
};

export const decisionApi = {
  suggest: (patient_context: string, query: string) =>
    api.post<DecisionSupportResult>("/api/decision/suggest", { patient_context, query }),
};
