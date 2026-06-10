import { BookOpen, CheckCircle2 } from "lucide-react";
import type { CultureFitNudge } from "../../data/cultureFitNudges";
import "./NudgeCard.css";

type NudgeCardProps = {
  nudge: CultureFitNudge;
  isActive?: boolean;
  isCompleted?: boolean;
  isFuture?: boolean;
  isLoading?: boolean;
  onClick?: () => void;
};

export function NudgeCard({
  nudge,
  isActive,
  isCompleted,
  isFuture,
  isLoading,
  onClick,
}: NudgeCardProps) {
  return (
    <article
      className={`nudge-card ${isActive ? "nudge-card--active" : ""} ${
        isCompleted ? "nudge-card--completed" : ""
      } ${isFuture ? "nudge-card--future" : ""} ${
        onClick ? "nudge-card--clickable" : ""
      } ${isLoading ? "nudge-card--loading" : ""}`}
      onClick={onClick}
      onKeyDown={
        onClick
          ? (event) => {
              if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                onClick();
              }
            }
          : undefined
      }
      role={onClick ? "button" : undefined}
      tabIndex={onClick ? 0 : undefined}
    >
      <div className="nudge-card__day">
        {isCompleted ? <CheckCircle2 size={22} /> : <span>{nudge.day}</span>}
      </div>

      <div className="nudge-card__content">
        <div className="nudge-card__header">
          <h3>{nudge.title}</h3>

          {isActive && <strong>Сегодня</strong>}
          {isCompleted && !isActive && <strong>Пройдено</strong>}
          {isFuture && <strong>Скоро</strong>}
        </div>

        <p>{nudge.text}</p>

        <div className="nudge-card__source">
          <BookOpen size={15} />
          <span>Источник: {nudge.source}</span>
        </div>
      </div>
    </article>
  );
}
