import { useEffect, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  ClipboardList,
  UsersRound,
} from "lucide-react";
import { EmployeeRow } from "../components/EmployeeRow/EmployeeRow";
import { hrApi, type HRDashboardResponse } from "../api/hrApi";
import "./HRDashboardPage.css";

export function HRDashboardPage() {
  const [dashboard, setDashboard] = useState<HRDashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const data = await hrApi.getDashboard();
        setDashboard(data);
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboard();
  }, []);

  if (isLoading) {
    return (
      <main className="hr-dashboard-page">
        <div className="hr-dashboard-page__container">
          <div className="hr-dashboard-alert">
            <div className="hr-dashboard-alert__icon">
              <ClipboardList size={28} />
            </div>

            <div>
              <h2>Загрузка HR Dashboard...</h2>
              <p>Получаем данные сотрудников из backend.</p>
            </div>
          </div>
        </div>
      </main>
    );
  }

  if (!dashboard) {
    return (
      <main className="hr-dashboard-page">
        <div className="hr-dashboard-page__container">
          <div className="hr-dashboard-alert">
            <div className="hr-dashboard-alert__icon">
              <AlertTriangle size={28} />
            </div>

            <div>
              <h2>Не удалось загрузить HR Dashboard</h2>
              <p>Проверьте, что backend запущен и доступен.</p>
            </div>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="hr-dashboard-page">
      <div className="hr-dashboard-page__container">
        <header className="hr-dashboard-page__header">
          <div>
            <span>HR Admin</span>
            <h1>Контроль адаптации сотрудников</h1>
            <p>
              Панель показывает прогресс маршрута, текущий этап, NPS,
              sentiment и risk-флаги без раскрытия личной переписки.
            </p>
          </div>
        </header>

        <section className="hr-dashboard-summary">
          <article className="hr-dashboard-summary__card">
            <UsersRound size={28} />
            <span>Новые сотрудники</span>
            <strong>{dashboard.summary.total_employees}</strong>
          </article>

          <article className="hr-dashboard-summary__card">
            <BarChart3 size={28} />
            <span>Средний прогресс</span>
            <strong>{dashboard.summary.average_progress}%</strong>
          </article>

          <article className="hr-dashboard-summary__card">
            <AlertTriangle size={28} />
            <span>Высокий риск</span>
            <strong>{dashboard.summary.high_risk_count}</strong>
          </article>

          <article className="hr-dashboard-summary__card">
            <CheckCircle2 size={28} />
            <span>Активны сегодня</span>
            <strong>{dashboard.summary.active_today_count}</strong>
          </article>
        </section>

        <section className="hr-dashboard-alert">
          <div className="hr-dashboard-alert__icon">
            <ClipboardList size={28} />
          </div>

          <div>
            <h2>Принцип конфиденциальности</h2>
            <p>
              HR получает агрегированную аналитику: прогресс, NPS, риск-флаги и
              динамику тональности. Текст личной переписки с Digital Buddy в
              отчёты не передаётся.
            </p>
          </div>
        </section>

        <section className="hr-dashboard-table">
          <div className="hr-dashboard-table__header">
            <div>
              <span>Сотрудники</span>
              <h2>Маршруты адаптации</h2>
            </div>

            <button type="button">Экспорт отчёта</button>
          </div>

          <div className="hr-dashboard-table__list">
            {dashboard.employees.map((employee) => (
              <EmployeeRow key={employee.id} employee={employee} />
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
