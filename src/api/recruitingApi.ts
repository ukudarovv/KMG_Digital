import { httpClient } from "./httpClient";
import type { Employee } from "./employeeApi";

export type DepartmentMatch = {
  id: number;
  department_id: number;
  department_code: string;
  department_name: string;
  score: number;
  reasoning?: string | null;
  rank: number;
  decision?: "pass" | "review" | "reject" | null;
};

export type ResumeAnalysis = {
  id: number;
  parsed_json?: {
    full_name?: string | null;
    email?: string | null;
    phone?: string | null;
    skills?: string[];
    experience_years?: number | null;
    education?: string | null;
    positions?: string[];
    summary?: string | null;
  } | null;
  llm_summary?: string | null;
  created_at: string;
  matches: DepartmentMatch[];
};

export type Candidate = {
  id: number;
  full_name: string;
  email?: string | null;
  phone?: string | null;
  source: string;
  status: "new" | "analyzed" | "hired" | "rejected";
  consent_given: boolean;
  confirmed_department_id?: number | null;
  confirmed_department_name?: string | null;
  created_at: string;
  top_match_department?: string | null;
  top_match_score?: number | null;
};

export type CandidateDetail = Candidate & {
  resume_file_name?: string | null;
  extracted_text_preview?: string | null;
  analysis?: ResumeAnalysis | null;
  hired_employee_id?: number | null;
};

export type RecruitingSettings = {
  prompt_template?: string | null;
  min_score: number;
  top_n: number;
  llm_enabled: boolean;
  screening_service_url?: string | null;
  screening_service_available?: boolean;
};

export const recruitingApi = {
  async analyzeResume(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    const response = await httpClient.post<{
      candidate: CandidateDetail;
      llm_used: boolean;
    }>("/hr/recruiting/analyze-resume", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  },

  async getCandidates() {
    const response = await httpClient.get<Candidate[]>(
      "/hr/recruiting/candidates"
    );
    return response.data;
  },

  async getCandidate(candidateId: number) {
    const response = await httpClient.get<CandidateDetail>(
      `/hr/recruiting/candidates/${candidateId}`
    );
    return response.data;
  },

  async confirmDepartment(candidateId: number, departmentId: number) {
    const response = await httpClient.post<CandidateDetail>(
      `/hr/recruiting/candidates/${candidateId}/confirm-department`,
      { department_id: departmentId }
    );
    return response.data;
  },

  async hire(
    candidateId: number,
    payload: {
      position?: string;
      manager_name?: string;
      start_date?: string;
      bitrix_user_id?: number | null;
    }
  ) {
    const response = await httpClient.post<Employee>(
      `/hr/recruiting/candidates/${candidateId}/hire`,
      payload
    );
    return response.data;
  },

  async getSettings() {
    const response = await httpClient.get<RecruitingSettings>(
      "/hr/recruiting/settings"
    );
    return response.data;
  },

  async updateSettings(payload: Partial<RecruitingSettings>) {
    const response = await httpClient.patch<RecruitingSettings>(
      "/hr/recruiting/settings",
      payload
    );
    return response.data;
  },
};
