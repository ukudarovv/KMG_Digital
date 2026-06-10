import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BrainCircuit, UserRound } from "lucide-react";
import { recruitingApi, type Candidate } from "../../api/recruitingApi";
import { HR_ROUTES } from "../../routes/hrRoutes";
import "./HRAdminShared.css";

export const CANDIDATE_STATUS_LABELS: Record<
  string,
  { label: string; tone: string }
> = {
  new: { label: "Новый", tone: "" },
  analyzed: { label: "Проанализирован", tone: "hra-badge--blue" },
  hired: { label: "Принят", tone: "hra-badge--green" },
  rejected: { label: "Отклонён", tone: "hra-badge--red" },
};

export function RecruitingListPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    recruitingApi
      .getCandidates()
      .then(setCandidates)
      .catch(() => setError("Не удалось загрузить кандидатов."))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <main className="hra-page">
      <div className="hra-container">
        <header className="hra-header">
          <div>
            <span>HR Admin</span>
            <h1>Рекрутинг AI</h1>
            <p>
              Загрузите резюме — ИИ извлечёт профиль кандидата и предложит
              наиболее подходящие отделы с обоснованием.
            </p>
          </div>

          <div className="hra-header__actions">
            <Link className="hra-btn" to={HR_ROUTES.recruitingAnalyze}>
              <BrainCircuit size={16} />
              Анализ резюме
            </Link>
          </div>
        </header>

        {error && <div className="hra-alert hra-alert--error">{error}</div>}

        <section className="hra-card">
          {isLoading ? (
            <div className="hra-empty">Загрузка...</div>
          ) : candidates.length === 0 ? (
            <div className="hra-empty">
              Кандидатов пока нет. Загрузите первое резюме для анализа.
            </div>
          ) : (
            <table className="hra-table">
              <thead>
                <tr>
                  <th>Кандидат</th>
                  <th>Контакты</th>
                  <th>Рекомендация ИИ</th>
                  <th>Подтверждённый отдел</th>
                  <th>Статус</th>
                  <th>Дата</th>
                </tr>
              </thead>
              <tbody>
                {candidates.map((candidate) => {
                  const status =
                    CANDIDATE_STATUS_LABELS[candidate.status] ?? {
                      label: candidate.status,
                      tone: "",
                    };

                  return (
                    <tr key={candidate.id}>
                      <td>
                        <Link
                          className="hra-link"
                          to={HR_ROUTES.candidate(candidate.id)}
                        >
                          <UserRound
                            size={14}
                            style={{ verticalAlign: "-2px", marginRight: 6 }}
                          />
                          {candidate.full_name}
                        </Link>
                      </td>
                      <td>
                        {[candidate.email, candidate.phone]
                          .filter(Boolean)
                          .join(" · ") || "—"}
                      </td>
                      <td>
                        {candidate.top_match_department
                          ? `${candidate.top_match_department} (${candidate.top_match_score}%)`
                          : "—"}
                      </td>
                      <td>{candidate.confirmed_department_name || "—"}</td>
                      <td>
                        <span className={`hra-badge ${status.tone}`}>
                          {status.label}
                        </span>
                      </td>
                      <td>
                        {new Date(candidate.created_at).toLocaleDateString(
                          "ru-RU"
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </section>
      </div>
    </main>
  );
}
