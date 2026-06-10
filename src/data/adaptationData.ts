export type OneToOneMeeting = {
  id: number;
  title: string;
  date: string;
  time: string;
  manager: string;
  status: "upcoming" | "completed" | "pending";
};

export type SmartGoal = {
  id: number;
  title: string;
  description: string;
  metric: string;
  deadline: string;
  status: "draft" | "approved" | "needs_update";
};

export type LearningModule = {
  id: number;
  title: string;
  progress: number;
  deadline: string;
};

export type ReflectionQuestion = {
  id: number;
  question: string;
  hint: string;
};

export const oneToOneMeetings: OneToOneMeeting[] = [
  {
    id: 1,
    title: "Первая встреча 1:1 с руководителем",
    date: "15 февраля",
    time: "10:00",
    manager: "Руководитель подразделения",
    status: "upcoming",
  },
  {
    id: 2,
    title: "Промежуточная встреча по целям",
    date: "1 марта",
    time: "15:00",
    manager: "Руководитель подразделения",
    status: "pending",
  },
];

export const smartGoals: SmartGoal[] = [
  {
    id: 1,
    title: "Изучить основные процессы подразделения",
    description:
      "Понять ключевые бизнес-процессы, зоны ответственности и основные регламенты.",
    metric: "Пройти 3 внутренних материала и обсудить с руководителем",
    deadline: "До конца 1 месяца",
    status: "approved",
  },
  {
    id: 2,
    title: "Выполнить первые рабочие задачи",
    description:
      "Выполнить стартовый набор задач под контролем руководителя или наставника.",
    metric: "Не менее 5 выполненных задач с обратной связью",
    deadline: "До конца 2 месяца",
    status: "draft",
  },
  {
    id: 3,
    title: "Подготовить план развития",
    description:
      "Определить профессиональные навыки, которые нужно усилить после испытательного срока.",
    metric: "Согласованный план развития на 3–6 месяцев",
    deadline: "До 90-го дня",
    status: "needs_update",
  },
];

export const learningModules: LearningModule[] = [
  {
    id: 1,
    title: "Корпоративные процессы КМГ",
    progress: 70,
    deadline: "20 февраля",
  },
  {
    id: 2,
    title: "Информационная безопасность для сотрудников",
    progress: 45,
    deadline: "22 февраля",
  },
  {
    id: 3,
    title: "Комплаенс и деловая этика",
    progress: 90,
    deadline: "25 февраля",
  },
];

export const reflectionQuestions: ReflectionQuestion[] = [
  {
    id: 1,
    question: "Что уже получилось хорошо?",
    hint: "Опишите задачи, процессы или коммуникации, где вы чувствуете прогресс.",
  },
  {
    id: 2,
    question: "Где сейчас есть сложности?",
    hint: "Укажите темы, документы, процессы или ожидания, которые нужно уточнить.",
  },
  {
    id: 3,
    question: "Что нужно обсудить с руководителем?",
    hint: "Подготовьте вопросы для встречи 1:1.",
  },
];
