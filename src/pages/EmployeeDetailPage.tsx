import { useEffect, useState } from "react";
import {
  ArrowLeft,
  AlertTriangle,
  BarChart3,
  Bot,
  CalendarDays,
  CheckCircle2,
  ClipboardCheck,
  FileText,
  MessageSquareText,
  Plus,
  RefreshCw,
  Save,
  ShieldCheck,
  Target,
  Trash2,
  UserRound,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import { HR_ROUTES } from "../routes/hrRoutes";
import { adaptationApi } from "../api/adaptationApi";
import {
  hrApi,
  type HREmployeeDetailResponse,
  type HRRecommendationItem,
  type HRRiskFlagItem,
} from "../api/hrApi";
import { riskEngineApi } from "../api/riskEngineApi";
import { ProgressBar } from "../components/ProgressBar/ProgressBar";
import { SentimentChart } from "../components/SentimentChart/SentimentChart";
import "./EmployeeDetailPage.css";

function BackendRiskFlagCard({ risk }: { risk: HRRiskFlagItem }) {
  return (
    <article className={`backend-risk-card backend-risk-card--${risk.level}`}>
      <div>
        <h3>{risk.title}</h3>
        <p>{risk.description}</p>
      </div>

      <span>{risk.status === "active" ? "Активен" : "Закрыт"}</span>
    </article>
  );
}

function BackendRecommendationCard({
  item,
}: {
  item: HRRecommendationItem;
}) {
  const priorityLabel = {
    low: "Низкий",
    medium: "Средний",
    high: "Высокий",
  }[item.priority];

  return (
    <article
      className={`backend-recommendation-card backend-recommendation-card--${item.priority}`}
    >
      <div>
        <h3>{item.title}</h3>
        <p>{item.description}</p>
      </div>

      <span>{priorityLabel}</span>
    </article>
  );
}

export function EmployeeDetailPage() {
  const navigate = useNavigate();
  const { id } = useParams();

  const [detail, setDetail] = useState<HREmployeeDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isNotFound, setIsNotFound] = useState(false);
  const [isAnalyzingRisks, setIsAnalyzingRisks] = useState(false);

  const [meetingForm, setMeetingForm] = useState({
    title: "",
    description: "",
    meeting_date: "",
    meeting_time: "10:00",
    status: "planned" as const,
  });

  const [goalForm, setGoalForm] = useState({
    title: "",
    description: "",
    deadline: "",
    status: "planned" as const,
  });

  const [learningForm, setLearningForm] = useState({
    title: "",
    deadline: "",
    progress: 0,
    status: "not_started" as const,
  });

  const loadEmployeeDetail = async () => {
    if (!id) {
      setIsNotFound(true);
      setIsLoading(false);
      return;
    }

    try {
      const data = await hrApi.getEmployeeDetail(Number(id));
      setDetail(data);
      setIsNotFound(false);
    } catch {
      setIsNotFound(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEmployeeDetail();
  }, [id]);

  const handleCreateMeeting = async () => {
    if (!detail || !meetingForm.title || !meetingForm.meeting_date) {
      alert("Заполните название и дату встречи.");
      return;
    }

    await adaptationApi.createMeeting(detail.employee.id, {
      title: meetingForm.title,
      description: meetingForm.description,
      meeting_date: meetingForm.meeting_date,
      meeting_time: meetingForm.meeting_time,
      status: meetingForm.status,
    });

    setMeetingForm({
      title: "",
      description: "",
      meeting_date: "",
      meeting_time: "10:00",
      status: "planned",
    });

    await loadEmployeeDetail();
  };

  const handleCreateGoal = async () => {
    if (!detail || !goalForm.title || !goalForm.deadline) {
      alert("Заполните название и дедлайн цели.");
      return;
    }

    await adaptationApi.createGoal(detail.employee.id, {
      title: goalForm.title,
      description: goalForm.description,
      deadline: goalForm.deadline,
      status: goalForm.status,
    });

    setGoalForm({
      title: "",
      description: "",
      deadline: "",
      status: "planned",
    });

    await loadEmployeeDetail();
  };

  const handleCreateLearningModule = async () => {
    if (!detail || !learningForm.title || !learningForm.deadline) {
      alert("Заполните название и дедлайн модуля.");
      return;
    }

    await adaptationApi.createLearningModule(detail.employee.id, {
      title: learningForm.title,
      deadline: learningForm.deadline,
      progress: learningForm.progress,
      status: learningForm.status,
    });

    setLearningForm({
      title: "",
      deadline: "",
      progress: 0,
      status: "not_started",
    });

    await loadEmployeeDetail();
  };

  const handleUpdateMeetingStatus = async (
    meetingId: number,
    status: "planned" | "completed" | "cancelled"
  ) => {
    await adaptationApi.updateMeeting(meetingId, { status });
    await loadEmployeeDetail();
  };

  const handleDeleteMeeting = async (meetingId: number) => {
    const confirmed = confirm("Удалить эту встречу?");

    if (!confirmed) {
      return;
    }

    await adaptationApi.deleteMeeting(meetingId);
    await loadEmployeeDetail();
  };

  const handleUpdateGoalStatus = async (
    goalId: number,
    status: "planned" | "in_progress" | "completed" | "needs_update"
  ) => {
    await adaptationApi.updateGoal(goalId, { status });
    await loadEmployeeDetail();
  };

  const handleDeleteGoal = async (goalId: number) => {
    const confirmed = confirm("Удалить эту SMART-цель?");

    if (!confirmed) {
      return;
    }

    await adaptationApi.deleteGoal(goalId);
    await loadEmployeeDetail();
  };

  const handleUpdateLearningProgress = async (
    moduleId: number,
    progress: number
  ) => {
    let status: "not_started" | "in_progress" | "completed" | "overdue" =
      "in_progress";

    if (progress <= 0) {
      status = "not_started";
    }

    if (progress >= 100) {
      status = "completed";
    }

    await adaptationApi.updateLearningModule(moduleId, {
      progress,
      status,
    });

    await loadEmployeeDetail();
  };

  const handleDeleteLearningModule = async (moduleId: number) => {
    const confirmed = confirm("Удалить обучающий модуль?");

    if (!confirmed) {
      return;
    }

    await adaptationApi.deleteLearningModule(moduleId);
    await loadEmployeeDetail();
  };

  const handleAnalyzeRisks = async () => {
    if (!detail || isAnalyzingRisks) {
      return;
    }

    try {
      setIsAnalyzingRisks(true);

      const result = await riskEngineApi.analyzeEmployee(detail.employee.id);

      await loadEmployeeDetail();

      alert(
        `Risk Engine завершил анализ. Активных рисков: ${result.active_risks_count}`
      );
    } finally {
      setIsAnalyzingRisks(false);
    }
  };

  if (isLoading) {
    return (
      <main className="employee-detail-page">
        <div className="employee-detail-page__container">
          <button
            type="button"
            className="employee-detail-page__back"
            onClick={() => navigate(HR_ROUTES.dashboard)}
          >
            <ArrowLeft size={18} />
            Назад в HR Dashboard
          </button>

          <div className="employee-not-found">
            <h1>Загрузка полной карточки сотрудника...</h1>
            <p>Получаем employee detail из backend.</p>
          </div>
        </div>
      </main>
    );
  }

  if (isNotFound || !detail) {
    return (
      <main className="employee-detail-page">
        <div className="employee-detail-page__container">
          <button
            type="button"
            className="employee-detail-page__back"
            onClick={() => navigate(HR_ROUTES.dashboard)}
          >
            <ArrowLeft size={18} />
            Назад в HR Dashboard
          </button>

          <div className="employee-not-found">
            <h1>Сотрудник не найден</h1>
            <p>
              Проверьте идентификатор сотрудника, backend или наличие seed-данных.
            </p>
          </div>
        </div>
      </main>
    );
  }

  const employee = detail.employee;

  const riskLabel = {
    low: "Низкий риск",
    medium: "Средний риск",
    high: "Высокий риск",
  }[employee.risk_level];

  const sentimentLabel = {
    positive: "Позитивный",
    neutral: "Нейтральный",
    negative: "Негативный",
  }[employee.sentiment];

  return (
    <main className="employee-detail-page">
      <div className="employee-detail-page__container">
        <button
          type="button"
          className="employee-detail-page__back"
          onClick={() => navigate(HR_ROUTES.dashboard)}
        >
          <ArrowLeft size={18} />
          Назад в HR Dashboard
        </button>

        <section className="employee-profile-hero">
          <div className="employee-profile-hero__avatar">
            {employee.full_name
              .split(" ")
              .map((part) => part[0])
              .join("")
              .slice(0, 2)}
          </div>

          <div className="employee-profile-hero__main">
            <span>Карточка адаптации сотрудника</span>
            <h1>{employee.full_name}</h1>
            <p>
              {employee.position || "Должность не указана"} •{" "}
              {employee.department || "Подразделение не указано"}
            </p>

            <div className="employee-profile-hero__meta">
              <div>
                <UserRound size={16} />
                Руководитель: {employee.manager || "Не указан"}
              </div>

              <div>
                <CalendarDays size={16} />
                Дата выхода:{" "}
                {new Date(employee.start_date).toLocaleDateString("ru-RU")}
              </div>

              <div>
                <Target size={16} />
                Этап: {employee.current_stage}
              </div>
            </div>
          </div>

          <div
            className={`employee-profile-hero__risk employee-profile-hero__risk--${employee.risk_level}`}
          >
            <AlertTriangle size={18} />
            {riskLabel}
          </div>

          <button
            type="button"
            className="employee-profile-hero__analyze"
            onClick={handleAnalyzeRisks}
            disabled={isAnalyzingRisks}
          >
            <RefreshCw size={17} />
            {isAnalyzingRisks ? "Анализ..." : "Анализ рисков"}
          </button>
        </section>

        <section className="employee-detail-summary">
          <article className="employee-detail-summary__card">
            <BarChart3 size={26} />
            <span>Прогресс</span>
            <strong>{employee.progress}%</strong>
          </article>

          <article className="employee-detail-summary__card">
            <ClipboardCheck size={26} />
            <span>Задачи</span>
            <strong>
              {employee.completed_tasks}/{employee.total_tasks}
            </strong>
          </article>

          <article className="employee-detail-summary__card">
            <FileText size={26} />
            <span>NPS</span>
            <strong>
              {employee.nps === null ? "—" : `${employee.nps}/10`}
            </strong>
          </article>

          <article className="employee-detail-summary__card">
            <MessageSquareText size={26} />
            <span>Sentiment</span>
            <strong>{sentimentLabel}</strong>
          </article>
        </section>

        <section className="employee-detail-grid">
          <div className="employee-detail-main">
            <section className="employee-detail-section">
              <div className="employee-detail-section__header">
                <div>
                  <span>Маршрут адаптации</span>
                  <h2>Общий прогресс</h2>
                </div>
              </div>

              <div className="employee-route-card">
                <ProgressBar
                  completed={employee.completed_tasks}
                  total={employee.total_tasks}
                />

                <div className="employee-route-steps">
                  {detail.route_steps.map((step) => {
                    const Icon =
                      step.key === "adaptation"
                        ? Bot
                        : step.key === "retention"
                          ? ShieldCheck
                          : CheckCircle2;

                    return (
                      <div
                        key={step.key}
                        className={`employee-route-step employee-route-step--${step.status}`}
                      >
                        <Icon size={20} />
                        <div>
                          <strong>{step.title}</strong>
                          <span>{step.description}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </section>

            <section className="employee-detail-section">
              <div className="employee-detail-section__header">
                <div>
                  <span>Sentiment</span>
                  <h2>Динамика тональности</h2>
                </div>
              </div>

              <SentimentChart data={detail.sentiment_weeks} />
            </section>

            <section className="employee-detail-section">
              <div className="employee-detail-section__header">
                <div>
                  <span>at_risk</span>
                  <h2>Риск-флаги</h2>
                </div>
              </div>

              <div className="employee-detail-cards">
                {detail.risk_flags.map((risk) => (
                  <BackendRiskFlagCard key={risk.id} risk={risk} />
                ))}
              </div>
            </section>

            <section className="employee-detail-section">
              <div className="employee-detail-section__header">
                <div>
                  <span>Развитие</span>
                  <h2>Рекомендации Digital Buddy</h2>
                </div>
              </div>

              <div className="employee-detail-cards">
                {detail.recommendations.map((item) => (
                  <BackendRecommendationCard key={item.id} item={item} />
                ))}
              </div>
            </section>
          </div>

          <aside className="employee-detail-sidebar">
            <div className="employee-detail-info-card">
              <h3>HR-резюме</h3>
              <p>{detail.hr_summary}</p>
            </div>

            <div className="employee-detail-info-card">
              <h3>Встречи 1:1</h3>

              <div className="adaptation-form">
                <input
                  value={meetingForm.title}
                  onChange={(event) =>
                    setMeetingForm((prev) => ({
                      ...prev,
                      title: event.target.value,
                    }))
                  }
                  placeholder="Название встречи"
                />

                <textarea
                  value={meetingForm.description}
                  onChange={(event) =>
                    setMeetingForm((prev) => ({
                      ...prev,
                      description: event.target.value,
                    }))
                  }
                  placeholder="Описание"
                />

                <div className="adaptation-form__row">
                  <input
                    type="date"
                    value={meetingForm.meeting_date}
                    onChange={(event) =>
                      setMeetingForm((prev) => ({
                        ...prev,
                        meeting_date: event.target.value,
                      }))
                    }
                  />

                  <input
                    type="time"
                    value={meetingForm.meeting_time}
                    onChange={(event) =>
                      setMeetingForm((prev) => ({
                        ...prev,
                        meeting_time: event.target.value,
                      }))
                    }
                  />
                </div>

                <button type="button" onClick={handleCreateMeeting}>
                  <Plus size={16} />
                  Добавить встречу
                </button>
              </div>

              <div className="employee-mini-list">
                {detail.meetings.map((meeting) => (
                  <div
                    key={meeting.id}
                    className="employee-mini-item employee-mini-item--managed"
                  >
                    <strong>{meeting.title}</strong>
                    <span>
                      {meeting.date}, {meeting.time}
                    </span>
                    <small>{meeting.description}</small>

                    <div className="managed-actions">
                      <select
                        value={meeting.status}
                        onChange={(event) =>
                          handleUpdateMeetingStatus(
                            meeting.id,
                            event.target.value as
                              | "planned"
                              | "completed"
                              | "cancelled"
                          )
                        }
                      >
                        <option value="planned">Запланирована</option>
                        <option value="completed">Завершена</option>
                        <option value="cancelled">Отменена</option>
                      </select>

                      <button
                        type="button"
                        onClick={() => handleDeleteMeeting(meeting.id)}
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="employee-detail-info-card">
              <h3>SMART-цели</h3>

              <div className="adaptation-form">
                <input
                  value={goalForm.title}
                  onChange={(event) =>
                    setGoalForm((prev) => ({
                      ...prev,
                      title: event.target.value,
                    }))
                  }
                  placeholder="Название цели"
                />

                <textarea
                  value={goalForm.description}
                  onChange={(event) =>
                    setGoalForm((prev) => ({
                      ...prev,
                      description: event.target.value,
                    }))
                  }
                  placeholder="Описание цели"
                />

                <input
                  type="date"
                  value={goalForm.deadline}
                  onChange={(event) =>
                    setGoalForm((prev) => ({
                      ...prev,
                      deadline: event.target.value,
                    }))
                  }
                />

                <button type="button" onClick={handleCreateGoal}>
                  <Target size={16} />
                  Добавить цель
                </button>
              </div>

              <div className="employee-mini-list">
                {detail.smart_goals.map((goal) => (
                  <div
                    key={goal.id}
                    className="employee-mini-item employee-mini-item--managed"
                  >
                    <strong>{goal.title}</strong>
                    <span>{goal.deadline}</span>
                    <small>{goal.description}</small>

                    <div className="managed-actions">
                      <select
                        value={goal.status}
                        onChange={(event) =>
                          handleUpdateGoalStatus(
                            goal.id,
                            event.target.value as
                              | "planned"
                              | "in_progress"
                              | "completed"
                              | "needs_update"
                          )
                        }
                      >
                        <option value="planned">План</option>
                        <option value="in_progress">В работе</option>
                        <option value="completed">Завершена</option>
                        <option value="needs_update">Нужно обновить</option>
                      </select>

                      <button
                        type="button"
                        onClick={() => handleDeleteGoal(goal.id)}
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="employee-detail-info-card">
              <h3>Обучение</h3>

              <div className="adaptation-form">
                <input
                  value={learningForm.title}
                  onChange={(event) =>
                    setLearningForm((prev) => ({
                      ...prev,
                      title: event.target.value,
                    }))
                  }
                  placeholder="Название модуля"
                />

                <input
                  type="date"
                  value={learningForm.deadline}
                  onChange={(event) =>
                    setLearningForm((prev) => ({
                      ...prev,
                      deadline: event.target.value,
                    }))
                  }
                />

                <button type="button" onClick={handleCreateLearningModule}>
                  <Save size={16} />
                  Добавить модуль
                </button>
              </div>

              <div className="employee-mini-list">
                {detail.learning_modules.map((module) => (
                  <div
                    key={module.id}
                    className="employee-learning-item employee-mini-item--managed"
                  >
                    <div>
                      <strong>{module.title}</strong>
                      <span>Дедлайн: {module.deadline}</span>
                    </div>

                    <div className="employee-learning-item__track">
                      <div style={{ width: `${module.progress}%` }} />
                    </div>

                    <small>{module.progress}%</small>

                    <div className="managed-actions">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={module.progress}
                        onChange={(event) =>
                          handleUpdateLearningProgress(
                            module.id,
                            Number(event.target.value)
                          )
                        }
                      />

                      <button
                        type="button"
                        onClick={() => handleDeleteLearningModule(module.id)}
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="employee-detail-info-card employee-detail-info-card--privacy">
              <h3>Конфиденциальность</h3>
              <p>{detail.privacy_note}</p>
            </div>
          </aside>
        </section>
      </div>
    </main>
  );
}
