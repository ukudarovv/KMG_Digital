import { CheckCircle2, CircleDashed, PencilLine } from "lucide-react";
import type { SmartGoal } from "../../data/adaptationData";
import "./SmartGoalCard.css";

type SmartGoalCardProps = {
  goal: SmartGoal;
};

export function SmartGoalCard({ goal }: SmartGoalCardProps) {
  const statusConfig = {
    approved: {
      label: "Согласована",
      icon: CheckCircle2,
    },
    draft: {
      label: "Черновик",
      icon: PencilLine,
    },
    needs_update: {
      label: "Нужно уточнить",
      icon: CircleDashed,
    },
  }[goal.status];

  const StatusIcon = statusConfig.icon;

  return (
    <article className={`smart-goal-card smart-goal-card--${goal.status}`}>
      <div className="smart-goal-card__icon">
        <StatusIcon size={22} />
      </div>

      <div className="smart-goal-card__content">
        <div className="smart-goal-card__header">
          <h3>{goal.title}</h3>
          <span>{statusConfig.label}</span>
        </div>

        <p>{goal.description}</p>

        <div className="smart-goal-card__details">
          <div>
            <strong>Метрика:</strong>
            <span>{goal.metric}</span>
          </div>

          <div>
            <strong>Срок:</strong>
            <span>{goal.deadline}</span>
          </div>
        </div>
      </div>
    </article>
  );
}
