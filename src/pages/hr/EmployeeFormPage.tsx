import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Save } from "lucide-react";
import {
  employeeApi,
  type Department,
  type EmployeePayload,
} from "../../api/employeeApi";
import { HR_ROUTES } from "../../routes/hrRoutes";
import "./HRAdminShared.css";

const EMPTY_FORM: EmployeePayload = {
  full_name: "",
  email: "",
  position: "",
  department_id: null,
  manager_name: "",
  start_date: new Date().toISOString().slice(0, 10),
  language: "ru",
  status: "active",
  bitrix_user_id: null,
};

export function EmployeeFormPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const isEdit = Boolean(id);

  const [form, setForm] = useState<EmployeePayload>(EMPTY_FORM);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    employeeApi.getDepartments().then(setDepartments).catch(() => {});

    if (isEdit && id) {
      employeeApi
        .getById(Number(id))
        .then((employee) =>
          setForm({
            full_name: employee.full_name,
            email: employee.email ?? "",
            position: employee.position ?? "",
            department_id: employee.department_id ?? null,
            manager_name: employee.manager_name ?? "",
            start_date: employee.start_date,
            language: employee.language,
            status: employee.status,
            bitrix_user_id: employee.bitrix_user_id ?? null,
          })
        )
        .catch(() => setError("Не удалось загрузить сотрудника."));
    }
  }, [id, isEdit]);

  const setField = <K extends keyof EmployeePayload>(
    key: K,
    value: EmployeePayload[K]
  ) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!form.full_name.trim()) {
      setError("Укажите ФИО сотрудника.");
      return;
    }

    setIsSaving(true);
    setError(null);

    const payload: EmployeePayload = {
      ...form,
      email: form.email || null,
      position: form.position || null,
      manager_name: form.manager_name || null,
      bitrix_user_id: form.bitrix_user_id || null,
    };

    try {
      if (isEdit && id) {
        await employeeApi.update(Number(id), payload);
      } else {
        await employeeApi.create(payload);
      }
      navigate(HR_ROUTES.employees);
    } catch {
      setError("Не удалось сохранить сотрудника. Проверьте данные и backend.");
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
            <h1>{isEdit ? "Редактирование сотрудника" : "Новый сотрудник"}</h1>
            <p>
              {isEdit
                ? "Изменение профиля и назначений сотрудника."
                : "При создании автоматически назначаются задачи Дня 1 и маршрут онбординга."}
            </p>
          </div>

          <div className="hra-header__actions">
            <button
              type="button"
              className="hra-btn hra-btn--secondary"
              onClick={() => navigate(HR_ROUTES.employees)}
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
              <label htmlFor="full_name">ФИО *</label>
              <input
                id="full_name"
                value={form.full_name}
                onChange={(event) => setField("full_name", event.target.value)}
                placeholder="Иванов Иван Иванович"
                required
              />
            </div>

            <div className="hra-form__field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={form.email ?? ""}
                onChange={(event) => setField("email", event.target.value)}
                placeholder="ivanov@kmg.kz"
              />
            </div>

            <div className="hra-form__field">
              <label htmlFor="position">Должность</label>
              <input
                id="position"
                value={form.position ?? ""}
                onChange={(event) => setField("position", event.target.value)}
                placeholder="Специалист"
              />
            </div>

            <div className="hra-form__field">
              <label htmlFor="department">Отдел</label>
              <select
                id="department"
                value={form.department_id ?? ""}
                onChange={(event) =>
                  setField(
                    "department_id",
                    event.target.value ? Number(event.target.value) : null
                  )
                }
              >
                <option value="">— Не назначен —</option>
                {departments.map((department) => (
                  <option key={department.id} value={department.id}>
                    {department.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="hra-form__field">
              <label htmlFor="manager">Руководитель</label>
              <input
                id="manager"
                value={form.manager_name ?? ""}
                onChange={(event) =>
                  setField("manager_name", event.target.value)
                }
                placeholder="Сапарова Айгуль"
              />
            </div>

            <div className="hra-form__field">
              <label htmlFor="start_date">Дата выхода *</label>
              <input
                id="start_date"
                type="date"
                value={form.start_date}
                onChange={(event) => setField("start_date", event.target.value)}
                required
              />
            </div>

            <div className="hra-form__field">
              <label htmlFor="language">Язык</label>
              <select
                id="language"
                value={form.language}
                onChange={(event) => setField("language", event.target.value)}
              >
                <option value="ru">Русский</option>
                <option value="kk">Қазақша</option>
              </select>
            </div>

            <div className="hra-form__field">
              <label htmlFor="status">Статус</label>
              <select
                id="status"
                value={form.status}
                onChange={(event) => setField("status", event.target.value)}
              >
                <option value="active">Активен</option>
                <option value="probation">Испытательный срок</option>
                <option value="inactive">Неактивен</option>
              </select>
            </div>

            <div className="hra-form__field">
              <label htmlFor="bitrix">Bitrix User ID</label>
              <input
                id="bitrix"
                type="number"
                value={form.bitrix_user_id ?? ""}
                onChange={(event) =>
                  setField(
                    "bitrix_user_id",
                    event.target.value ? Number(event.target.value) : null
                  )
                }
                placeholder="1001"
              />
            </div>

            <div className="hra-form__actions">
              <button type="submit" className="hra-btn" disabled={isSaving}>
                <Save size={15} />
                {isSaving
                  ? "Сохранение..."
                  : isEdit
                  ? "Сохранить изменения"
                  : "Создать сотрудника"}
              </button>
            </div>
          </form>
        </section>
      </div>
    </main>
  );
}
