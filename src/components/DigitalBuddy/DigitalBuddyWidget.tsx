import { useLocation } from "react-router-dom";
import { DigitalBuddyChat } from "../DigitalBuddyChat/DigitalBuddyChat";
import { DigitalBuddyCharacter } from "./DigitalBuddyCharacter";
import { useDigitalBuddy } from "./DigitalBuddyContext";
import "./DigitalBuddyWidget.css";

const PAGE_HINTS: Record<string, string> = {
  "/": "Выберите этап адаптации — я подскажу, что делать дальше.",
  "/introduction": "День 1: помогу с инструктажами, видео и ВНД.",
  "/engagement": "Culture Fit и опросы — спрашивайте про корпоративную культуру.",
  "/adaptation": "Подготовлю вас к 1:1 и SMART-целям.",
  "/retention": "Расскажу про итоговую оценку и HR-аналитику.",
};

export function DigitalBuddyWidget() {
  const { isChatOpen, openChat, closeChat } = useDigitalBuddy();
  const location = useLocation();

  const hint =
    PAGE_HINTS[location.pathname] ??
    "Я рядом на каждом этапе адаптации. Задайте вопрос!";

  return (
    <>
      {!isChatOpen && (
        <div className="buddy-widget">
          <div className="buddy-widget__hint" role="status">
            <span>{hint}</span>
          </div>

          <button
            type="button"
            className="buddy-widget__launcher"
            onClick={openChat}
            aria-label="Открыть чат Digital Buddy"
            aria-expanded={false}
          >
            <DigitalBuddyCharacter
              mood="idle"
              size={120}
              variant="standing"
              animate="appear"
              className="buddy-widget__character"
            />
            <span className="buddy-widget__pulse" />
          </button>
        </div>
      )}

      <DigitalBuddyChat isOpen={isChatOpen} onClose={closeChat} />
    </>
  );
}
