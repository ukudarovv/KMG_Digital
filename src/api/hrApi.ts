import { httpClient } from "./httpClient";

export type HREmployeeDashboardItem = {
  id: number;
  full_name: string;
  position?: string | null;
  department?: string | null;
  manager?: string | null;
  start_date: string;

  current_stage: "Знакомство" | "Вовлечение" | "Адаптация" | "Закрепление";
  progress: number;

  completed_tasks: number;
  total_tasks: number;

  nps: number | null;
  sentiment: "positive" | "neutral" | "negative";
  risk_level: "low" | "medium" | "high";
  last_activity: string;
};

export type HRDashboardSummary = {
  total_employees: number;
  average_progress: number;
  high_risk_count: number;
  active_today_count: number;
};

export type HRDashboardResponse = {
  summary: HRDashboardSummary;
  employees: HREmployeeDashboardItem[];
};

export type HRRouteStep = {
  key: string;
  title: string;
  description: string;
  status: "done" | "active" | "pending";
};

export type HRSentimentWeek = {
  week: string;
  positive: number;
  neutral: number;
  negative: number;
};

export type HRRiskFlagItem = {
  id: number;
  title: string;
  description: string;
  level: "low" | "medium" | "high";
  status: "active" | "resolved";
};

export type HRRecommendationItem = {
  id: number;
  title: string;
  description: string;
  priority: "low" | "medium" | "high";
};

export type HRMeetingItem = {
  id: number;
  title: string;
  date: string;
  time: string;
  status: string;
  description: string;
};

export type HRSmartGoalItem = {
  id: number;
  title: string;
  description: string;
  deadline: string;
  status: string;
};

export type HRLearningModuleItem = {
  id: number;
  title: string;
  deadline: string;
  progress: number;
  status: string;
};

export type HREmployeeDetailResponse = {
  employee: HREmployeeDashboardItem;
  route_steps: HRRouteStep[];
  sentiment_weeks: HRSentimentWeek[];
  risk_flags: HRRiskFlagItem[];
  recommendations: HRRecommendationItem[];
  meetings: HRMeetingItem[];
  smart_goals: HRSmartGoalItem[];
  learning_modules: HRLearningModuleItem[];
  hr_summary: string;
  privacy_note: string;
};

export const hrApi = {
  async getDashboard() {
    const response = await httpClient.get<HRDashboardResponse>("/hr/employees");
    return response.data;
  },

  async getEmployeeById(employeeId: number) {
    const response = await httpClient.get<HREmployeeDashboardItem>(
      `/hr/employees/${employeeId}`
    );

    return response.data;
  },

  async getEmployeeDetail(employeeId: number) {
    const response = await httpClient.get<HREmployeeDetailResponse>(
      `/hr/employees/${employeeId}/detail`
    );

    return response.data;
  },

  async getEmployeeAnalytics(employeeId: number) {
    const employee = await hrApi.getEmployeeById(employeeId);

    if (!employee) {
      return null;
    }

    return {
      employee,
      sentimentWeeks: [],
      riskFlags: [],
      developmentRecommendations: [],
      hrReportSummary: null,
      oneToOneMeetings: [],
      smartGoals: [],
      learningModules: [],
    };
  },
};
