import { Check, Lock } from "lucide-react";
import { useNavigate } from "react-router-dom";
import "./StageCard.css";

type StageCardProps = {
  step: number;
  title: string;
  description: string;
  status: string;
  period: string;
  path: string;
  disabled?: boolean;
  icon: React.ElementType;
};

export function StageCard({
  step,
  title,
  description,
  status,
  period,
  path,
  disabled,
  icon: Icon,
}: StageCardProps) {
  const navigate = useNavigate();
  const isCompleted = status === "Готово";

  const handleClick = () => {
    if (disabled) {
      return;
    }

    navigate(path);
  };

  return (
    <button
      className={`stage-card ${disabled ? "stage-card--disabled" : ""} ${isCompleted ? "stage-card--completed" : ""}`}
      onClick={handleClick}
      type="button"
      aria-label={`${title}. ${period}. ${status}`}
    >
      <span className="stage-card__step">
        {isCompleted ? <Check size={12} strokeWidth={3} /> : step}
      </span>

      {disabled && !isCompleted && (
        <span className="stage-card__lock" aria-hidden="true">
          <Lock size={12} strokeWidth={2.5} />
        </span>
      )}

      <div className="stage-card__icon">
        <Icon size={36} strokeWidth={2} />
      </div>

      <div className="stage-card__footer">
        <span>{title}</span>
      </div>

      <div className="stage-card__details">
        <span
          className={`stage-card__status stage-card__status--${isCompleted ? "done" : "active"}`}
        >
          {status}
        </span>
        <p>{description}</p>
        <small>{period}</small>
      </div>
    </button>
  );
}
