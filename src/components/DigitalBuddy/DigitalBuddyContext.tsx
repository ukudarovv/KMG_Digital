import { createContext, useCallback, useContext, useMemo, useState } from "react";
import type { BuddyLanguage } from "./buddyMessages";

type DigitalBuddyContextValue = {
  isChatOpen: boolean;
  language: BuddyLanguage;
  pendingPrompt: string | null;
  openChat: () => void;
  openChatWithPrompt: (prompt: string) => void;
  closeChat: () => void;
  toggleChat: () => void;
  setLanguage: (language: BuddyLanguage) => void;
  clearPendingPrompt: () => void;
};

const DigitalBuddyContext = createContext<DigitalBuddyContextValue | null>(null);

type DigitalBuddyProviderProps = {
  children: React.ReactNode;
};

export function DigitalBuddyProvider({ children }: DigitalBuddyProviderProps) {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [language, setLanguage] = useState<BuddyLanguage>("ru");
  const [pendingPrompt, setPendingPrompt] = useState<string | null>(null);

  const openChat = useCallback(() => setIsChatOpen(true), []);
  const openChatWithPrompt = useCallback((prompt: string) => {
    setPendingPrompt(prompt);
    setIsChatOpen(true);
  }, []);
  const closeChat = useCallback(() => setIsChatOpen(false), []);
  const toggleChat = useCallback(() => setIsChatOpen((open) => !open), []);
  const clearPendingPrompt = useCallback(() => setPendingPrompt(null), []);

  const value = useMemo(
    () => ({
      isChatOpen,
      language,
      pendingPrompt,
      openChat,
      openChatWithPrompt,
      closeChat,
      toggleChat,
      setLanguage,
      clearPendingPrompt,
    }),
    [
      isChatOpen,
      language,
      pendingPrompt,
      openChat,
      openChatWithPrompt,
      closeChat,
      toggleChat,
      clearPendingPrompt,
    ]
  );

  return (
    <DigitalBuddyContext.Provider value={value}>
      {children}
    </DigitalBuddyContext.Provider>
  );
}

export function useDigitalBuddy() {
  const context = useContext(DigitalBuddyContext);

  if (!context) {
    throw new Error("useDigitalBuddy must be used within DigitalBuddyProvider");
  }

  return context;
}
