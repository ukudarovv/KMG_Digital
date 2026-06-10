import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FileText, Plus } from "lucide-react";
import { hrDocumentsApi, type HrDocument } from "../../api/hrDocumentsApi";
import { HR_ROUTES } from "../../routes/hrRoutes";
import "./HRAdminShared.css";

export const DOC_STATUS_LABELS: Record<
  string,
  { label: string; tone: string }
> = {
  draft: { label: "Черновик", tone: "" },
  in_review: { label: "На согласовании", tone: "hra-badge--yellow" },
  approved: { label: "Согласован", tone: "hra-badge--blue" },
  rejected: { label: "Отклонён", tone: "hra-badge--red" },
  signed: { label: "Подписан", tone: "hra-badge--green" },
  archived: { label: "В архиве", tone: "hra-badge--navy" },
};

export const DOC_TYPE_LABELS: Record<string, string> = {
  employment_contract: "Трудовой договор",
  nda: "NDA",
  order: "Приказ",
  policy: "Политика / регламент",
  other: "Прочее",
};

const FILTERS = [
  { value: "", label: "Все" },
  { value: "draft", label: "Черновики" },
  { value: "in_review", label: "На согласовании" },
  { value: "approved", label: "Согласованные" },
  { value: "signed", label: "Подписанные" },
  { value: "archived", label: "Архив" },
];

export function DocumentsListPage() {
  const [documents, setDocuments] = useState<HrDocument[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsLoading(true);
    hrDocumentsApi
      .getAll(statusFilter ? { status: statusFilter } : undefined)
      .then(setDocuments)
      .catch(() => setError("Не удалось загрузить реестр документов."))
      .finally(() => setIsLoading(false));
  }, [statusFilter]);

  return (
    <main className="hra-page">
      <div className="hra-container">
        <header className="hra-header">
          <div>
            <span>HR Admin</span>
            <h1>Документооборот</h1>
            <p>
              Реестр кадровых документов: версии, маршруты согласования,
              подпись и архив.
            </p>
          </div>

          <div className="hra-header__actions">
            <Link className="hra-btn" to={HR_ROUTES.documentNew}>
              <Plus size={16} />
              Загрузить документ
            </Link>
          </div>
        </header>

        {error && <div className="hra-alert hra-alert--error">{error}</div>}

        <div className="hra-tabs">
          {FILTERS.map((filter) => (
            <button
              key={filter.value}
              type="button"
              className={statusFilter === filter.value ? "is-active" : ""}
              onClick={() => setStatusFilter(filter.value)}
            >
              {filter.label}
            </button>
          ))}
        </div>

        <section className="hra-card">
          {isLoading ? (
            <div className="hra-empty">Загрузка...</div>
          ) : documents.length === 0 ? (
            <div className="hra-empty">Документов нет.</div>
          ) : (
            <table className="hra-table">
              <thead>
                <tr>
                  <th>Документ</th>
                  <th>Тип</th>
                  <th>Сотрудник</th>
                  <th>Версия</th>
                  <th>Статус</th>
                  <th>Обновлён</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((document) => {
                  const status =
                    DOC_STATUS_LABELS[document.status] ?? {
                      label: document.status,
                      tone: "",
                    };

                  return (
                    <tr key={document.id}>
                      <td>
                        <Link
                          className="hra-link"
                          to={HR_ROUTES.document(document.id)}
                        >
                          <FileText
                            size={14}
                            style={{ verticalAlign: "-2px", marginRight: 6 }}
                          />
                          {document.title}
                        </Link>
                      </td>
                      <td>
                        {DOC_TYPE_LABELS[document.doc_type] ?? document.doc_type}
                      </td>
                      <td>{document.owner_employee_name || "—"}</td>
                      <td>v{document.current_version_no}</td>
                      <td>
                        <span className={`hra-badge ${status.tone}`}>
                          {status.label}
                        </span>
                      </td>
                      <td>
                        {new Date(document.updated_at).toLocaleDateString("ru-RU")}
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
