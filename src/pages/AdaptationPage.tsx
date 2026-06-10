import { useCallback, useEffect, useState } from "react";
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  MessageCircle,
  Send,
  Target,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import {
  adaptationApi,
  type AdaptationContext,
} from "../api/adaptationApi";
import { onboardingApi } from "../api/onboardingApi";
import { DigitalBuddyCharacter } from "../components/DigitalBuddy/DigitalBuddyCharacter";
import { useDigitalBuddy } from "../components/DigitalBuddy/DigitalBuddyContext";
import { MeetingCard } from "../components/MeetingCard/MeetingCard";
import { ProgressBar } from "../components/ProgressBar/ProgressBar";
import { SmartGoalCard } from "../components/SmartGoalCard/SmartGoalCard";
import type { OneToOneMeeting, SmartGoal } from "../data/adaptationData";
import "./AdaptationPage.css";

const EMPLOYEE_ID = 1;

type ApiMeeting = {
  id: number;
  title: string;
  description?: string | null;
  meeting_date: string;
  meeting_time?: string | null;
  status: string;
};

type ApiGoal = {
  id: number;
  title: string;
  description?: string | null;
  deadline: string;
  status: string;
};

type ApiLearningModule = {
  id: number;
  title: string;
  deadline: string;
  progress: number;
  status: string;
};

const FEATURE_LABELS: Record<string, string> = {
  f17: "F-17 · Напоминание 1:1",
  f18: "F-18 · Подготовка к 1:1",
  f19: "F-19 · SMART-цели",
  f20: "F-20 · Промежуточная оценка",
  f21: "F-21 · Рефлексия",
  f22: "F-22 · Актуализация КПД",
  f23: "F-23 · Обучение",
  f24: "F-24 · ВНД 24/7",
};

