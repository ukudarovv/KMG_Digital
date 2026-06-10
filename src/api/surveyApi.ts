import { httpClient } from "./httpClient";

export type SurveyType = "pulse_day_14" | "nps_day_30" | "final_nps";

export type SurveyCreatePayload = {
  survey_type: SurveyType;
  nps_score?: number | null;
  comment?: string | null;
  answers?: Record<string, unknown> | null;
};

export type SurveyRead = {
  id: number;
  employee_id: number;
  survey_type: SurveyType;
  nps_score?: number | null;
  comment?: string | null;
  answers?: Record<string, unknown> | null;
  created_at: string;
};

export type SurveySummary = {
  pulse_day_14_completed: boolean;
  nps_day_30_completed: boolean;
  final_nps_completed: boolean;
  latest_nps?: number | null;
};

export const surveyApi = {
  async getEmployeeSurveys(employeeId: number) {
    const response = await httpClient.get<SurveyRead[]>(
      `/surveys/employees/${employeeId}`
    );

    return response.data;
  },

  async getSummary(employeeId: number) {
    const response = await httpClient.get<SurveySummary>(
      `/surveys/employees/${employeeId}/summary`
    );

    return response.data;
  },

  async createSurvey(employeeId: number, payload: SurveyCreatePayload) {
    const response = await httpClient.post<SurveyRead>(
      `/surveys/employees/${employeeId}`,
      payload
    );

    return response.data;
  },

  async deleteSurvey(surveyId: number) {
    const response = await httpClient.delete(`/surveys/${surveyId}`);
    return response.data;
  },

  async resetEngagementSurveys(employeeId: number) {
    const response = await httpClient.delete(
      `/surveys/employees/${employeeId}/demo-reset`
    );
    return response.data;
  },
};
