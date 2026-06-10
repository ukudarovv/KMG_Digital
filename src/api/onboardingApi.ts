import { httpClient } from "./httpClient";

export type BackendTaskStatus =
  | "pending"
  | "in_progress"
  | "completed"
  | "overdue";

export type BackendDayOneTask = {
  id: number;
  employee_id: number;
  bitrix_task_id?: number | null;
  stage: "introduction" | "engagement" | "adaptation" | "retention";
  title: string;
  description?: string | null;
  deadline_at?: string | null;
  status: BackendTaskStatus;
  is_required: boolean;
  vnd_document_code?: string | null;
  external_link?: string | null;
  confirmation_required?: boolean;
  document_url?: string | null;
  requirement_code?: string | null;
  created_at: string;
  completed_at?: string | null;
};

export type LearningModule = {
  id: number;
  employee_id: number;
  title: string;
  deadline: string;
  progress: number;
  status: "not_started" | "in_progress" | "completed";
  created_at: string;
};

export type EngagementContext = {
  adaptation_day: number;
  corporate_channels: {
    requirement_code: string;
    title: string;
    description: string;
    channels: Array<{
      name: string;
      purpose: string;
      contact: string;
    }>;
    unlocked: boolean;
  } | null;
  learning_modules: LearningModule[];
  duchr_meeting: {
    requirement_code: string;
    title: string;
    description: string;
    meeting_day: number;
    suggested_questions: string[];
    unlocked: boolean;
  } | null;
  feature_status: {
    f10_completed: boolean;
    f11_completed: boolean;
    f12_unlocked: boolean;
    f13_has_courses: boolean;
    f14_completed: boolean;
    f15_unlocked: boolean;
    f16_completed: boolean;
  };
};

export type BackendNudge = {
  id: number;
  day_number: number;
  title: string;
  text: string;
  source: string;
  vnd_document_code?: string | null;
  is_active: boolean;
  created_at: string;
};

export type CurrentNudgeResponse = {
  nudge: BackendNudge | null;
  already_sent_today: boolean;
  adaptation_day: number;
};

export type LoginPopupResponse = {
  success: boolean;
  popup: {
    employee_name: string;
    adaptation_day: number;
    mode: string;
    nudge_sent: boolean;
    completed_tasks: number;
    total_tasks: number;
    video_url: string;
    nudge?: BackendNudge | null;
    next_task?: {
      title: string;
      description?: string | null;
      deadline_at?: string | null;
    } | null;
  };
};

export const onboardingApi = {
  async getDayOneTasks(employeeId: number = 1) {
    const response = await httpClient.get<BackendDayOneTask[]>(
      `/onboarding/day-one/tasks/${employeeId}`
    );

    return response.data;
  },

  async getEngagementTasks(employeeId: number = 1) {
    const response = await httpClient.get<BackendDayOneTask[]>(
      `/onboarding/engagement/tasks/${employeeId}`
    );

    return response.data;
  },

  async getEngagementContext(employeeId: number = 1) {
    const response = await httpClient.get<EngagementContext>(
      `/onboarding/engagement/context/${employeeId}`
    );

    return response.data;
  },

  async completeTask(taskId: number) {
    const response = await httpClient.post<BackendDayOneTask>(
      `/onboarding/tasks/${taskId}/complete`
    );

    return response.data;
  },

  async getCultureFitNudges() {
    const response = await httpClient.get<BackendNudge[]>("/onboarding/nudges");
    return response.data;
  },

  async getCurrentNudge(employeeId: number = 1) {
    const response = await httpClient.get<CurrentNudgeResponse>(
      `/onboarding/nudges/current/${employeeId}`
    );

    return response.data;
  },

  async sendNudgeToChat(employeeId: number = 1) {
    const response = await httpClient.post(
      `/onboarding/nudges/${employeeId}/send`
    );

    return response.data;
  },

  async resetTodayNudgeDelivery(employeeId: number = 1) {
    const response = await httpClient.delete(
      `/onboarding/nudges/demo-reset/${employeeId}`
    );

    return response.data;
  },

  async triggerUserLogin(employeeId: number = 1) {
    const response = await httpClient.post<LoginPopupResponse>(
      `/webhooks/on-user-login/${employeeId}`
    );

    return response.data;
  },

  async resetDayOneDemo(employeeId: number = 1) {
    const response = await httpClient.post<{ success: boolean; message: string }>(
      `/onboarding/day-one/demo-reset/${employeeId}`
    );

    return response.data;
  },

  async setupEngagementDemo(employeeId: number = 1) {
    const response = await httpClient.post<ShiftAdaptationDayResponse>(
      `/onboarding/engagement/demo-setup/${employeeId}`
    );

    return response.data;
  },

  async shiftAdaptationDay(
    employeeId: number = 1,
    params: { target_day?: number; delta?: number } = {}
  ) {
    const response = await httpClient.post<ShiftAdaptationDayResponse>(
      `/onboarding/nudges/demo-shift-day/${employeeId}`,
      params
    );

    return response.data;
  },
};

export type ShiftAdaptationDayResponse = {
  success: boolean;
  adaptation_day: number;
  nudge_day: number;
  message: string;
};