export function AdaptationPage() {
  const navigate = useNavigate();
  const { openChatWithPrompt } = useDigitalBuddy();
  const [meetings, setMeetings] = useState<OneToOneMeeting[]>([]);
  const [smartGoals, setSmartGoals] = useState<SmartGoal[]>([]);
  const [learningModules, setLearningModules] = useState<ApiLearningModule[]>(
    []
  );
  const [context, setContext] = useState<AdaptationContext | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isShiftingDay, setIsShiftingDay] = useState(false);
  const [isTriggeringTouchpoints, setIsTriggeringTouchpoints] = useState(false);
  const [touchpointResult, setTouchpointResult] = useState<string | null>(null);

  const adaptationDay = context?.adaptation_day ?? 1;

  const loadData = useCallback(async () => {
    const [meetingsData, goalsData, modulesData, contextData] =
      await Promise.all([
        adaptationApi.getMeetings(EMPLOYEE_ID),
        adaptationApi.getGoals(EMPLOYEE_ID),
        adaptationApi.getLearningModules(EMPLOYEE_ID),
        adaptationApi.getContext(EMPLOYEE_ID),
      ]);

    setMeetings(
      (meetingsData as ApiMeeting[]).map((meeting) => ({
        id: meeting.id,
        title: meeting.title,
        date: new Date(meeting.meeting_date).toLocaleDateString("ru-RU"),
        time: meeting.meeting_time?.slice(0, 5) || "—",
        manager: "Руководитель",
        status:
          meeting.status === "completed"
            ? "completed"
            : meeting.status === "planned"
              ? "upcoming"
              : "pending",
      }))
    );

    setSmartGoals(
      (goalsData as ApiGoal[]).map((goal) => ({
        id: goal.id,
        title: goal.title,
        description: goal.description || "",
        metric:
          goal.description?.slice(0, 80) ||
          "KPI по должностной инструкции",
        deadline: new Date(goal.deadline).toLocaleDateString("ru-RU"),
        status:
          goal.status === "completed"
            ? "approved"
            : goal.status === "needs_update"
              ? "needs_update"
              : "draft",
      }))
    );

    setLearningModules(modulesData as ApiLearningModule[]);
    setContext(contextData);
  }, []);

  useEffect(() => {
    loadData()
      .catch(() => undefined)
      .finally(() => setIsLoading(false));
  }, [loadData]);

  const handleShiftDay = async (delta: number) => {
    if (isShiftingDay || adaptationDay + delta < 1 || adaptationDay + delta > 90) {
      return;
    }

    setIsShiftingDay(true);
    setTouchpointResult(null);
    try {
      await onboardingApi.shiftAdaptationDay(EMPLOYEE_ID, { delta });
      await loadData();
    } finally {
      setIsShiftingDay(false);
    }
  };

  const handleSetupDemo = async () => {
    setIsShiftingDay(true);
    setTouchpointResult(null);
    try {
      await adaptationApi.setupDemo(EMPLOYEE_ID);
      await loadData();
    } finally {
      setIsShiftingDay(false);
    }
  };

  const handleTriggerTouchpoints = async () => {
    setIsTriggeringTouchpoints(true);
    try {
      const result = await adaptationApi.triggerTouchpoints(EMPLOYEE_ID);
      const sent = (result.touchpoints_sent as string[]).join(", ") || "нет";
      setTouchpointResult(`Touchpoints: ${sent}`);
    } finally {
      setIsTriggeringTouchpoints(false);
    }
  };

  const approvedGoals = smartGoals.filter(
    (goal) => goal.status === "approved"
  ).length;

  const averageLearningProgress =
    learningModules.length > 0
      ? Math.round(
          learningModules.reduce((sum, module) => sum + module.progress, 0) /
            learningModules.length
        )
      : 0;

  const reflectionSteps =
    context?.reflection_dialog.steps ?? [];

  const featureStatus = context?.feature_status;

  return (
    <main className="adaptation-page">
      <div className="adaptation-page__container">
        <button
          type="button"
          className="adaptation-page__back"
          onClick={() => navigate("/")}
        >
          <ArrowLeft size={18} />
          Назад к этапам
        </button>

        <header className="adaptation-page__header">
          <div>
            <span>Этап 4</span>
            <h1>Адаптация</h1>
            <p>
              Месяц 1–3: регулярные встречи 1:1, постановка целей по SMART,
              промежуточная оценка и корректировка плана адаптации.
            </p>
          </div>

          <div className="adaptation-page__badge">
            День {adaptationDay} · Месяц 1–3
          </div>
        </header>

        <section className="adaptation-hero">
          <div className="adaptation-hero__icon">
            <DigitalBuddyCharacter mood="idle" size={72} variant="standing" />
          </div>

          <div>
            <span>Digital Buddy · F-18, F-19, F-24</span>
            <h2>Подготовка к 1:1, SMART-цели и ответы по ВНД</h2>
            <p>
              Ассистент подскажет структуру разговора с руководителем,
              поможет сформулировать цели по SMART и ответит на вопросы по
              регламентам 24/7.
            </p>

            <div className="adaptation-hero__actions">
              <button
                type="button"
                onClick={() =>
                  openChatWithPrompt("Подготовка к встрече 1:1 с руководителем")
                }
              >
                <MessageCircle size={18} />
                Подготовить к 1:1
              </button>
              <button
                type="button"
                className="adaptation-hero__secondary"
                onClick={() => openChatWithPrompt("Помощь с SMART-целями")}
              >
                <Target size={18} />
                SMART-цели
              </button>
            </div>
          </div>
        </section>

        {featureStatus && (
          <section className="adaptation-features">
            {Object.entries(FEATURE_LABELS).map(([key, label]) => {
              const active =
                key === "f17"
                  ? featureStatus.f17_has_upcoming_meeting
                  : key === "f18"
                    ? featureStatus.f18_prep_available
                    : key === "f19"
                      ? featureStatus.f19_has_goals
                      : key === "f20"
                        ? featureStatus.f20_interim_scheduled
                        : key === "f21"
                          ? featureStatus.f21_reflection_available
                          : key === "f22"
                            ? featureStatus.f22_needs_kpi_update
                            : key === "f23"
                              ? featureStatus.f23_incomplete_modules > 0
                              : featureStatus.f24_vnd_available;

              return (
                <span
                  key={key}
                  className={`adaptation-feature-badge${active ? " adaptation-feature-badge--active" : ""}`}
                >
                  {label}
                </span>
              );
            })}
          </section>
        )}

        {isLoading ? (
          <div className="adaptation-info-card">
            <h3>Загрузка данных адаптации...</h3>
          </div>
        ) : (
          <section className="adaptation-page__grid">
            <div className="adaptation-page__main">
              <section className="adaptation-section">
                <div className="adaptation-section__header">
                  <div>
                    <span>F-17 · Встречи 1:1</span>
                    <h2>План коммуникации с руководителем</h2>
                  </div>
                </div>

                <div className="adaptation-section__cards adaptation-section__cards--two">
                  {meetings.map((meeting) => (
                    <MeetingCard key={meeting.id} meeting={meeting} />
                  ))}
                </div>

                {featureStatus?.f17_days_until_meeting === 2 && (
                  <p className="adaptation-section__note">
                    F-17: напоминание о ближайшей 1:1 отправлено в чат
                    (imbot.send) за 2 дня до встречи.
                  </p>
                )}
              </section>

              <section className="adaptation-section">
                <div className="adaptation-section__header">
                  <div>
                    <span>F-19 · SMART-цели</span>
                    <h2>Цели на испытательный срок</h2>
                  </div>

                  <button
                    type="button"
                    onClick={() =>
                      openChatWithPrompt("Помощь с SMART-целями на испытательный срок")
                    }
                  >
                    <Target size={17} />
                    Сформулировать цель
                  </button>
                </div>

                <div className="adaptation-section__cards">
                  {smartGoals.map((goal) => (
                    <SmartGoalCard key={goal.id} goal={goal} />
                  ))}
                </div>
              </section>

              <section className="adaptation-section">
                <div className="adaptation-section__header">
                  <div>
                    <span>F-21 · Рефлексия</span>
                    <h2>Подготовка к промежуточной оценке</h2>
                  </div>

                  <button
                    type="button"
                    onClick={() => openChatWithPrompt("Рефлексия прогресса")}
                  >
                    <MessageCircle size={17} />
                    Начать диалог
                  </button>
                </div>

                <div className="reflection-grid">
                  {reflectionSteps.map((item) => (
                    <article key={item.step} className="reflection-card">
                      <h3>{item.question}</h3>
                      <p>{item.hint}</p>
                      <textarea
                        placeholder="Введите короткий ответ..."
                        onFocus={() =>
                          openChatWithPrompt(
                            `Рефлексия: ${item.question}`
                          )
                        }
                      />
                    </article>
                  ))}
                </div>
              </section>
            </div>

            <aside className="adaptation-page__sidebar">
              <ProgressBar
                completed={approvedGoals}
                total={smartGoals.length || 1}
              />

              <div className="adaptation-info-card">
                <h3>F-23 · Обучение</h3>
                <p>
                  Средний прогресс модулей: {averageLearningProgress}%.{" "}
                  {featureStatus?.f23_incomplete_modules
                    ? `Незавершённых: ${featureStatus.f23_incomplete_modules}.`
                    : "Все модули завершены."}
                </p>

                <div className="learning-list">
                  {learningModules.map((module) => (
                    <div key={module.id} className="learning-item">
                      <div className="learning-item__top">
                        <span>{module.title}</span>
                        <strong>{module.progress}%</strong>
                      </div>

                      <div className="learning-item__track">
                        <div
                          className="learning-item__fill"
                          style={{ width: `${module.progress}%` }}
                        />
                      </div>

                      <small>
                        Дедлайн:{" "}
                        {new Date(module.deadline).toLocaleDateString("ru-RU")}
                      </small>
                    </div>
                  ))}
                </div>
              </div>

              <div className="adaptation-info-card">
                <h3>F-20 · Промежуточная оценка</h3>
                {context?.interim_assessment.meeting_date ? (
                  <>
                    <p>
                      Дата:{" "}
                      {new Date(
                        context.interim_assessment.meeting_date
                      ).toLocaleDateString("ru-RU")}
                      {context.interim_assessment.days_until != null &&
                        context.interim_assessment.days_until >= 0 &&
                        ` · через ${context.interim_assessment.days_until} дн.`}
                    </p>
                    <ul className="adaptation-prep-list">
                      {context.interim_assessment.employee_prep.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                    <small>
                      За неделю до оценки Digital Buddy напомнит сотруднику и
                      руководителю (imbot.send).
                    </small>
                  </>
                ) : (
                  <p>Встреча промежуточной оценки не запланирована.</p>
                )}
              </div>

              <div className="adaptation-info-card">
                <h3>F-24 · ВНД и регламенты</h3>
                <p>
                  Digital Buddy отвечает на вопросы по ВНД, процессам и
                  регламентам 24/7 — задайте вопрос в чате в любое время.
                </p>
              </div>

              <div className="adaptation-day-shift">
                <h3>Демо этапа «Адаптация»</h3>
                <p>
                  Сдвиньте день (31–90) для тестирования F-17–F-23 или
                  симулируйте OnUserLogin.
                </p>

                <button
                  type="button"
                  className="adaptation-day-shift__setup"
                  onClick={handleSetupDemo}
                  disabled={isShiftingDay}
                >
                  Быстрый старт (день 35)
                </button>

                <div className="adaptation-day-shift__controls">
                  <button
                    type="button"
                    onClick={() => handleShiftDay(-1)}
                    disabled={isShiftingDay || adaptationDay <= 1}
                  >
                    <ChevronLeft size={18} />
                  </button>

                  <div className="adaptation-day-shift__value">
                    <strong>{adaptationDay}</strong>
                    <span>из 90</span>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleShiftDay(1)}
                    disabled={isShiftingDay || adaptationDay >= 90}
                  >
                    <ChevronRight size={18} />
                  </button>
                </div>

                <button
                  type="button"
                  className="adaptation-day-shift__touchpoints"
                  onClick={handleTriggerTouchpoints}
                  disabled={isTriggeringTouchpoints}
                >
                  <Send size={16} />
                  {isTriggeringTouchpoints
                    ? "Отправка..."
                    : "Touchpoints (imbot.send)"}
                </button>

                {touchpointResult && (
                  <small className="adaptation-day-shift__result">
                    {touchpointResult}
                  </small>
                )}
              </div>
            </aside>
          </section>
        )}
      </div>
    </main>
  );
}
