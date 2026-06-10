import { GraduationCap } from "lucide-react";
import type { DevelopmentRecommendation } from "../../data/retentionData";
import "./DevelopmentCard.css";

type DevelopmentCardProps = {
  item: DevelopmentRecommendation;
};

export function DevelopmentCard({ item }: DevelopmentCardProps) {
  const priorityLabel = {
    high: "Высокий приоритет",
    medium: "Средний приоритет",
    low: "Низкий приоритет",
  }[item.priority];

  return (
    <article className={`development-card development-card--${item.priority}`}>
      <div className="development-card__icon">
        <GraduationCap size={22} />
      </div>

      <div className="development-card__content">
        <div className="development-card__header">
          <h3>{item.title}</h3>
          <span>{priorityLabel}</span>
        </div>

        <p>{item.description}</p>
      </div>
    </article>
  );
}
