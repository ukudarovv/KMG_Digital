import { useEffect, useState } from "react";
import { Plus, Save } from "lucide-react";
import {
  employeeApi,
  type Department,
  type DepartmentPayload,
} from "../../api/employeeApi";
import { hrDocumentsApi, type HrWorkflow } from "../../api/hrDocumentsApi";
import {
  recruitingApi,
  type RecruitingSettings,
} from "../../api/recruitingApi";
import "./HRAdminShared.css";

type Tab = "departments" | "workflows" | "ai";

const ROLE_LABELS: Record<string, string> = {
  hr: "HR",
  manager: "Руководитель",
  employee: "Сотрудник",
  signer: "Подписант",
};

const EMPTY_DEPARTMENT: DepartmentPayload = {
  code: "",
  name: "",
  description: "",
  competencies: "",
};

export function HRSettingsPage() {
  const [tab, setTab] = useState<Tab>("departments");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [departments, setDepartments] = useState<Department[]>([]);
  const [editing, setEditing] = useState<Department | null>(null);
  const [departmentForm, setDepartmentForm] =
    useState<DepartmentPayload>(EMPTY_DEPARTMENT);

  const [workflows, setWorkflows] = useState<HrWorkflow[]>([]);
  const [workflowName, setWorkflowName] = useState("");
  const [workflowSteps, setWorkflowSteps] = useState<string[]>(["hr"]);

  const [aiSettings, setAiSettings] = useState<RecruitingSettings | null>(null);

  const notify = (message: string) => {
    setSuccess(message);
    setError(null);
    setTimeout(() => setSuccess(null), 3000);
  };

  const loadDepartments = () => {
    employeeApi.getDepartments().then(setDepartments).catch(() => {});
  };

  useEffect(() => {
    loadDepartments();
    hrDocumentsApi.getWorkflows().then(setWorkflows).catch(() => {});
    recruitingApi.getSettings().then(setAiSettings).catch(() => {});
  }, []);

  const startEditDepartment = (department: Department) => {
    setEditing(department);
    setDepartmentForm({
      code: department.code,
      name: department.name,
      description: department.description ?? "",
      competencies: department.competencies ?? "",
      is_active: department.is_active,
    });
  };

  const saveDepartment = async () => {
    if (!departmentForm.code.trim() || !departmentForm.name.trim()) {
      setError("Укажите код и название отдела.");
      return;
    }
    try {
      if (editing) {
        await employeeApi.updateDepartment(editing.id, departmentForm);
        notify("Отдел обновлён.");
      } else {
        await employeeApi.createDepartment(departmentForm);
        notify("Отдел создан.");
      }
      setEditing(null);
      setDepartmentForm(EMPTY_DEPARTMENT);
      loadDepartments();
    } catch {
      setError("Не удалось сохранить отдел (код должен быть уникальным).");
    }
  };

  const createWorkflow = async () => {
    if (!workflowName.trim() || workflowSteps.length === 0) {
      setError("Укажите название маршрута и хотя бы один шаг.");
      return;
    }
    try {
      await hrDocumentsApi.createWorkflow({
        name: workflowName,
        steps: workflowSteps.map((role, index) => ({
          step_order: index + 1,
          role,
          approver_name: ROLE_LABELS[role],
        })),
      });
      setWorkflowName("");
      setWorkflowSteps(["hr"]);
      hrDocumentsApi.getWorkflows().then(setWorkflows).catch(() => {});
      notify("Маршрут создан.");
    } catch {
      setError("Не удалось создать маршрут.");
    }
  };

  const saveAiSettings = async () => {
    if (!aiSettings) {
      return;
    }
    try {
      const updated = await recruitingApi.updateSettings(aiSettings);
      setAiSettings(updated);
      notify("Настройки ИИ сохранены.");
    } catch {
      setError("Не удалось сохранить настройки ИИ.");
    }
  };

  return (
    <main className="hra-page">
      <div className="hra-container">
        <header className="hra-header">
          <div>
            <span>HR Admin</span>
            <h1>Настройки</h1>
            <p>
              Отделы и их компетенции для AI-подбора, маршруты согласования
              документов и параметры рекрутинг-ИИ.
            </p>
          </div>
        </header>

        {error && <div className="hra-alert hra-alert--error">{error}</div>}
        {success && <div className="hra-alert hra-alert--success">{success}</div>}

        <div className="hra-tabs">
          <button
            type="button"
            className={tab === "departments" ? "is-active" : ""}
            onClick={() => setTab("departments")}
          >
            Отделы
          </button>
          <button
            type="button"
            className={tab === "workflows" ? "is-active" : ""}
            onClick={() => setTab("workflows")}
          >
            Маршруты согласования
          </button>
          <button
            type="button"
            className={tab === "ai" ? "is-active" : ""}
            onClick={() => setTab("ai")}
          >
            AI-рекрутинг
          </button>
        </div>

        {tab === "departments" && (
          <>
            <section className="hra-card">
              <h2>{editing ? `Редактирование: ${editing.name}` : "Новый отдел"}</h2>
              <div className="hra-form">
                <div className="hra-form__field">
                  <label htmlFor="dep-code">Код *</label>
                  <input
                    id="dep-code"
                    value={departmentForm.code}
                    onChange={(event) =>
                      setDepartmentForm((prev) => ({
                        ...prev,
                        code: event.target.value.toUpperCase(),
                      }))
                    }
                    placeholder="IT"
                  />
                </div>
                <div className="hra-form__field">
                  <label htmlFor="dep-name">Название *</label>
                  <input
                    id="dep-name"
                    value={departmentForm.name}
                    onChange={(event) =>
                      setDepartmentForm((prev) => ({
                        ...prev,
                        name: event.target.value,
                      }))
                    }
                    placeholder="Департамент информационных технологий"
                  />
                </div>
                <div className="hra-form__field hra-form__field--full">
                  <label htmlFor="dep-desc">Описание</label>
                  <textarea
                    id="dep-desc"
                    value={departmentForm.description ?? ""}
                    onChange={(event) =>
                      setDepartmentForm((prev) => ({
                        ...prev,
                        description: event.target.value,
                      }))
                    }
                  />
                </div>
                <div className="hra-form__field hra-form__field--full">
                  <label htmlFor="dep-comp">
                    Компетенции для AI-подбора (через запятую)
                  </label>
                  <textarea
                    id="dep-comp"
                    value={departmentForm.competencies ?? ""}
                    onChange={(event) =>
                      setDepartmentForm((prev) => ({
                        ...prev,
                        competencies: event.target.value,
                      }))
                    }
                    placeholder="разработка ПО, Python, SQL, DevOps"
                  />
                </div>
                <div className="hra-form__actions">
                  <button type="button" className="hra-btn" onClick={saveDepartment}>
                    <Save size={15} />
                    {editing ? "Сохранить" : "Создать отдел"}
                  </button>
                  {editing && (
                    <button
                      type="button"
                      className="hra-btn hra-btn--secondary"
                      onClick={() => {
                        setEditing(null);
                        setDepartmentForm(EMPTY_DEPARTMENT);
                      }}
                    >
                      Отмена
                    </button>
                  )}
                </div>
              </div>
            </section>

            <section className="hra-card">
              <h2>Список отделов</h2>
              <table className="hra-table">
                <thead>
                  <tr>
                    <th>Код</th>
                    <th>Название</th>
                    <th>Компетенции</th>
                    <th>Статус</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {departments.map((department) => (
                    <tr key={department.id}>
                      <td>{department.code}</td>
                      <td>{department.name}</td>
                      <td style={{ maxWidth: 380, color: "#64748b", fontSize: 13 }}>
                        {department.competencies || "—"}
                      </td>
                      <td>
                        <span
                          className={`hra-badge ${
                            department.is_active
                              ? "hra-badge--green"
                              : "hra-badge--red"
                          }`}
                        >
                          {department.is_active ? "Активен" : "Отключён"}
                        </span>
                      </td>
                      <td>
                        <button
                          type="button"
                          className="hra-btn hra-btn--secondary"
                          onClick={() => startEditDepartment(department)}
                        >
                          Изменить
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          </>
        )}

        {tab === "workflows" && (
          <>
            <section className="hra-card">
              <h2>Новый маршрут согласования</h2>
              <div className="hra-form">
                <div className="hra-form__field">
                  <label htmlFor="wf-name">Название *</label>
                  <input
                    id="wf-name"
                    value={workflowName}
                    onChange={(event) => setWorkflowName(event.target.value)}
                    placeholder="Согласование приказа"
                  />
                </div>
                <div className="hra-form__field hra-form__field--full">
                  <label>Шаги маршрута (по порядку)</label>
                  {workflowSteps.map((role, index) => (
                    <div key={index} style={{ display: "flex", gap: 8 }}>
                      <select
                        value={role}
                        style={{ flex: 1, minHeight: 42, borderRadius: 12, border: "1px solid #cbd5e1", padding: "8px 12px" }}
                        onChange={(event) =>
                          setWorkflowSteps((prev) =>
                            prev.map((item, itemIndex) =>
                              itemIndex === index ? event.target.value : item
                            )
                          )
                        }
                      >
                        {Object.entries(ROLE_LABELS).map(([value, label]) => (
                          <option key={value} value={value}>
                            Шаг {index + 1}: {label}
                          </option>
                        ))}
                      </select>
                      <button
                        type="button"
                        className="hra-btn hra-btn--secondary"
                        onClick={() =>
                          setWorkflowSteps((prev) =>
                            prev.filter((_, itemIndex) => itemIndex !== index)
                          )
                        }
                      >
                        Удалить
                      </button>
                    </div>
                  ))}
                  <button
                    type="button"
                    className="hra-btn hra-btn--secondary"
                    style={{ alignSelf: "flex-start" }}
                    onClick={() => setWorkflowSteps((prev) => [...prev, "manager"])}
                  >
                    <Plus size={14} />
                    Добавить шаг
                  </button>
                </div>
                <div className="hra-form__actions">
                  <button type="button" className="hra-btn" onClick={createWorkflow}>
                    <Save size={15} />
                    Создать маршрут
                  </button>
                </div>
              </div>
            </section>

            <section className="hra-card">
              <h2>Существующие маршруты</h2>
              {workflows.map((workflow) => (
                <article
                  key={workflow.id}
                  style={{
                    padding: "12px 0",
                    borderBottom: "1px solid #f1f5f9",
                  }}
                >
                  <h3 style={{ marginBottom: 4 }}>{workflow.name}</h3>
                  <p style={{ margin: 0, color: "#64748b", fontSize: 13 }}>
                    {workflow.steps
                      .map(
                        (step) =>
                          `${step.step_order}. ${
                            ROLE_LABELS[step.role] ?? step.role
                          }`
                      )
                      .join(" → ")}
                  </p>
                </article>
              ))}
            </section>
          </>
        )}

        {tab === "ai" && aiSettings && (
          <section className="hra-card">
            <h2>Параметры AI-рекрутинга</h2>

            <div className="hra-meta" style={{ marginBottom: 18 }}>
              <div>
                <span>Внешний сервис скрининга (AI-CheckResume)</span>
                <strong>
                  <span
                    className={`hra-badge ${
                      aiSettings.screening_service_available
                        ? "hra-badge--green"
                        : "hra-badge--red"
                    }`}
                  >
                    {aiSettings.screening_service_available
                      ? "Доступен"
                      : aiSettings.screening_service_url
                      ? "Недоступен"
                      : "Не настроен"}
                  </span>
                </strong>
              </div>
              {aiSettings.screening_service_url && (
                <div>
                  <span>URL сервиса</span>
                  <strong>{aiSettings.screening_service_url}</strong>
                </div>
              )}
            </div>

            <div className="hra-form">
              <div className="hra-form__field">
                <label htmlFor="ai-enabled">LLM-анализ</label>
                <select
                  id="ai-enabled"
                  value={aiSettings.llm_enabled ? "1" : "0"}
                  onChange={(event) =>
                    setAiSettings((prev) =>
                      prev
                        ? { ...prev, llm_enabled: event.target.value === "1" }
                        : prev
                    )
                  }
                >
                  <option value="1">Включён (Ollama)</option>
                  <option value="0">Выключен (keyword-matching)</option>
                </select>
              </div>

              <div className="hra-form__field">
                <label htmlFor="ai-topn">Количество отделов в подборе</label>
                <input
                  id="ai-topn"
                  type="number"
                  min={1}
                  max={10}
                  value={aiSettings.top_n}
                  onChange={(event) =>
                    setAiSettings((prev) =>
                      prev
                        ? { ...prev, top_n: Number(event.target.value) || 3 }
                        : prev
                    )
                  }
                />
              </div>

              <div className="hra-form__field">
                <label htmlFor="ai-minscore">Минимальный score (порог)</label>
                <input
                  id="ai-minscore"
                  type="number"
                  min={0}
                  max={100}
                  value={aiSettings.min_score}
                  onChange={(event) =>
                    setAiSettings((prev) =>
                      prev
                        ? { ...prev, min_score: Number(event.target.value) || 0 }
                        : prev
                    )
                  }
                />
              </div>

              <div className="hra-form__field hra-form__field--full">
                <label htmlFor="ai-prompt">
                  Системный промпт для подбора отдела (пусто — стандартный)
                </label>
                <textarea
                  id="ai-prompt"
                  rows={5}
                  value={aiSettings.prompt_template ?? ""}
                  onChange={(event) =>
                    setAiSettings((prev) =>
                      prev
                        ? {
                            ...prev,
                            prompt_template: event.target.value || null,
                          }
                        : prev
                    )
                  }
                  placeholder="Вы — HR-эксперт по подбору персонала..."
                />
              </div>

              <div className="hra-form__actions">
                <button type="button" className="hra-btn" onClick={saveAiSettings}>
                  <Save size={15} />
                  Сохранить настройки
                </button>
              </div>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
