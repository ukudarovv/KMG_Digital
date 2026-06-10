import { Bot, MessageCircle } from "lucide-react";
import "./DigitalBuddyPanel.css";

type DigitalBuddyPanelProps = {
  employeeName: string;
  onAskQuestion: () => void;
};

export function DigitalBuddyPanel({
  employeeName,
  onAskQuestion,
}: DigitalBuddyPanelProps) {
  return (
    <section className="buddy-panel">
      <div className="buddy-panel__avatar">
        <Bot size={42} />
      </div>

      <div className="buddy-panel__content">
        <span>Digital Buddy</span>
        <h2>Добрый день, {employeeName}!</h2>
        <p>
          День 1 вашей адаптации в КМГ. Я помогу вам пройти первые задачи,
          найти нужные материалы и ответить на вопросы по внутренним документам.
        </p>

        <button
          type="button"
          className="buddy-panel__button"
          onClick={onAskQuestion}
        >
          <MessageCircle size={18} />
          Задать вопрос Digital Buddy
        </button>
      </div>
    </section>
  );
}
