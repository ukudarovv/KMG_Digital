import "./ProgressBar.css";

type ProgressBarProps = {
  completed: number;
  total: number;
  label?: string;
};

export function ProgressBar({
  completed,
  total,
  label = "Прогресс Дня 1",
}: ProgressBarProps) {
  const percent = total === 0 ? 0 : Math.round((completed / total) * 100);

  return (
    <div className="progress">
      <div className="progress__header">
        <span>{label}</span>
        <strong>
          {completed} из {total} задач
        </strong>
      </div>

      <div className="progress__track">
        <div className="progress__fill" style={{ width: `${percent}%` }} />
      </div>

      <small>{percent}% выполнено</small>
    </div>
  );
}
