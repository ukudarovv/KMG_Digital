import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  Archive,
  ArrowLeft,
  CheckCircle2,
  Download,
  PenLine,
  Send,
  Upload,
  XCircle,
} from "lucide-react";
import {
  hrDocumentsApi,
  type HrDocumentDetail,
  type HrWorkflow,
} from "../../api/hrDocumentsApi";
import { HR_ROUTES } from "../../routes/hrRoutes";
import { DOC_STATUS_LABELS, DOC_TYPE_LABELS } from "./DocumentsListPage";
import "./HRAdminShared.css";

const ROLE_LABELS: Record<string, string> = {
  hr: "HR",
  manager: "Руководитель",
  employee: "Сотрудник",
  signer: "Подписант",
};

const ACTOR = "HR — Айгуль";

export function DocumentDetailPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const documentId = Number(id);

  const [doc, setDoc] = useState<HrDocumentDetail | null>(null);
  const [workflows, setWorkflows] = useState<HrWorkflow[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<number | null>(null);
  const [comment, setComment] = useState("");
  const [newVersionFile, setNewVersionFile] = useState<File | null>(null);
  const [isBusy, setIsBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    hrDocumentsApi
      .getById(documentId)
      .then(setDoc)
      .catch(() => setError("Не удалось загрузить документ."));
  }, [documentId]);

  useEffect(() => {
    load();
    hrDocumentsApi
      .getWorkflows()
      .then((items) => {
        setWorkflows(items);
        if (items.length > 0) {
          setSelectedWorkflow(items[0].id);
        }
      })
      .catch(() => {});
  }, [load]);

  const runAction = async (action: () => Promise<HrDocumentDetail>) => {
    setIsBusy(true);
    setError(null);
    try {
      const updated = await action();
      setDoc(updated);
      setComment("");
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? "Действие не выполнено.";
      setError(detail);
    } finally {
      setIsBusy(false);
    }
  };

  if (!doc) {
    return (
      <main className="hra-page">
        <div className="hra-container">
          {error ? (
            <div className="hra-alert hra-alert--error">{error}</div>
          ) : (
            <div className="hra-empty">Загрузка документа...</div>
          )}
        </div>
      </main>
    );
  }

  const status = DOC_STATUS_LABELS[doc.status] ?? { label: doc.status, tone: "" };

  return (
    <main className="hra-page">
      <div className="hra-container">
        <header className="hra-header">
          <div>
            <span>Документооборот</span>
            <h1>{doc.title}</h1>
            <p>
              {DOC_TYPE_LABELS[doc.doc_type] ?? doc.doc_type}
              {doc.owner_employee_name
                ? ` · Сотрудник: ${doc.owner_employee_name}`
                : ""}
            </p>
          </div>

          <div className="hra-header__actions">
            <button
              type="button"
              className="hra-btn hra-btn--secondary"
              onClick={() => navigate(HR_ROUTES.documents)}
            >
              <ArrowLeft size={15} />
              К реестру
            </button>
          </div>
        </header>

        {error && <div className="hra-alert hra-alert--error">{error}</div>}

        <section className="hra-card">
          <div className="hra-meta">
            <div>
              <span>Статус</span>
              <strong>
                <span className={`hra-badge ${status.tone}`}>{status.label}</span>
              </strong>
            </div>
            <div>
              <span>Текущая версия</span>
              <strong>v{doc.current_version_no}</strong>
            </div>
            <div>
              <span>Маршрут</span>
              <strong>{doc.workflow_name ?? "Не назначен"}</strong>
            </div>
            {doc.status === "in_review" && (
              <div>
                <span>Текущий шаг</span>
                <strong>
                  {doc.current_step_order}.{" "}
                  {ROLE_LABELS[doc.current_step_role ?? ""] ??
                    doc.current_step_role}
                </strong>
              </div>
            )}
          </div>
        </section>

        {(doc.status === "draft" || doc.status === "rejected") && (
          <section className="hra-card">
            <h2>Отправить на согласование</h2>
            <div className="hra-form">
              <div className="hra-form__field">
                <label htmlFor="workflow">Маршрут согласования</label>
                <select
                  id="workflow"
                  value={selectedWorkflow ?? ""}
                  onChange={(event) =>
                    setSelectedWorkflow(Number(event.target.value))
                  }
                >
                  {workflows.map((workflow) => (
                    <option key={workflow.id} value={workflow.id}>
                      {workflow.name} (
                      {workflow.steps
                        .map((step) => ROLE_LABELS[step.role] ?? step.role)
                        .join(" → ")}
                      )
                    </option>
                  ))}
                </select>
              </div>

              <div className="hra-form__actions">
                <button
                  type="button"
                  className="hra-btn"
                  disabled={isBusy || !selectedWorkflow}
                  onClick={() =>
                    runAction(() =>
                      hrDocumentsApi.submit(doc.id, selectedWorkflow!)
                    )
                  }
                >
                  <Send size={15} />
                  Отправить на согласование
                </button>
              </div>
            </div>

            <h3 style={{ marginTop: 18 }}>Загрузить новую версию</h3>
            <div className="hra-form">
              <div className="hra-form__field">
                <label htmlFor="version-file">Файл</label>
                <input
                  id="version-file"
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={(event) =>
                    setNewVersionFile(event.target.files?.[0] ?? null)
                  }
                />
              </div>
              <div className="hra-form__actions">
                <button
                  type="button"
                  className="hra-btn hra-btn--secondary"
                  disabled={isBusy || !newVersionFile}
                  onClick={() =>
                    runAction(() =>
                      hrDocumentsApi.addVersion(doc.id, {
                        file: newVersionFile!,
                        uploaded_by: ACTOR,
                      })
                    )
                  }
                >
                  <Upload size={15} />
                  Загрузить версию
                </button>
              </div>
            </div>
          </section>
        )}

        {(doc.status === "in_review" || doc.status === "approved") && (
          <section className="hra-card">
            <h2>
              {doc.status === "in_review" ? "Решение по шагу" : "Подписание"}
            </h2>
            <div className="hra-form">
              <div className="hra-form__field hra-form__field--full">
                <label htmlFor="decision-comment">Комментарий</label>
                <textarea
                  id="decision-comment"
                  value={comment}
                  onChange={(event) => setComment(event.target.value)}
                  placeholder="Комментарий к решению (необязательно)"
                />
              </div>

              <div className="hra-form__actions">
                {doc.status === "in_review" && (
                  <>
                    <button
                      type="button"
                      className="hra-btn"
                      disabled={isBusy}
                      onClick={() =>
                        runAction(() =>
                          hrDocumentsApi.approve(doc.id, {
                            actor: ACTOR,
                            comment: comment || undefined,
                          })
                        )
                      }
                    >
                      <CheckCircle2 size={15} />
                      Согласовать
                    </button>
                    <button
                      type="button"
                      className="hra-btn hra-btn--danger"
                      disabled={isBusy}
                      onClick={() =>
                        runAction(() =>
                          hrDocumentsApi.reject(doc.id, {
                            actor: ACTOR,
                            comment: comment || undefined,
                          })
                        )
                      }
                    >
                      <XCircle size={15} />
                      Отклонить
                    </button>
                  </>
                )}

                {doc.status === "approved" && (
                  <button
                    type="button"
                    className="hra-btn"
                    disabled={isBusy}
                    onClick={() =>
                      runAction(() =>
                        hrDocumentsApi.sign(doc.id, {
                          actor: ACTOR,
                          comment: comment || undefined,
                        })
                      )
                    }
                  >
                    <PenLine size={15} />
                    Подписать
                  </button>
                )}
              </div>
            </div>
          </section>
        )}

        {doc.status === "signed" && (
          <section className="hra-card">
            <h2>Архивирование</h2>
            <button
              type="button"
              className="hra-btn hra-btn--secondary"
              disabled={isBusy}
              onClick={() => runAction(() => hrDocumentsApi.archive(doc.id))}
            >
              <Archive size={15} />
              Отправить в архив
            </button>
          </section>
        )}

        {doc.workflow_steps.length > 0 && (
          <section className="hra-card">
            <h2>Маршрут согласования</h2>
            <ul className="hra-timeline">
              {doc.workflow_steps.map((step) => {
                const decision = doc.approvals.find(
                  (approval) =>
                    approval.step_order === step.step_order &&
                    approval.decision !== "signed"
                );
                const isCurrent =
                  doc.status === "in_review" &&
                  doc.current_step_order === step.step_order;
                const cls = decision
                  ? decision.decision === "approved"
                    ? "is-done"
                    : "is-rejected"
                  : isCurrent
                  ? "is-current"
                  : "";

                return (
                  <li key={step.id} className={cls}>
                    <strong>
                      Шаг {step.step_order}: {ROLE_LABELS[step.role] ?? step.role}
                      {step.approver_name ? ` — ${step.approver_name}` : ""}
                    </strong>
                    <small>
                      {decision
                        ? `${
                            decision.decision === "approved"
                              ? "Согласовано"
                              : "Отклонено"
                          } · ${decision.actor ?? ""} · ${new Date(
                            decision.created_at
                          ).toLocaleString("ru-RU")}${
                            decision.comment ? ` · ${decision.comment}` : ""
                          }`
                        : isCurrent
                        ? "Ожидает решения"
                        : "Ожидание"}
                    </small>
                  </li>
                );
              })}
            </ul>
          </section>
        )}

        <section className="hra-card">
          <h2>Версии</h2>
          <table className="hra-table">
            <thead>
              <tr>
                <th>Версия</th>
                <th>Файл</th>
                <th>Загрузил</th>
                <th>Комментарий</th>
                <th>Дата</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {doc.versions.map((version) => (
                <tr key={version.id}>
                  <td>v{version.version_no}</td>
                  <td>{version.file_name}</td>
                  <td>{version.uploaded_by || "—"}</td>
                  <td>{version.comment || "—"}</td>
                  <td>
                    {new Date(version.created_at).toLocaleString("ru-RU")}
                  </td>
                  <td>
                    <a
                      className="hra-btn hra-btn--secondary"
                      href={hrDocumentsApi.fileUrl(doc.id, version.version_no)}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <Download size={14} />
                      Скачать
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>
    </main>
  );
}
