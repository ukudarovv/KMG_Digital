export type DayOneTask = {
  id: number;
  title: string;
  description: string;
  deadline: string;
  status: "completed" | "in_progress" | "pending";
  required: boolean;
  requirementCode?: string | null;
  documentUrl?: string | null;
  externalLink?: string | null;
  confirmationRequired?: boolean;
};

export const dayOneTasks: DayOneTask[] = [
  {
    id: 1,
    title: "Просмотр видео Председателя Правления",
    description: "Ознакомьтесь с приветственным видеообращением.",
    deadline: "Сегодня до 18:00",
    status: "in_progress",
    required: true,
    externalLink: "https://team.kmg.kz/onboarding/welcome-video",
    confirmationRequired: true,
  },
  {
    id: 2,
    title: "Инструктаж по технике безопасности",
    description: "Пройдите обязательный инструктаж и тестирование.",
    deadline: "Сегодня до 18:00",
    status: "pending",
    required: true,
  },
  {
    id: 3,
    title: "Инструктаж по информационной безопасности",
    description: "Ознакомьтесь с правилами ИБ и подтвердите прохождение.",
    deadline: "Сегодня до 18:00",
    status: "pending",
    required: true,
  },
  {
    id: 4,
    title: "Ознакомление с пропускным режимом",
    description: "Изучите правила доступа и использования пропуска.",
    deadline: "Сегодня до 18:00",
    status: "pending",
    required: true,
  },
  {
    id: 5,
    title: "Кодекс деловой этики",
    description: "Ознакомьтесь с кодексом и подтвердите согласие.",
    deadline: "Сегодня до 18:00",
    status: "pending",
    required: true,
  },
  {
    id: 6,
    title: "Модуль Комплаенс",
    description: "Антикоррупционная политика и линия доверия.",
    deadline: "Сегодня до 18:00",
    status: "pending",
    required: true,
  },
];

export function mapBackendTask(task: {
  id: number;
  title: string;
  description?: string | null;
  deadline_at?: string | null;
  status: string;
  is_required: boolean;
  document_url?: string | null;
  external_link?: string | null;
  confirmation_required?: boolean;
  requirement_code?: string | null;
}): DayOneTask {
  return {
    id: task.id,
    title: task.title,
    description: task.description || "",
    deadline: task.deadline_at
      ? new Date(task.deadline_at).toLocaleString("ru-RU")
      : "Сегодня до 18:00",
    status:
      task.status === "overdue"
        ? "pending"
        : task.status === "in_progress"
          ? "in_progress"
          : task.status === "completed"
            ? "completed"
            : "pending",
    required: task.is_required,
    requirementCode: task.requirement_code,
    documentUrl: task.document_url,
    externalLink: task.external_link,
    confirmationRequired: task.confirmation_required,
  };
}
