import { useNavigate } from "react-router-dom";
import { HR_ROUTES } from "../../routes/hrRoutes";
import { AlertTriangle, CheckCircle2, CircleDashed, Eye } from "lucide-react";
import type { HREmployeeDashboardItem } from "../../api/hrApi";
import "./EmployeeRow.css";

type EmployeeRowProps = {
  employee: HREmployeeDashboardItem;
};

export function EmployeeRow({ employee }: EmployeeRowProps) {
  const navigate = useNavigate();

  const riskLabel = {
    low: "Низкий",
    medium: "Средний",
    high: "Высокий",
  }[employee.risk_level];

  const sentimentLabel = {
    positive: "Позитивный",
    neutral: "Нейтральный",
    negative: "Негативный",
  }[employee.sentiment];

  const RiskIcon =
    employee.risk_level === "high"
      ? AlertTriangle
      : employee.risk_level === "medium"
        ? CircleDashed
        : CheckCircle2;

  return (
    <article className="employee-row">
      <div className="employee-row__profile">
        <div className="employee-row__avatar">
          {employee.full_name
            .split(" ")
            .map((part) => part[0])
            .join("")
            .slice(0, 2)}
        </div>

        <div>
          <h3>{employee.full_name}</h3>
          <p>{employee.position || "Должность не указана"}</p>
          <small>{employee.department || "Подразделение не указано"}</small>
        </div>
      </div>

      <div className="employee-row__cell">
        <span>Руководитель</span>
        <strong>{employee.manager || "Не указан"}</strong>
      </div>

      <div className="employee-row__cell">
        <span>Этап</span>
        <strong>{employee.current_stage}</strong>
      </div>

      <div className="employee-row__progress">
        <div className="employee-row__progress-top">
          <span>{employee.progress}%</span>
          <small>
            {employee.completed_tasks}/{employee.total_tasks}
          </small>
        </div>

        <div className="employee-row__track">
          <div
            className="employee-row__fill"
            style={{ width: `${employee.progress}%` }}
          />
        </div>
      </div>

      <div className="employee-row__cell">
        <span>NPS</span>
        <strong>{employee.nps === null ? "—" : `${employee.nps}/10`}</strong>
      </div>

      <div className={`employee-row__badge employee-row__badge--${employee.sentiment}`}>
        {sentimentLabel}
      </div>

      <div className={`employee-row__risk employee-row__risk--${employee.risk_level}`}>
        <RiskIcon size={16} />
        {riskLabel}
      </div>

      <div className="employee-row__cell">
        <span>Активность</span>
        <strong>{employee.last_activity}</strong>
      </div>

      <button
        type="button"
        className="employee-row__button"
        onClick={() => navigate(HR_ROUTES.employee(employee.id))}
      >
        <Eye size={17} />
        Открыть
      </button>
    </article>
  );
}
