import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  LogIn,
  MessageCircle,
  RotateCcw,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import {
  onboardingApi,
  type BackendDayOneTask,
  type BackendNudge,
  type CurrentNudgeResponse,
  type EngagementContext,
} from "../api/onboardingApi";
import { surveyApi, type SurveySummary } from "../api/surveyApi";
import { NudgeCard } from "../components/NudgeCard/NudgeCard";
import { NudgePopup } from "../components/NudgePopup/NudgePopup";
import { ProgressBar } from "../components/ProgressBar/ProgressBar";
import { TaskCard } from "../components/TaskCard/TaskCard";
import { mapBackendTask } from "../data/dayOneTasks";
import "./EngagementPage.css";

const EMPLOYEE_ID = 1;
const ENGAGEMENT_POPUP_SESSION_KEY = "kmg_engagement_popup_shown";

export function EngagementPage() {
  const navigate = useNavigate();

  const [nudges, setNudges] = useState<BackendNudge[]>([]);
  const [engagementTasks, setEngagementTasks] = useState<BackendDayOneTask[]>([]);
  const [engagementContext, setEngagementContext] =
    useState<EngagementContext | null>(null);
  const [currentNudgeData, setCurrentNudgeData] =
    useState<CurrentNudgeResponse | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isNudgePopupOpen, setIsNudgePopupOpen] = useState(false);
  const [selectedNudge, setSelectedNudge] = useState<BackendNudge | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [isShiftingDay, setIsShiftingDay] = useState(false);
  const [isSimulatingLogin, setIsSimulatingLogin] = useState(false);

  const [surveySummary, setSurveySummary] = useState<SurveySummary | null>(null);

  const [pulseComment, setPulseComment] = useState("");
  const [pulseRoleClear, setPulseRoleClear] = useState(true);
  const [pulseManagerSupport, setPulseManagerSupport] = useState(true);
  const [pulseHasQuestions, setPulseHasQuestions] = useState(false);

  const [npsScore, setNpsScore] = useState(8);
  const [npsComment, setNpsComment] = useState("");

  const currentNudge = currentNudgeData?.nudge || null;
  const alreadySentToday = currentNudgeData?.already_sent_today || false;
  const adaptationDay = currentNudgeData?.adaptation_day || 1;

  const nudgeDay = Math.min(adaptationDay, 23);
  const pulseUnlocked = adaptationDay >= 14;
  const npsUnlocked = adaptationDay >= 30;

  const sentCount = useMemo(() => {
    const completedThrough = alreadySentToday ? nudgeDay : nudgeDay - 1;
    return Math.max(completedThrough, 0);
  }, [alreadySentToday, nudgeDay]);

  const refreshEngagementState = async (openPopupForCurrent = false) => {
    const [allNudges, current, summary, tasks, context] = await Promise.all([
      onboardingApi.getCultureFitNudges(),
      onboardingApi.getCurrentNudge(EMPLOYEE_ID),
      surveyApi.getSummary(EMPLOYEE_ID),
      onboardingApi.getEngagementTasks(EMPLOYEE_ID),
      onboardingApi.getEngagementContext(EMPLOYEE_ID),
    ]);

    setNudges(allNudges);
    setCurrentNudgeData(current);
    setSurveySummary(summary);
    setEngagementTasks(tasks);
    setEngagementContext(context);

    if (openPopupForCurrent && current.nudge) {
      setSelectedNudge(current.nudge);
      setIsNudgePopupOpen(true);
    }

    return current;
  };

  const loadNudges = async () => {
    try {
      setIsLoading(true);
      await onboardingApi.setupEngagementDemo(EMPLOYEE_ID);

      const alreadyShown = sessionStorage.getItem(ENGAGEMENT_POPUP_SESSION_KEY);
      const current = await refreshEngagementState(!alreadyShown);

      if (!alreadyShown && current.nudge) {
        sessionStorage.setItem(ENGAGEMENT_POPUP_SESSION_KEY, "1");
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadNudges();
  }, []);

  const handleCompleteEngagementTask = async (taskId: number) => {
    await onboardingApi.completeTask(taskId);
    await refreshEngagementState(false);
  };

  const handleSendToChat = async () => {
    if (!currentNudge || alreadySentToday || isSending) {
      return;
    }

    try {
      setIsSending(true);

      await onboardingApi.sendNudgeToChat(EMPLOYEE_ID);
      await refreshEngagementState(false);
      closeNudgePopup();

      alert("Карточка Culture Fit отправлена в Bitrix-чат от имени Digital Buddy.");
    } finally {
      setIsSending(false);
    }
  };

  const handleShiftDay = async (delta: number) => {
    if (isShiftingDay || adaptationDay + delta < 2 || adaptationDay + delta > 30) {
      return;
    }

    try {
      setIsShiftingDay(true);
      await onboardingApi.shiftAdaptationDay(EMPLOYEE_ID, { delta });
      sessionStorage.removeItem(ENGAGEMENT_POPUP_SESSION_KEY);
      await refreshEngagementState(true);
    } finally {
      setIsShiftingDay(false);
    }
  };

  const handleSimulateLogin = async () => {
    if (isSimulatingLogin) {
      return;
    }

    try {
      setIsSimulatingLogin(true);
      await onboardingApi.triggerUserLogin(EMPLOYEE_ID);
      const current = await refreshEngagementState(true);

      if (current.already_sent_today) {
        alert(
          "Симуляция входа: карточка дня показана в окне и продублирована в Bitrix-чат."
        );
      }
    } finally {
      setIsSimulatingLogin(false);
    }
  };

  const handleResetDemo = async () => {
    await onboardingApi.resetTodayNudgeDelivery(EMPLOYEE_ID);
    await refreshEngagementState(true);
    alert("Demo-флаг сброшен. Карточку снова можно отправить.");
  };

  const handleResetSurveys = async () => {
    await surveyApi.resetEngagementSurveys(EMPLOYEE_ID);
    const summary = await surveyApi.getSummary(EMPLOYEE_ID);
    setSurveySummary(summary);
    alert("Пульс-опрос и NPS сброшены для демо.");
  };

  const handleSubmitPulseSurvey = async () => {
    if (!pulseUnlocked) {
      return;
    }

    await surveyApi.createSurvey(EMPLOYEE_ID, {
      survey_type: "pulse_day_14",
      nps_score: null,
      comment: pulseComment,
      answers: {
        understands_role: pulseRoleClear,
        has_manager_support: pulseManagerSupport,
        has_open_questions: pulseHasQuestions,
      },
    });

    setPulseComment("");
    await refreshEngagementState(false);

    alert("Пульс-опрос День 14 отправлен. Результат передан HR.");
  };

  const handleSubmitNpsSurvey = async () => {
    if (!npsUnlocked) {
      return;
    }

    await surveyApi.createSurvey(EMPLOYEE_ID, {
      survey_type: "nps_day_30",
      nps_score: npsScore,
      comment: npsComment,
      answers: {
        recommend_onboarding: npsScore,
      },
    });

    setNpsComment("");
    await refreshEngagementState(false);

    alert("NPS-опрос День 30 отправлен. Результат передан HR.");
  };

  const openNudgePopup = (nudge: BackendNudge) => {
    setSelectedNudge(nudge);
    setIsNudgePopupOpen(true);
  };

  const handleOpenNudgeCard = (nudge: BackendNudge) => {
    if (nudge.day_number > adaptationDay) {
      return;
    }

    openNudgePopup(nudge);
  };

  const closeNudgePopup = () => {
    setIsNudgePopupOpen(false);
    setSelectedNudge(null);
  };

  if (isLoading) {
    return (
      <main className="engagement-page">
        <div className="engagement-page__container">
          <button
            type="button"
            className="engagement-page__back"
            onClick={() => navigate("/")}
          >
            <ArrowLeft size={18} />
            Назад к этапам
          </button>

          <div className="engagement-info-card">
            <h3>Загрузка этапа “Вовлечение”...</h3>
            <p>Получаем Culture Fit карточки и текущий статус из backend.</p>
          </div>
        </div>
      </main>
    );
  }

  if (!currentNudge) {
    return (
      <main className="engagement-page">
        <div className="engagement-page__container">
          <button
            type="button"
            className="engagement-page__back"
            onClick={() => navigate("/")}
          >
            <ArrowLeft size={18} />
            Назад к этапам
          </button>

          <div className="engagement-info-card">
            <h3>Карточка не найдена</h3>
            <p>
              Проверьте, что backend запущен, миграции применены, а seed-данные
              созданы.
            </p>
          </div>
        </div>
      </main>
    );
  }

  const popupNudge = selectedNudge ?? currentNudge;
  const isTodayNudge = popupNudge.day_number === nudgeDay;

  return (
    <main className="engagement-page">
      <NudgePopup
        nudge={{
          day: popupNudge.day_number,
          title: popupNudge.title,
          text: popupNudge.text,
          source: popupNudge.source,
        }}
        isOpen={isNudgePopupOpen}
        alreadySentToday={alreadySentToday}
        canSendToChat={isTodayNudge}
        onClose={closeNudgePopup}
        onSendToChat={handleSendToChat}
      />

      <div className="engagement-page__container">
        <button
          type="button"
          className="engagement-page__back"
          onClick={() => navigate("/")}
        >
          <ArrowLeft size={18} />
          Назад к этапам
        </button>

        <header className="engagement-page__header">
          <div>
            <span>Этап 3</span>
            <h1>Вовлечение</h1>
            <p>
              Дни 2–30: ежедневные Culture Fit Nudges, первые HR-опросы,
              знакомство с корпоративными правилами и вовлечение в процессы.
            </p>
          </div>

          <div className="engagement-page__header-actions">
            <button
              type="button"
              className="engagement-page__demo-btn"
              onClick={handleSimulateLogin}
              disabled={isSimulatingLogin}
            >
              <LogIn size={16} />
              {isSimulatingLogin ? "Вход..." : "Симулировать вход"}
            </button>
            <div className="engagement-page__badge">
              День адаптации: {adaptationDay}
            </div>
          </div>
        </header>

        <section className="engagement-page__grid">
          <div className="engagement-page__main">
            <article className="today-nudge">
              <div>
                <span>Карточка дня {nudgeDay}</span>
                <h2>{currentNudge.title}</h2>
                <p>{currentNudge.text}</p>
                <small>Источник: {currentNudge.source}</small>
              </div>

              <div className="today-nudge__actions">
                <button
                  type="button"
                  onClick={() => openNudgePopup(currentNudge)}
                >
                  Открыть карточку
                </button>

                <button
                  type="button"
                  disabled={alreadySentToday || isSending}
                  onClick={handleSendToChat}
                >
                  <MessageCircle size={17} />
                  {isSending ? "Отправка..." : "Отправить в чат"}
                </button>
              </div>
            </article>

            <section className="requirements-grid">
              {[
                { code: "F-10", label: "ДИ и положение о подразделении", done: engagementContext?.feature_status.f10_completed },
                { code: "F-11", label: "Цели КПД на испытательный срок", done: engagementContext?.feature_status.f11_completed },
                { code: "F-12", label: "Корпоративные каналы", done: engagementContext?.feature_status.f12_unlocked },
                { code: "F-13", label: "Обучающие курсы", done: engagementContext?.feature_status.f13_has_courses },
                { code: "F-14", label: "Пульс-опрос (день 14)", done: engagementContext?.feature_status.f14_completed },
                { code: "F-15", label: "Встреча с Директором ДУЧР", done: engagementContext?.feature_status.f15_unlocked },
                { code: "F-16", label: "NPS-опрос (день 30)", done: engagementContext?.feature_status.f16_completed },
              ].map((item) => (
                <div
                  key={item.code}
                  className={`requirements-grid__item ${
                    item.done ? "requirements-grid__item--done" : ""
                  }`}
                >
                  <strong>{item.code}</strong>
                  <span>{item.label}</span>
                </div>
              ))}
            </section>

            <section className="survey-row">
              <article className="survey-card">
                <span>F-14 · День 14</span>
                <h3>Пульс-опрос</h3>
                <p>
                  3 вопроса о первых двух неделях адаптации. Результат видит HR.
                </p>

                {!pulseUnlocked ? (
                  <div className="survey-status survey-status--locked">
                    Откроется на 14-й день адаптации. Сейчас день {adaptationDay}.
                    Сдвиньте день в панели справа или откройте карточку дня 14.
                  </div>
                ) : surveySummary?.pulse_day_14_completed ? (
                  <div className="survey-status survey-status--done">
                    Пульс-опрос уже отправлен
                  </div>
                ) : (
                  <div className="survey-form">
                    <label>
                      <input
                        type="checkbox"
                        checked={pulseRoleClear}
                        onChange={(event) => setPulseRoleClear(event.target.checked)}
                      />
                      Я понимаю свою роль и задачи
                    </label>

                    <label>
                      <input
                        type="checkbox"
                        checked={pulseManagerSupport}
                        onChange={(event) =>
                          setPulseManagerSupport(event.target.checked)
                        }
                      />
                      У меня есть поддержка руководителя
                    </label>

                    <label>
                      <input
                        type="checkbox"
                        checked={pulseHasQuestions}
                        onChange={(event) =>
                          setPulseHasQuestions(event.target.checked)
                        }
                      />
                      У меня остались открытые вопросы
                    </label>

                    <textarea
                      value={pulseComment}
                      onChange={(event) => setPulseComment(event.target.value)}
                      placeholder="Комментарий"
                    />

                    <button type="button" onClick={handleSubmitPulseSurvey}>
                      Отправить пульс-опрос
                    </button>
                  </div>
                )}
              </article>

              <article className="survey-card">
                <span>F-16 · День 30</span>
                <h3>NPS-опрос</h3>
                <p>
                  Оценка удовлетворённости адаптацией и открытый комментарий.
                </p>

                {!npsUnlocked ? (
                  <div className="survey-status survey-status--locked">
                    Откроется на 30-й день адаптации. Сейчас день {adaptationDay}.
                    Сдвиньте день в панели справа или откройте карточку дня 30.
                  </div>
                ) : surveySummary?.nps_day_30_completed ? (
                  <div className="survey-status survey-status--done">
                    NPS уже отправлен: {surveySummary.latest_nps ?? "—"}/10
                  </div>
                ) : (
                  <div className="survey-form">
                    <label>
                      Оценка NPS: {npsScore}/10
                      <input
                        type="range"
                        min="0"
                        max="10"
                        value={npsScore}
                        onChange={(event) => setNpsScore(Number(event.target.value))}
                      />
                    </label>

                    <textarea
                      value={npsComment}
                      onChange={(event) => setNpsComment(event.target.value)}
                      placeholder="Комментарий"
                    />

                    <button type="button" onClick={handleSubmitNpsSurvey}>
                      Отправить NPS
                    </button>
                  </div>
                )}
              </article>
            </section>

            {engagementContext?.corporate_channels ? (
              <section className="engagement-feature-card">
                <div className="engagement-feature-card__header">
                  <span>F-12</span>
                  <h2>{engagementContext.corporate_channels.title}</h2>
                  <p>{engagementContext.corporate_channels.description}</p>
                </div>
                <div className="engagement-feature-card__list">
                  {engagementContext.corporate_channels.channels.map((channel) => (
                    <article key={channel.name}>
                      <strong>{channel.name}</strong>
                      <p>{channel.purpose}</p>
                      <small>{channel.contact}</small>
                    </article>
                  ))}
                </div>
              </section>
            ) : (
              <section className="engagement-info-card">
                <h3>F-12 · Корпоративные каналы</h3>
                <p>
                  Digital Buddy расскажет о структуре подразделений с 4-го дня
                  адаптации. Сейчас день {adaptationDay}.
                </p>
              </section>
            )}

            {engagementContext && engagementContext.learning_modules.length > 0 && (
              <section className="engagement-feature-card">
                <div className="engagement-feature-card__header">
                  <span>F-13</span>
                  <h2>Обучающие курсы</h2>
                  <p>
                    Напоминания о назначенных курсах и отслеживание прогресса
                    прохождения.
                  </p>
                </div>
                <div className="learning-modules">
                  {engagementContext.learning_modules.map((module) => (
                    <article key={module.id} className="learning-module">
                      <div className="learning-module__header">
                        <strong>{module.title}</strong>
                        <span>{module.progress}%</span>
                      </div>
                      <div className="learning-module__bar">
                        <div
                          className="learning-module__fill"
                          style={{ width: `${module.progress}%` }}
                        />
                      </div>
                      <small>
                        Дедлайн:{" "}
                        {new Date(module.deadline).toLocaleDateString("ru-RU")}
                      </small>
                    </article>
                  ))}
                </div>
              </section>
            )}

            {engagementContext?.duchr_meeting ? (
              <section className="engagement-feature-card">
                <div className="engagement-feature-card__header">
                  <span>F-15</span>
                  <h2>{engagementContext.duchr_meeting.title}</h2>
                  <p>{engagementContext.duchr_meeting.description}</p>
                </div>
                <ul className="engagement-feature-card__questions">
                  {engagementContext.duchr_meeting.suggested_questions.map(
                    (question) => (
                      <li key={question}>{question}</li>
                    )
                  )}
                </ul>
              </section>
            ) : (
              <section className="engagement-info-card">
                <h3>F-15 · Встреча с Директором ДУЧР</h3>
                <p>
                  Напоминание и подготовка вопросов откроются на 20-й день
                  адаптации. Сейчас день {adaptationDay}.
                </p>
              </section>
            )}

            <section className="tasks-section">
              <div className="tasks-section__header">
                <div>
                  <span>F-10 · F-11</span>
                  <h2>ДИ и цели КПД</h2>
                </div>
              </div>

              <div className="tasks-section__list">
                {engagementTasks.length === 0 ? (
                  <div className="engagement-info-card">
                    <h3>Задачи вовлечения не найдены</h3>
                    <p>Запустите seed для создания задач F-10 и F-11.</p>
                  </div>
                ) : (
                  engagementTasks.map((task) => (
                    <TaskCard
                      key={task.id}
                      task={mapBackendTask(task)}
                      onComplete={handleCompleteEngagementTask}
                    />
                  ))
                )}
              </div>
            </section>

            <section className="nudges-section">
              <div className="nudges-section__header">
                <div>
                  <span>Банк Culture Fit</span>
                  <h2>23 карточки корпоративной культуры</h2>
                </div>
              </div>

              <div className="nudges-section__list">
                {nudges.map((nudge) => (
                  <NudgeCard
                    key={nudge.id}
                    nudge={{
                      day: nudge.day_number,
                      title: nudge.title,
                      text: nudge.text,
                      source: nudge.source,
                    }}
                    isActive={nudge.day_number === nudgeDay}
                    isCompleted={nudge.day_number < nudgeDay}
                    isFuture={nudge.day_number > nudgeDay}
                    onClick={
                      nudge.day_number <= adaptationDay
                        ? () => handleOpenNudgeCard(nudge)
                        : undefined
                    }
                  />
                ))}
              </div>
            </section>
          </div>

          <aside className="engagement-page__sidebar">
            <ProgressBar
              completed={sentCount}
              total={nudges.length}
              label="Culture Fit Nudges"
            />

            <div className="engagement-day-shift">
              <h3>Имитация дня</h3>
              <p>
                Демо-панель для тестирования: сдвиньте день адаптации (2–30),
                чтобы симулировать OnUserLogin и опросы. Сотрудник не может
                открывать будущие карточки — только текущий и прошедшие дни.
              </p>

              <div className="engagement-day-shift__controls">
                <button
                  type="button"
                  onClick={() => handleShiftDay(-1)}
                  disabled={isShiftingDay || adaptationDay <= 2}
                >
                  <ChevronLeft size={18} />
                  День −1
                </button>

                <div className="engagement-day-shift__value">
                  <strong>{adaptationDay}</strong>
                  <span>из 30</span>
                </div>

                <button
                  type="button"
                  onClick={() => handleShiftDay(1)}
                  disabled={isShiftingDay || adaptationDay >= 30}
                >
                  День +1
                  <ChevronRight size={18} />
                </button>
              </div>

              <small>
                Карточка Culture Fit: день {nudgeDay} из 23
                {adaptationDay > 23 ? " (банк завершён)" : ""}
              </small>
            </div>

            <div className="engagement-info-card">
              <h3>Правило отправки</h3>
              <p>
                При входе сотрудника показывается только одна карточка. Если он
                уже получил карточку сегодня, повторная отправка блокируется на
                уровне backend и PostgreSQL.
              </p>
            </div>

            <div className="engagement-info-card">
              <h3>Статус сегодня</h3>
              <p>
                {alreadySentToday
                  ? "Карточка уже отправлена сегодня."
                  : "Карточка ещё не отправлена сегодня."}
              </p>
            </div>

            <button
              type="button"
              className="engagement-page__reset"
              onClick={handleResetDemo}
            >
              <RotateCcw size={17} />
              Сбросить demo-флаг
            </button>

            <button
              type="button"
              className="engagement-page__reset engagement-page__reset--secondary"
              onClick={handleResetSurveys}
            >
              <RotateCcw size={17} />
              Сбросить опросы
            </button>
          </aside>
        </section>
      </div>
    </main>
  );
}
