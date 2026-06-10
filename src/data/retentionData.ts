export type SentimentWeek = {
  week: string;
  positive: number;
  neutral: number;
  negative: number;
};

export type RiskFlag = {
  id: number;
  title: string;
  description: string;
  level: "low" | "medium" | "high";
  status: "active" | "resolved";
};

export type DevelopmentRecommendation = {
  id: number;
  title: string;
  description: string;
  priority: "high" | "medium" | "low";
};

export const sentimentWeeks: SentimentWeek[] = [
  {
    week: "Неделя 1",
    positive: 68,
    neutral: 24,
    negative: 8,
  },
  {
    week: "Неделя 2",
    positive: 72,
    neutral: 20,
    negative: 8,
  },
  {
    week: "Неделя 3",
    positive: 76,
    neutral: 18,
    negative: 6,
  },
  {
    week: "Неделя 4",
    positive: 81,
    neutral: 15,
    negative: 4,
  },
];

export const riskFlags: RiskFlag[] = [
  {
    id: 1,
    title: "Нерегулярные входы в портал",
    description:
      "Сотрудник не заходил в портал 4 дня подряд в период адаптации.",
    level: "medium",
    status: "active",
  },
  {
    id: 2,
    title: "Игнорирование Culture Fit карточек",
    description:
      "Несколько карточек были просмотрены позже ожидаемого срока.",
    level: "low",
    status: "resolved",
  },
  {
    id: 3,
    title: "Негативная тональность в обращениях",
    description:
      "Digital Buddy обнаружил повышенную тревожность в нескольких сообщениях.",
    level: "high",
    status: "active",
  },
];

export const developmentRecommendations: DevelopmentRecommendation[] = [
  {
    id: 1,
    title: "Усилить знание внутренних процессов",
    description:
      "Рекомендуется пройти дополнительный модуль по корпоративным процессам и согласовать вопросы с наставником.",
    priority: "high",
  },
  {
    id: 2,
    title: "Развить навык деловой коммуникации",
    description:
      "Рекомендуется изучить материалы по корпоративной переписке и эффективным совещаниям.",
    priority: "medium",
  },
  {
    id: 3,
    title: "Сформировать индивидуальный план развития",
    description:
      "После итоговой оценки нужно закрепить план развития на следующие 3–6 месяцев.",
    priority: "medium",
  },
];

export const hrReportSummary = {
  routeCompletion: 87,
  completedTasks: 34,
  totalTasks: 39,
  npsDay14: 8,
  npsDay30: 9,
  finalNps: 8,
  riskLevel: "Средний",
  recommendation:
    "Продолжить сопровождение руководителем и наставником в течение следующего месяца.",
};
