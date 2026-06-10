import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Upload } from "lucide-react";
import { employeeApi, type Employee } from "../../api/employeeApi";
import { hrDocumentsApi } from "../../api/hrDocumentsApi";
import { HR_ROUTES } from "../../routes/hrRoutes";
import { DOC_TYPE_LABELS } from "./DocumentsListPage";
import "./HRAdminShared.css";

export function DocumentNewPage() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [docType, setDocType] = useState("employment_contract");
  const [employeeId, setEmployeeId] = useState<number | null>(null);
  const [comment, setComment] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    employeeApi.getAll().then(setEmployees).catch(() => {});
  }, []);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!file) {
      setError("Прикрепите файл документа (PDF, DOC, DOCX).");
      return;
    }
    if (!title.trim()) {
      setError("Укажите название документа.");
      return;
    }

    setIsSaving(true);
    setError(null);
    try {
      const document = await hrDocumentsApi.create({
        title,
        doc_type: docType,
        owner_employee_id: employeeId,
        uploaded_by: "HR — Айгуль",
        comment: comment || undefined,
        file,
      });
      navigate(HR_ROUTES.document(document.id));
    } catch {
      setError("Не удалось загрузить документ. Проверьте формат и размер (до 10 МБ).");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <main className="hra-page">
      <div className="hra-container">
        <header className="hra-header">
          <div>
            <span>HR Admin</span>
            <h1>Новый документ</h1>
            <p>
              Загрузите документ, привяжите его к сотруднику и отправьте на
              согласование из карточки документа.
            </p>
          </div>

          <div className="hra-header__actions">
            <button
              type="button"
              className="hra-btn hra-btn--secondary"
              onClick={() => navigate(HR_ROUTES.documents)}
            >
              <ArrowLeft size={15} />
              Назад
            </button>
          </div>
        </header>

        {error && <div className="hra-alert hra-alert--error">{error}</div>}

        <section className="hra-card">
          <form className="hra-form" onSubmit={handleSubmit}>
            <div className="hra-form__field">
              <label htmlFor="title">Название документа *</label>
              <input
                id="title"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="Трудовой договор — Иванов И.И."
                required
              />
            </div>

            <div className="hra-form__field">
              <label htmlFor="doc_type">Тип документа</label>
              <select
                id="doc_type"
                value={docType}
                onChange={(event) => setDocType(event.target.value)}
              >
                {Object.entries(DOC_TYPE_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            <div className="hra-form__field">
              <label htmlFor="employee">Сотрудник</label>
              <select
                id="employee"
                value={employeeId ?? ""}
                onChange={(event) =>
                  setEmployeeId(
                    event.target.value ? Number(event.target.value) : null
                  )
                }
              >
                <option value="">— Без привязки —</option>
                {employees.map((employee) => (
                  <option key={employee.id} value={employee.id}>
                    {employee.full_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="hra-form__field">
              <label htmlFor="file">Файл (PDF, DOC, DOCX, до 10 МБ) *</label>
              <input
                id="file"
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                required
              />
            </div>

            <div className="hra-form__field hra-form__field--full">
              <label htmlFor="comment">Комментарий к версии</label>
              <textarea
                id="comment"
                value={comment}
                onChange={(event) => setComment(event.target.value)}
                placeholder="Первая версия документа"
              />
            </div>

            <div className="hra-form__actions">
              <button type="submit" className="hra-btn" disabled={isSaving}>
                <Upload size={15} />
                {isSaving ? "Загрузка..." : "Загрузить документ"}
              </button>
            </div>
          </form>
        </section>
      </div>
    </main>
  );
}
