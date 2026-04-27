import axios from "axios";
import { fetchAuthSession } from "aws-amplify/auth";

const API_URL = process.env.EXPO_PUBLIC_API_URL;

const api = axios.create({ baseURL: API_URL });

api.interceptors.request.use(async (config) => {
  const session = await fetchAuthSession();
  const token = session.tokens?.idToken?.toString();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const mobileApi = {
  generateNote: (transcript: string, patientId: string) =>
    api.post("/api/notes/generate", { transcript, patient_id: patientId }),

  checkDrugs: (clinicalText: string, patientId: string) =>
    api.post("/api/drugs/check", { clinical_text: clinicalText, patient_id: patientId }),

  getTimeline: (patientId: string) =>
    api.get(`/api/timeline/${patientId}`),

  getDecisionSupport: (context: string, query: string) =>
    api.post("/api/decision/suggest", { patient_context: context, query }),
};
