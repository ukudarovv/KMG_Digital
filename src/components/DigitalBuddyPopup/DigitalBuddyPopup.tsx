import { ExternalLink, MessageCircle, PlayCircle, X } from "lucide-react";
import { DigitalBuddyLogo } from "../DigitalBuddy/DigitalBuddyLogo";
import { BUDDY_NAME } from "../DigitalBuddy/buddyMessages";
import "./DigitalBuddyPopup.css";

type PopupNextTask = {
  title: string;
  description?: string | null;
  deadline_at?: string | null;
};

type DigitalBuddyPopupProps = {
  employeeName: string;
  adaptationDay?: number;
  completedTasks: number;
  totalTasks: number;
  videoUrl?: string;
  nextTask?: PopupNextTask;
  isOpen: boolean;
  onClose: () => void;
  onAskQuestion: () => void;
  onWatchVideo?: () => void;
};

function formatDeadline(deadline?: string | null) {
  if (!deadline) {
    return "Сегодня до 18:00";
  }

  return new Date(deadline).toLocaleString("ru-RU", {
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function DigitalBuddyPopup({
  employeeName,
  adaptationDay = 1,
  completedTasks,
  totalTasks,
  videoUrl,
  nextTask,
  isOpen,
  onClose,
  onAskQuestion,
  onWatchVideo,
}: DigitalBuddyPopupProps) {
  if (!isOpen) {
    return null;
  }

  const percent =
    totalTasks === 0 ? 0 : Math.round((completedTasks / totalTasks) * 100);

  const handleWatchVideo = () => {
    if (videoUrl) {
      window.open(videoUrl, "_blank", "noopener,noreferrer");
    }
    onWatchVideo?.();
  };

  return (
    <div className="buddy-popup-overlay" onClick={onClose}>
      <div
        className="buddy-popup"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="buddy-popup-title"
      >
        <DigitalBuddyLogo mood="happy" className="buddy-popup__brand-logo" />

        <header className="buddy-popup__header">
          <div className="buddy-popup__title">
            <div>
              <span>{BUDDY_NAME}</span>
              <h2 id="buddy-popup-title">Добрый день, {employeeName}!</h2>
              <p className="buddy-popup__subtitle">
                День {adaptationDay} вашей адаптации в КМГ. Я помогу пройти
                обязательные инструктажи и отвечу на вопросы по ВНД.
              </p>
            </div>
          </div>

          <button
            type="button"
            className="buddy-popup__close"
            onClick={onClose}
            aria-label="Закрыть"
          >
            <X size={20} />
          </button>
        </header>

        <div className="buddy-popup__body">
          <button
            type="button"
            className="buddy-popup__video"
            onClick={handleWatchVideo}
            disabled={!videoUrl}
          >
            <PlayCircle size={36} />
            <div>
              <strong>Приветственное видео</strong>
              <p>Видеообращение Председателя Правления КМГ</p>
              {videoUrl && (
                <span className="buddy-popup__video-link">
                  <ExternalLink size={14} />
                  Смотреть видео
                </span>
              )}
            </div>
          </button>

          {nextTask && (
            <div className="buddy-popup__next-task">
              <span>Ближайшая задача</span>
              <h3>{nextTask.title}</h3>
              {nextTask.description && <p>{nextTask.description}</p>}
              <small>Срок: {formatDeadline(nextTask.deadline_at)}</small>
            </div>
          )}

          <div className="buddy-popup__progress">
            <div className="buddy-popup__progress-header">
              <span>Прогресс Дня 1</span>
              <strong>
                {completedTasks} из {totalTasks}
              </strong>
            </div>
            <div className="buddy-popup__progress-track">
              <div
                className="buddy-popup__progress-fill"
                style={{ width: `${percent}%` }}
              />
            </div>
            <small>{percent}% выполнено</small>
          </div>
        </div>

        <footer className="buddy-popup__footer">
          <button
            type="button"
            className="buddy-popup__btn-secondary"
            onClick={onClose}
          >
            Понятно
          </button>
          <button
            type="button"
            className="buddy-popup__btn-primary"
            onClick={onAskQuestion}
          >
            <MessageCircle size={18} />
            Задать вопрос
          </button>
        </footer>
      </div>
    </div>
  );
}
