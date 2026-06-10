import { httpClient } from "./httpClient";

export type MeetingStatus = "planned" | "completed" | "cancelled";

export type SmartGoalStatus =
  | "planned"
  | "in_progress"
  | "completed"
  | "needs_update";

export type LearningModuleStatus =
  | "not_started"
  | "in_progress"
  | "completed"
  | "overdue";

export type CreateMeetingPayload = {
  title: string;
  description?: string;
  meeting_date: string;
  meeting_time?: string;
  status: MeetingStatus;
};

export type CreateSmartGoalPayload = {
  title: string;
  description?: string;
  deadline: string;
  status: SmartGoalStatus;
};

export type CreateLearningModulePayload = {
  title: string;
  deadline: string;
  progress: number;
  status: LearningModuleStatus;
};

export type AdaptationFeatureStatus = {
  f17_has_upcoming_meeting: boolean;
  f17_days_until_meeting: number | null;
  f18_prep_available: boolean;
  f19_has_goals: boolean;
  f20_interim_scheduled: boolean;
  f20_days_until_interim: number | null;
  f21_reflection_available: boolean;
  f22_needs_kpi_update: boolean;
  f23_incomplete_modules: number;
  f24_vnd_available: boolean;
};

export type AdaptationContext = {
  adaptation_day: number;
  one_to_one_prep: {
    requirement_code: string;
    topics: string[];
    suggested_questions: string[];
  };
  smart_goal_help: {
    requirement_code: string;
    clarifying_questions: string[];
    document_code: string;
  };
  reflection_dialog: {
    requirement_code: string;
    steps: Array<{ step: number; question: string; hint: string }>;
  };
  interim_assessment: {
    requirement_code: string;
    meeting_date: string | null;
    employee_prep: string[];
    manager_prep: string[];
    days_until: number | null;
  };
  feature_status: AdaptationFeatureStatus;
};

export const adaptationApi = {
  async createMeeting(employeeId: number, payload: CreateMeetingPayload) {
    const response = await httpClient.post(
      `/adaptation/employees/${employeeId}/meetings`,
      payload
    );

    return response.data;
  },

  async updateMeeting(meetingId: number, payload: Partial<CreateMeetingPayload>) {
    const response = await httpClient.patch(
      `/adaptation/meetings/${meetingId}`,
      payload
    );

    return response.data;
  },

  async deleteMeeting(meetingId: number) {
    const response = await httpClient.delete(`/adaptation/meetings/${meetingId}`);
    return response.data;
  },

  async createGoal(employeeId: number, payload: CreateSmartGoalPayload) {
    const response = await httpClient.post(
      `/adaptation/employees/${employeeId}/goals`,
      payload
    );

    return response.data;
  },

  async updateGoal(goalId: number, payload: Partial<CreateSmartGoalPayload>) {
    const response = await httpClient.patch(`/adaptation/goals/${goalId}`, payload);
    return response.data;
  },

  async deleteGoal(goalId: number) {
    const response = await httpClient.delete(`/adaptation/goals/${goalId}`);
    return response.data;
  },

  async createLearningModule(
    employeeId: number,
    payload: CreateLearningModulePayload
  ) {
    const response = await httpClient.post(
      `/adaptation/employees/${employeeId}/learning-modules`,
      payload
    );

    return response.data;
  },

  async updateLearningModule(
    moduleId: number,
    payload: Partial<CreateLearningModulePayload>
  ) {
    const response = await httpClient.patch(
      `/adaptation/learning-modules/${moduleId}`,
      payload
    );

    return response.data;
  },

  async deleteLearningModule(moduleId: number) {
    const response = await httpClient.delete(
      `/adaptation/learning-modules/${moduleId}`
    );

    return response.data;
  },

  async getMeetings(employeeId: number) {
    const response = await httpClient.get(
      `/adaptation/employees/${employeeId}/meetings`
    );

    return response.data;
  },

  async getGoals(employeeId: number) {
    const response = await httpClient.get(
      `/adaptation/employees/${employeeId}/goals`
    );

    return response.data;
  },

  async getLearningModules(employeeId: number) {
    const response = await httpClient.get(
      `/adaptation/employees/${employeeId}/learning-modules`
    );

    return response.data;
  },

  async getContext(employeeId: number): Promise<AdaptationContext> {
    const response = await httpClient.get(`/adaptation/context/${employeeId}`);
    return response.data;
  },

  async setupDemo(employeeId: number) {
    const response = await httpClient.post(
      `/adaptation/demo-setup/${employeeId}`
    );
    return response.data;
  },

  async triggerTouchpoints(employeeId: number) {
    const response = await httpClient.post(
      `/adaptation/touchpoints/${employeeId}`
    );
    return response.data;
  },
};
