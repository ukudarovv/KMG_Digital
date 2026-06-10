export type EmployeeOnboardingStatus = {
  id: number;
  fullName: string;
  position: string;
  department: string;
  manager: string;
  startDate: string;
  currentStage: "Знакомство" | "Вовлечение" | "Адаптация" | "Закрепление";
  progress: number;
  completedTasks: number;
  totalTasks: number;
  nps: number | null;
  sentiment: "positive" | "neutral" | "negative";
  riskLevel: "low" | "medium" | "high";
  lastActivity: string;
};

export const employeesOnboarding: EmployeeOnboardingStatus[] = [
  {
    id: 1,
    fullName: "Азамат Нурланов",
    position: "Специалист по закупкам",
    department: "Департамент закупок",
    manager: "Айгуль Сапарова",
    startDate: "01.02.2026",
    currentStage: "Знакомство",
    progress: 18,
    completedTasks: 1,
    totalTasks: 6,
    nps: null,
    sentiment: "neutral",
    riskLevel: "low",
    lastActivity: "Сегодня, 10:24",
  },
  {
    id: 2,
    fullName: "Дана Ермекова",
    position: "HR-аналитик",
    department: "ДУЧР",
    manager: "Марат Ибраев",
    startDate: "15.01.2026",
    currentStage: "Вовлечение",
    progress: 54,
    completedTasks: 21,
    totalTasks: 39,
    nps: 9,
    sentiment: "positive",
    riskLevel: "low",
    lastActivity: "Сегодня, 09:10",
  },
  {
    id: 3,
    fullName: "Руслан Ахметов",
    position: "Инженер ИБ",
    department: "Информационная безопасность",
    manager: "Ержан Касымов",
    startDate: "10.12.2025",
    currentStage: "Адаптация",
    progress: 72,
    completedTasks: 28,
    totalTasks: 39,
    nps: 7,
    sentiment: "neutral",
    riskLevel: "medium",
    lastActivity: "Вчера, 17:45",
  },
  {
    id: 4,
    fullName: "Мадина Оразбаева",
    position: "Финансовый аналитик",
    department: "Финансовый департамент",
    manager: "Самат Кенжебаев",
    startDate: "02.11.2025",
    currentStage: "Закрепление",
    progress: 87,
    completedTasks: 34,
    totalTasks: 39,
    nps: 8,
    sentiment: "negative",
    riskLevel: "high",
    lastActivity: "4 дня назад",
  },
];
