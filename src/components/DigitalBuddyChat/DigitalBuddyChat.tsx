import { useEffect, useState } from "react";
import { BookOpen, Send, User, X } from "lucide-react";
import { digitalBuddyApi, type DigitalBuddyStatus } from "../../api/digitalBuddyApi";
import { DigitalBuddyCharacter } from "../DigitalBuddy/DigitalBuddyCharacter";
import { useDigitalBuddy } from "../DigitalBuddy/DigitalBuddyContext";
import {
  BUDDY_NAME,
  buddyErrorMessages,
  buddyInputPlaceholders,
  buddyLoadingLabel,
  buddyModelGeneratingLabel,
  buddyModelLoadingMessages,
  buddyModelReadyLabel,
  buddySubtitle,
  buddyWelcomeMessages,
  type BuddyLanguage,
} from "../DigitalBuddy/buddyMessages";
import "./DigitalBuddyChat.css";

const CHAT_AVATAR_SIZE = 40;

type ChatMessage = {
  id: number;
  role: "user" | "assistant";
  text: string;
  source?: string;
  section?: string;
  documentCode?: string;
};

type DigitalBuddyChatProps = {
  onClose: () => void;
};

export function DigitalBuddyChat({ onClose }: DigitalBuddyChatProps) {
  const { language, setLanguage, pendingPrompt, clearPendingPrompt } =
    useDigitalBuddy();
  const [messageText, setMessageText] = useState("");
  const [pendingMessage, setPendingMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [llmStatus, setLlmStatus] = useState<DigitalBuddyStatus | null>(null);

  useEffect(() => {
    digitalBuddyApi.getStatus().then(setLlmStatus).catch(() => setLlmStatus(null));
  }, []);

  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: 1,
          role: "assistant",
          text: buddyWelcomeMessages[language],
        },
      ]);
    }
  }, [language, messages.length]);

  const handleSendMessage = async (textOverride?: string) => {
    const trimmedMessage = (textOverride ?? messageText).trim();

    if (!trimmedMessage || isLoading) {
      return;
    }

    const requestLanguage = language;

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: "user",
      text: trimmedMessage,
    };

    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setPendingMessage(trimmedMessage);
    setMessageText("");
    setIsLoading(true);

    try {
      const answer = await digitalBuddyApi.askQuestion(
        trimmedMessage,
        requestLanguage,
      );

      if (answer.language) {
        setLanguage(answer.language);
      }

      const assistantMessage: ChatMessage = {
        id: Date.now() + 1,
        role: "assistant",
        text: answer.answer,
        source: answer.source,
        section: answer.section,
        documentCode: answer.document_code,
      };

      setMessages((prevMessages) => [...prevMessages, assistantMessage]);
    } catch {
      const errorMessage: ChatMessage = {
        id: Date.now() + 1,
        role: "assistant",
        text: buddyErrorMessages[language],
      };

      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setPendingMessage("");
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (!pendingPrompt || isLoading) {
      return;
    }

    const prompt = pendingPrompt;
    clearPendingPrompt();
    void handleSendMessage(prompt);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- only react to pendingPrompt
  }, [pendingPrompt]);

  const llmSubtitle =
    llmStatus?.model_ready
      ? buddyModelReadyLabel(language, llmStatus.llm_model)
      : llmStatus?.llm_enabled
        ? buddyModelLoadingMessages[language]
        : buddySubtitle[language];

  const loadingLabel =
    llmStatus?.model_ready
      ? buddyModelGeneratingLabel(language)
      : buddyLoadingLabel(language, pendingMessage || messageText);

  const handleLanguageChange = (nextLanguage: BuddyLanguage) => {
    setLanguage(nextLanguage);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      void handleSendMessage();
    }
  };

  return (
    <aside className="buddy-chat">
      <header className="buddy-chat__header">
        <div className="buddy-chat__title">
          <DigitalBuddyCharacter
            mood={isLoading ? "thinking" : "talking"}
            size={52}
            variant="standing"
            className="buddy-chat__character"
          />

          <div>
            <h3>{BUDDY_NAME}</h3>
            <span>
              {isLoading ? loadingLabel : llmSubtitle}
            </span>
          </div>
        </div>

        <div className="buddy-chat__header-actions">
          <div className="buddy-chat__lang-switch" role="group" aria-label="Тіл / Язык">
            <button
              type="button"
              className={`buddy-chat__lang-btn${language === "ru" ? " buddy-chat__lang-btn--active" : ""}`}
              onClick={() => handleLanguageChange("ru")}
            >
              RU
            </button>
            <button
              type="button"
              className={`buddy-chat__lang-btn${language === "kk" ? " buddy-chat__lang-btn--active" : ""}`}
              onClick={() => handleLanguageChange("kk")}
            >
              KZ
            </button>
          </div>

          <button
            type="button"
            className="buddy-chat__close"
            onClick={onClose}
            aria-label="Закрыть чат"
          >
            <X size={20} />
          </button>
        </div>
      </header>

      <div className="buddy-chat__messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`buddy-chat__message buddy-chat__message--${message.role}`}
          >
            <div className="buddy-chat__message-icon">
              {message.role === "assistant" ? (
                <DigitalBuddyCharacter mood="idle" size={CHAT_AVATAR_SIZE} />
              ) : (
                <User size={17} />
              )}
            </div>

            <div className="buddy-chat__bubble">
              <p>{message.text}</p>

              {message.role === "assistant" &&
                message.source &&
                message.source !== "Digital Buddy" &&
                message.documentCode && (
                <div className="buddy-chat__source">
                  <BookOpen size={14} />
                  <span>
                    {message.source}
                    {message.section ? ` • ${message.section}` : ""}
                  </span>
                  {message.documentCode && (
                    <a
                      className="buddy-chat__source-link"
                      href={`/api/vnd/documents/${message.documentCode}/file`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {language === "kk" ? "Құжатты ашу" : "Открыть документ"}
                    </a>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="buddy-chat__message buddy-chat__message--assistant">
            <div className="buddy-chat__message-icon">
              <DigitalBuddyCharacter mood="thinking" size={CHAT_AVATAR_SIZE} />
            </div>

            <div className="buddy-chat__bubble">
              <p className="buddy-chat__typing">
                <span />
                <span />
                <span />
              </p>
            </div>
          </div>
        )}
      </div>

      <footer className="buddy-chat__footer">
        <input
          value={messageText}
          onChange={(event) => setMessageText(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={buddyInputPlaceholders[language]}
        />

        <button
          type="button"
          onClick={() => handleSendMessage()}
          disabled={isLoading}
        >
          <Send size={18} />
        </button>
      </footer>
    </aside>
  );
}
