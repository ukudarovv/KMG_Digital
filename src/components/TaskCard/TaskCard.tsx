import { CheckCircle2, Circle, Clock, ExternalLink } from "lucide-react";
import type { DayOneTask } from "../../data/dayOneTasks";
import { httpClient } from "../../api/httpClient";
import "./TaskCard.css";

type TaskCardProps = {
  task: DayOneTask;
  onComplete?: (taskId: number) => void;
};

export function TaskCard({ task, onComplete }: TaskCardProps) {
  const getStatusLabel = () => {
    if (task.status === "completed") {
      return "Выполнено";
    }

    if (task.status === "in_progress") {
      return "В процессе";
    }

    return "Ожидает";
  };

  const getStatusIcon = () => {
    if (task.status === "completed") {
      return <CheckCircle2 size={22} />;
    }

    if (task.status === "in_progress") {
      return <Clock size={22} />;
    }

    return <Circle size={22} />;
  };

  const openDocument = () => {
    if (task.documentUrl) {
      window.open(
        `${httpClient.defaults.baseURL?.replace(/\/api$/, "")}${task.documentUrl}`,
        "_blank"
      );
      return;
    }

    if (task.externalLink) {
      window.open(task.externalLink, "_blank");
    }
  };

  return (
    <article className={`task-card task-card--${task.status}`}>
      <div className="task-card__icon">{getStatusIcon()}</div>

      <div className="task-card__content">
        <div className="task-card__header">
          <h3>
            {task.requirementCode && (
              <small className="task-card__code">{task.requirementCode}</small>
            )}
            {task.title}
          </h3>
          <span>{getStatusLabel()}</span>
        </div>

        <p>{task.description}</p>

        <div className="task-card__footer">
          <small>{task.deadline}</small>
          {task.required && <strong>Обязательно</strong>}
        </div>

        <div className="task-card__actions">
          {(task.documentUrl || task.externalLink) && (
            <button type="button" onClick={openDocument}>
              <ExternalLink size={16} />
              Открыть материал
            </button>
          )}

          {task.confirmationRequired &&
            task.status !== "completed" &&
            onComplete && (
              <button type="button" onClick={() => onComplete(task.id)}>
                Подтвердить ознакомление
              </button>
            )}
        </div>
      </div>
    </article>
  );
}
