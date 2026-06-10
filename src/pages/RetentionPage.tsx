import { useEffect, useState } from "react";
import {
  ArrowLeft,
  BarChart3,
  ClipboardCheck,
  Database,
  FileText,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { hrApi, type HREmployeeDetailResponse } from "../api/hrApi";
import { surveyApi, type SurveySummary } from "../api/surveyApi";
import { DigitalBuddyCharacter } from "../components/DigitalBuddy/DigitalBuddyCharacter";
import { DevelopmentCard } from "../components/DevelopmentCard/DevelopmentCard";
import { ProgressBar } from "../components/ProgressBar/ProgressBar";
import { RiskFlagCard } from "../components/RiskFlagCard/RiskFlagCard";
import { SentimentChart } from "../components/SentimentChart/SentimentChart";
import "./RetentionPage.css";

const EMPLOYEE_ID = 1;

export function RetentionPage() {
  const navigate = useNavigate();

  const [employeeDetail, setEmployeeDetail] =
    useState<HREmployeeDetailResponse | null>(null);
  const [surveySummary, setSurveySummary] = useState<SurveySummary | null>(null);
  const [finalNpsScore, setFinalNpsScore] = useState(9);
  const [finalNpsComment, setFinalNpsComment] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmittingFinalNps, setIsSubmittingFinalNps] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [detail, summary] = await Promise.all([
          hrApi.getEmployeeDetail(EMPLOYEE_ID),
          surveyApi.getSummary(EMPLOYEE_ID),
        ]);

        setEmployeeDetail(detail);
        setSurveySummary(summary);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  const handleSubmitFinalNps = async () => {
    if (isSubmittingFinalNps) {
      return;
    }

    try {
      setIsSubmittingFinalNps(true);

      await surveyApi.createSurvey(EMPLOYEE_ID, {
        survey_type: "final_nps",
        nps_score: finalNpsScore,
        comment: finalNpsComment,
        answers: {
          recommend_company: finalNpsScore,
          adaptation_quality:
            finalNpsScore >= 9
              ? "excellent"
              : finalNpsScore >= 7
                ? "good"
                : finalNpsScore >= 5
                  ? "neutral"
                  : "needs_attention",
        },
      });

      const [summary, detail] = await Promise.all([
        surveyApi.getSummary(EMPLOYEE_ID),
        hrApi.getEmployeeDetail(EMPLOYEE_ID),
      ]);

      setSurveySummary(summary);
      setEmployeeDetail(detail);
      setFinalNpsComment("");

      alert("Final NPS успешно отправлен.");
    } finally {
      setIsSubmittingFinalNps(false);
    }
  };

  if (isLoading || !employeeDetail) {
    return (
      <main className="retention-page">
        <div className="retention-page__container">
          <p>Загрузка HR-аналитики...</p>
        </div>
      </main>
    );
  }

  const employee = employeeDetail.employee;
  const riskFlags = employeeDetail.risk_flags.map((risk) => ({
    id: risk.id,
    title: risk.title,
    description: risk.description,
    level: risk.level,
    status: risk.status,
  }));
  const developmentRecommendations = employeeDetail.recommendations.map((item) => ({
    id: item.id,
    title: item.title,
    description: item.description,
    priority: item.priority,
  }));
  const sentimentWeeks = employeeDetail.sentiment_weeks.map((week) => ({
    week: week.week,
    positive: week.positive,
    neutral: week.neutral,
    negative: week.negative,
  }));

  const activeRiskCount = riskFlags.filter((risk) => risk.status === "active").length;
  const finalNps = surveySummary?.latest_nps ?? employee.nps ?? 0;

  return (
    <main className="retention-page">
      <div className="retention-page__container">
        <button
          type="button"
          className="retention-page__back"
          onClick={() => navigate("/")}
        >
          <ArrowLeft size={18} />
          Назад к этапам
        </button>

        <header className="retention-page__header">
          <div>
            <span>Этап 5</span>
            <h1>Закрепление</h1>
            <p>
              Месяц 3–12: итоговая оценка, HR-аналитика, sentiment-анализ,
              at_risk-флаги, финальный NPS и план развития сотрудника.
            </p>
          </div>

          <div className="retention-page__badge">Месяц 3–12</div>
        </header>

        <section className="retention-hero">
          <div className="retention-hero__icon">
            <DigitalBuddyCharacter mood="talking" size={72} variant="standing" />
          </div>

          <div>
            <span>Digital Buddy анализирует адаптацию</span>
            <h2>HR видит прогресс, риски и итоговый статус без личной переписки</h2>
            <p>{employeeDetail.privacy_note}</p>
          </div>
        </section>

        <section className="retention-page__grid">
          <div className="retention-page__main">
            <section className="retention-summary">
              <article className="retention-summary__card">
                <BarChart3 size={26} />
                <span>Маршрут</span>
                <strong>{employee.progress}%</strong>
              </article>

              <article className="retention-summary__card">
                <ClipboardCheck size={26} />
                <span>Задачи</span>
                <strong>
                  {employee.completed_tasks}/{employee.total_tasks}
                </strong>
              </article>

              <article className="retention-summary__card">
                <FileText size={26} />
                <span>Финальный NPS</span>
                <strong>{finalNps}/10</strong>
              </article>

              <article className="retention-summary__card">
                <Database size={26} />
                <span>Риск</span>
                <strong>{employee.risk_level}</strong>
              </article>
            </section>

            <section className="retention-section">
              <div className="retention-section__header">
                <div>
                  <span>Sentiment-анализ</span>
                  <h2>Динамика тональности по неделям</h2>
                </div>
              </div>

              <SentimentChart data={sentimentWeeks} />
            </section>

            <section className="final-nps-section">
              <div className="final-nps-section__header">
                <div>
                  <span>Final NPS</span>
                  <h2>Итоговая оценка адаптации</h2>
                </div>
              </div>

              <article className="final-nps-card">
                {surveySummary?.final_nps_completed ? (
                  <div className="final-nps-card__done">
                    <strong>Final NPS уже отправлен</strong>
                    <span>
                      Последняя NPS-оценка: {surveySummary.latest_nps ?? "—"}/10
                    </span>
                  </div>
                ) : (
                  <>
                    <div className="final-nps-card__score">
                      <span>Оценка</span>
                      <strong>{finalNpsScore}/10</strong>
                    </div>

                    <input
                      type="range"
                      min="0"
                      max="10"
                      value={finalNpsScore}
                      onChange={(event) =>
                        setFinalNpsScore(Number(event.target.value))
                      }
                    />

                    <textarea
                      value={finalNpsComment}
                      onChange={(event) => setFinalNpsComment(event.target.value)}
                      placeholder="Комментарий к итоговой адаптации"
                    />

                    <button
                      type="button"
                      disabled={isSubmittingFinalNps}
                      onClick={handleSubmitFinalNps}
                    >
                      {isSubmittingFinalNps ? "Отправка..." : "Отправить Final NPS"}
                    </button>
                  </>
                )}
              </article>
            </section>

            <section className="retention-section">
              <div className="retention-section__header">
                <div>
                  <span>at_risk</span>
                  <h2>Флаги риска адаптации</h2>
                </div>
              </div>

              <div className="retention-section__cards">
                {riskFlags.map((risk) => (
                  <RiskFlagCard key={risk.id} risk={risk} />
                ))}
              </div>
            </section>

            <section className="retention-section">
              <div className="retention-section__header">
                <div>
                  <span>Развитие</span>
                  <h2>Рекомендации Digital Buddy</h2>
                </div>
              </div>

              <div className="retention-section__cards">
                {developmentRecommendations.map((item) => (
                  <DevelopmentCard key={item.id} item={item} />
                ))}
              </div>
            </section>
          </div>

          <aside className="retention-page__sidebar">
            <ProgressBar
              completed={employee.completed_tasks}
              total={employee.total_tasks || 1}
            />

            <div className="retention-info-card">
              <h3>HR-отчёт на 90-й день</h3>
              <p>{employeeDetail.hr_summary}</p>
            </div>

            <div className="retention-info-card">
              <h3>Активные риски</h3>
              <p>
                Сейчас активных риск-флагов: <strong>{activeRiskCount}</strong>.
                HR должен получить мягкий сигнал для дополнительного контакта.
              </p>
            </div>

            <div className="retention-info-card retention-info-card--success">
              <h3>Передача в HR-аналитику</h3>
              <p>
                Данные маршрута, опросов и sentiment готовы к передаче в
                HR-аналитику KMG. Личная переписка не передаётся.
              </p>
            </div>
          </aside>
        </section>
      </div>
    </main>
  );
}
