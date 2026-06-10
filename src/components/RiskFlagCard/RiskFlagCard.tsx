import { AlertTriangle, CheckCircle2 } from "lucide-react";
import type { RiskFlag } from "../../data/retentionData";
import "./RiskFlagCard.css";

type RiskFlagCardProps = {
  risk: RiskFlag;
};

export function RiskFlagCard({ risk }: RiskFlagCardProps) {
  const levelLabel = {
    low: "Низкий",
    medium: "Средний",
    high: "Высокий",
  }[risk.level];

  return (
    <article className={`risk-flag-card risk-flag-card--${risk.level}`}>
      <div className="risk-flag-card__icon">
        {risk.status === "resolved" ? (
          <CheckCircle2 size={22} />
        ) : (
          <AlertTriangle size={22} />
        )}
      </div>

      <div className="risk-flag-card__content">
        <div className="risk-flag-card__header">
          <h3>{risk.title}</h3>

          <div className="risk-flag-card__badges">
            <span>{levelLabel}</span>
            <strong>{risk.status === "active" ? "Активен" : "Решён"}</strong>
          </div>
        </div>

        <p>{risk.description}</p>
      </div>
    </article>
  );
}
