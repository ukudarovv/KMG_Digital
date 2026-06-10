import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  BadgeCheck,
  Briefcase,
  GraduationCap,
  UserRoundPlus,
} from "lucide-react";
import { employeeApi, type Department } from "../../api/employeeApi";
import {
  recruitingApi,
  type CandidateDetail,
} from "../../api/recruitingApi";
import { HR_ROUTES } from "../../routes/hrRoutes";
import { CANDIDATE_STATUS_LABELS } from "./RecruitingListPage";
import "./HRAdminShared.css";

function scoreTone(score: number) {
  if (score >= 70) {
    return "";
  }
  if (score >= 40) {
    return "hra-match__score--mid";
  }
  return "hra-match__score--low";
}

const DECISION_LABELS: Record<string, { label: string; tone: string }> = {
  pass: { label: "Рекомендован", tone: "hra-badge--green" },
  review: { label: "Ручная проверка", tone: "hra-badge--yellow" },
  reject: { label: "Не рекомендован", tone: "hra-badge--red" },
};

export function RecruitingCandidatePage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const candidateId = Number(id);

  const [candidate, setCandidate] = useState<CandidateDetail | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [isBusy, setIsBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [hirePosition, setHirePosition] = useState("");
  const [hireManager, setHireManager] = useState("");
  const [hireDate, setHireDate] = useState(
    new Date().toISOString().slice(0, 10)
  );

  const load = useCallback(() => {
    recruitingApi
      .getCandidate(candidateId)
      .then(setCandidate)
      .catch(() => setError("Не удалось загрузить кандидата."));
  }, [candidateId]);

  useEffect(() => {
    load();
    employeeApi.getDepartments().then(setDepartments).catch(() => {});
  }, [load]);

  const confirmDepartment = async (departmentId: number) => {
    setIsBusy(true);
    setError(null);
    try {
      const updated = await recruitingApi.confirmDepartment(
        candidateId,
        departmentId
      );
      setCandidate(updated);
    } catch {
      setError("Не удалось подтвердить отдел.");
    } finally {
      setIsBusy(false);
    }
  };

  const hire = async () => {
    setIsBusy(true);
    setError(null);
    try {
      const employee = await recruitingApi.hire(candidateId, {
        position: hirePosition || undefined,
        manager_name: hireManager || undefined,
        start_date: hireDate,
      });
      navigate(HR_ROUTES.employee(employee.id));
    } catch {
      setError("Не удалось принять кандидата на работу.");
    } finally {
      setIsBusy(false);
    }
  };

  if (!candidate) {
    return (
      <main className="hra-page">
        <div className="hra-container">
          {error ? (
            <div className="hra-alert hra-alert--error">{error}</div>
          ) : (
            <div className="hra-empty">Загрузка кандидата...</div>
          )}
        </div>
      </main>
    );
  }

  const status =
    CANDIDATE_STATUS_LABELS[candidate.status] ?? {
      label: candidate.status,
      tone: "",
    };
  const parsed = candidate.analysis?.parsed_json;
  const matches = candidate.analysis?.matches ?? [];

  return (
    <main className="hra-page">
      <div className="hra-container">
        <header className="hra-header">
          <div>
            <span>Рекрутинг AI</span>
            <h1>{candidate.full_name}</h1>
            <p>
              {[candidate.email, candidate.phone].filter(Boolean).join(" · ") ||
                "Контакты не указаны"}
              {candidate.resume_file_name
                ? ` · Файл: ${candidate.resume_file_name}`
                : ""}
            </p>
          </div>

          <div className="hra-header__actions">
            <button
              type="button"
              className="hra-btn hra-btn--secondary"
              onClick={() => navigate(HR_ROUTES.recruiting)}
            >
              <ArrowLeft size={15} />
              К кандидатам
            </button>
          </div>
        </header>

        {error && <div className="hra-alert hra-alert--error">{error}</div>}

        <section className="hra-card">
          <div className="hra-meta">
            <div>
              <span>Статус</span>
              <strong>
                <span className={`hra-badge ${status.tone}`}>
                  {status.label}
                </span>
              </strong>
            </div>
            <div>
              <span>Опыт</span>
              <strong>
                {parsed?.experience_years != null
                  ? `${parsed.experience_years} лет`
                  : "—"}
              </strong>
            </div>
            <div>
              <span>Подтверждённый отдел</span>
              <strong>{candidate.confirmed_department_name ?? "—"}</strong>
            </div>
            {candidate.hired_employee_id && (
              <div>
                <span>Сотрудник</span>
                <strong>
                  <button
                    type="button"
                    className="hra-link"
                    style={{ border: "none", background: "none", cursor: "pointer", padding: 0, font: "inherit" }}
                    onClick={() =>
                      navigate(HR_ROUTES.employee(candidate.hired_employee_id!))
                    }
                  >
                    Открыть профиль
                  </button>
                </strong>
              </div>
            )}
          </div>
        </section>

        {candidate.analysis?.llm_summary && (
          <section className="hra-card">
            <h2>Резюме кандидата (ИИ)</h2>
            <p style={{ margin: 0, color: "#52616b", lineHeight: 1.55 }}>
              {candidate.analysis.llm_summary}
            </p>
          </section>
        )}

        {parsed && (
          <section className="hra-card">
            <h2>Профиль</h2>
            <div className="hra-grid">
              <div>
                <h3>
                  <Briefcase size={15} style={{ verticalAlign: "-2px" }} />{" "}
                  Навыки
                </h3>
                {parsed.skills && parsed.skills.length > 0 ? (
                  <div className="hra-chips">
                    {parsed.skills.map((skill) => (
                      <span key={skill} className="hra-badge hra-badge--blue">
                        {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: "#64748b" }}>Не извлечены</p>
                )}
              </div>

              <div>
                <h3>
                  <GraduationCap size={15} style={{ verticalAlign: "-2px" }} />{" "}
                  Образование
                </h3>
                <p style={{ color: "#52616b" }}>{parsed.education || "—"}</p>

                {parsed.positions && parsed.positions.length > 0 && (
                  <>
                    <h3 style={{ marginTop: 12 }}>Должности</h3>
                    <p style={{ color: "#52616b" }}>
                      {parsed.positions.join(", ")}
                    </p>
                  </>
                )}
              </div>
            </div>
          </section>
        )}

        <section className="hra-card">
          <h2>Подходящие отделы (рекомендация ИИ)</h2>
          {matches.length === 0 ? (
            <div className="hra-empty">Совпадений не найдено.</div>
          ) : (
            matches.map((match) => (
              <article key={match.id} className="hra-match">
                <div className={`hra-match__score ${scoreTone(match.score)}`}>
                  {match.score}%
                </div>
                <div style={{ flex: 1 }}>
                  <h3 style={{ margin: 0 }}>
                    {match.rank}. {match.department_name}{" "}
                    {match.decision && DECISION_LABELS[match.decision] && (
                      <span
                        className={`hra-badge ${
                          DECISION_LABELS[match.decision].tone
                        }`}
                        style={{ marginLeft: 8, verticalAlign: "2px" }}
                      >
                        {DECISION_LABELS[match.decision].label}
                      </span>
                    )}
                  </h3>
                  <p>{match.reasoning || "Без обоснования."}</p>
                </div>
                {candidate.status !== "hired" && (
                  <button
                    type="button"
                    className={`hra-btn ${
                      candidate.confirmed_department_id === match.department_id
                        ? ""
                        : "hra-btn--secondary"
                    }`}
                    disabled={isBusy}
                    onClick={() => confirmDepartment(match.department_id)}
                  >
                    <BadgeCheck size={15} />
                    {candidate.confirmed_department_id === match.department_id
                      ? "Подтверждён"
                      : "Подтвердить"}
                  </button>
                )}
              </article>
            ))
          )}

          {candidate.status !== "hired" && departments.length > 0 && (
            <div className="hra-form" style={{ marginTop: 10 }}>
              <div className="hra-form__field">
                <label htmlFor="manual-department">
                  Или выберите отдел вручную
                </label>
                <select
                  id="manual-department"
                  value={candidate.confirmed_department_id ?? ""}
                  onChange={(event) => {
                    if (event.target.value) {
                      confirmDepartment(Number(event.target.value));
                    }
                  }}
                >
                  <option value="">— Выбрать отдел —</option>
                  {departments.map((department) => (
                    <option key={department.id} value={department.id}>
                      {department.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </section>

        {candidate.status !== "hired" && (
          <section className="hra-card">
            <h2>Принять на работу</h2>
            <div className="hra-form">
              <div className="hra-form__field">
                <label htmlFor="hire-position">Должность</label>
                <input
                  id="hire-position"
                  value={hirePosition}
                  onChange={(event) => setHirePosition(event.target.value)}
                  placeholder="Специалист"
                />
              </div>
              <div className="hra-form__field">
                <label htmlFor="hire-manager">Руководитель</label>
                <input
                  id="hire-manager"
                  value={hireManager}
                  onChange={(event) => setHireManager(event.target.value)}
                  placeholder="Сапарова Айгуль"
                />
              </div>
              <div className="hra-form__field">
                <label htmlFor="hire-date">Дата выхода</label>
                <input
                  id="hire-date"
                  type="date"
                  value={hireDate}
                  onChange={(event) => setHireDate(event.target.value)}
                />
              </div>

              <div className="hra-form__actions">
                <button
                  type="button"
                  className="hra-btn"
                  disabled={isBusy || !candidate.confirmed_department_id}
                  onClick={hire}
                >
                  <UserRoundPlus size={15} />
                  {candidate.confirmed_department_id
                    ? "Принять на работу"
                    : "Сначала подтвердите отдел"}
                </button>
              </div>
            </div>
          </section>
        )}

        {candidate.extracted_text_preview && (
          <section className="hra-card">
            <h2>Фрагмент резюме</h2>
            <p
              style={{
                margin: 0,
                color: "#64748b",
                fontSize: 13,
                whiteSpace: "pre-wrap",
                lineHeight: 1.5,
              }}
            >
              {candidate.extracted_text_preview}
            </p>
          </section>
        )}
      </div>
    </main>
  );
}
