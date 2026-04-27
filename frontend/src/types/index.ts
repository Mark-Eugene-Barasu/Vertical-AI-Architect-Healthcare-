export interface SOAPNote {
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
  follow_up: string;
}

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

export interface DrugInteraction {
  severity: "HIGH" | "MEDIUM" | "LOW";
  drugs: string[];
  warning: string;
}

export interface DrugCheckResult {
  medications: string[];
  interactions: DrugInteraction[];
}

export interface DecisionSupportResult {
  query: string;
  suggestions: string;
}
