import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Pencil, Plus, UserRound } from "lucide-react";
import { employeeApi, type Employee } from "../../api/employeeApi";
import { HR_ROUTES } from "../../routes/hrRoutes";
import "./HRAdminShared.css";

const STATUS_LABELS: Record<string, { label: string; tone: string }> = {
  active: { label: "Активен", tone: "hra-badge--green" },
  inactive: { label: "Неактивен", tone: "hra-badge--red" },
  probation: { label: "Испытательный срок", tone: "hra-badge--blue" },
};

export function EmployeesListPage() {
  const navigate = useNavigate();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    employeeApi
      .getAll()
      .then(setEmployees)
      .catch(() => setError("Не удалось загрузить список сотрудников."))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <main className="hra-page">
      <div className="hra-container">
        <header className="hra-header">
          <div>
            <span>HR Admin</span>
            <h1>Сотрудники</h1>
            <p>
              Управление профилями: добавление новых сотрудников, назначение
              отдела и руководителя, запуск маршрута онбординга.
            </p>
          </div>

          <div className="hra-header__actions">
            <Link className="hra-btn" to={HR_ROUTES.employeeNew}>
              <Plus size={16} />
              Добавить сотрудника
            </Link>
          </div>
        </header>

        {error && <div className="hra-alert hra-alert--error">{error}</div>}

        <section className="hra-card">
          {isLoading ? (
            <div className="hra-empty">Загрузка...</div>
          ) : employees.length === 0 ? (
            <div className="hra-empty">
              Сотрудников пока нет. Добавьте первого сотрудника или примите
              кандидата через AI-рекрутинг.
            </div>
          ) : (
            <table className="hra-table">
              <thead>
                <tr>
                  <th>Сотрудник</th>
                  <th>Должность</th>
                  <th>Отдел</th>
                  <th>Руководитель</th>
                  <th>Дата выхода</th>
                  <th>Статус</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {employees.map((employee) => {
                  const status =
                    STATUS_LABELS[employee.status] ?? {
                      label: employee.status,
                      tone: "",
                    };

                  return (
                    <tr key={employee.id}>
                      <td>
                        <Link
                          className="hra-link"
                          to={HR_ROUTES.employee(employee.id)}
                        >
                          <UserRound
                            size={14}
                            style={{ verticalAlign: "-2px", marginRight: 6 }}
                          />
                          {employee.full_name}
                        </Link>
                      </td>
                      <td>{employee.position || "—"}</td>
                      <td>{employee.department || "—"}</td>
                      <td>{employee.manager_name || "—"}</td>
                      <td>{employee.start_date}</td>
                      <td>
                        <span className={`hra-badge ${status.tone}`}>
                          {status.label}
                        </span>
                      </td>
                      <td>
                        <button
                          type="button"
                          className="hra-btn hra-btn--secondary"
                          onClick={() =>
                            navigate(HR_ROUTES.employeeEdit(employee.id))
                          }
                        >
                          <Pencil size={14} />
                          Изменить
                        </button>
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
