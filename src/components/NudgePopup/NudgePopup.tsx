import { BookOpen, MessageCircle, X } from "lucide-react";
import type { CultureFitNudge } from "../../data/cultureFitNudges";
import { CultureFitCharacter } from "../DigitalBuddy/CultureFitCharacter";
import { DigitalBuddyLogo } from "../DigitalBuddy/DigitalBuddyLogo";
import { BUDDY_NAME } from "../DigitalBuddy/buddyMessages";
import "./NudgePopup.css";

type NudgePopupProps = {
  nudge: CultureFitNudge;
  isOpen: boolean;
  alreadySentToday: boolean;
  canSendToChat?: boolean;
  onClose: () => void;
  onSendToChat: () => void;
};

export function NudgePopup({
  nudge,
  isOpen,
  alreadySentToday,
  canSendToChat = true,
  onClose,
  onSendToChat,
}: NudgePopupProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="nudge-popup">
      <div className="nudge-popup__overlay" onClick={onClose} />

      <div className="nudge-popup__scene">
        <aside className="nudge-popup__buddy-panel" aria-hidden="true">
          <div className="nudge-popup__speech-bubble">
            <span>Подсказка от Digital Buddy</span>
          </div>
          <CultureFitCharacter size={108} animate="nudge" />
        </aside>

        <section className="nudge-popup__window">
          <DigitalBuddyLogo mood="idle" className="nudge-popup__brand-logo" />

          <button
            type="button"
            className="nudge-popup__close"
            onClick={onClose}
            aria-label="Закрыть окно"
          >
            <X size={20} />
          </button>

          <header className="nudge-popup__header">
            <div className="nudge-popup__header-text">
              <span>{BUDDY_NAME}</span>
              <h2>Culture Fit Nudge — День {nudge.day}</h2>
              <p>Ежедневная карточка корпоративной культуры при входе на портал</p>
            </div>
          </header>

          <div className="nudge-popup__card">
            <span>{nudge.title}</span>
            <p>{nudge.text}</p>

            <div className="nudge-popup__source">
              <BookOpen size={16} />
              Источник ВНД: {nudge.source}
            </div>
          </div>

          {alreadySentToday && canSendToChat && (
            <div className="nudge-popup__notice">
              Эта карточка уже была отправлена сегодня. Повторная отправка
              заблокирована защитой от дублей.
            </div>
          )}

          {!canSendToChat && (
            <div className="nudge-popup__notice">
              Это архивная карточка — просмотр без отправки в чат. Отправить
              можно только карточку текущего дня.
            </div>
          )}

          <footer className="nudge-popup__actions">
            <button
              type="button"
              className="nudge-popup__button nudge-popup__button--secondary"
              onClick={onClose}
            >
              Понятно
            </button>

            {canSendToChat && (
              <button
                type="button"
                className="nudge-popup__button nudge-popup__button--primary"
                onClick={onSendToChat}
                disabled={alreadySentToday}
              >
                <MessageCircle size={18} />
                Отправить в чат
              </button>
            )}
          </footer>
        </section>
      </div>
    </div>
  );
}
