import { httpClient } from "./httpClient";

export type RiskEngineItem = {
  id: number;
  title: string;
  description?: string | null;
  level: "low" | "medium" | "high";
  status: "active" | "resolved";
};

export type RiskEngineAnalyzeResponse = {
  employee_id: number;
  created_or_updated_count: number;
  active_risks_count: number;
  active_risks: RiskEngineItem[];
};

export const riskEngineApi = {
  async analyzeEmployee(employeeId: number) {
    const response = await httpClient.post<RiskEngineAnalyzeResponse>(
      `/risk-engine/employees/${employeeId}/analyze`
    );

    return response.data;
  },
};
