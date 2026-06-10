import type { BuddyLanguage } from "../components/DigitalBuddy/buddyMessages";
import { httpClient } from "./httpClient";

export type DigitalBuddyAnswer = {
  answer: string;
  source?: string;
  section?: string;
  document_code?: string;
  sentiment?: string;
  language?: "ru" | "kk";
  mode?: "llm" | "rag" | "fallback" | "no_context" | "chat";
};

export type DigitalBuddyStatus = {
  llm_enabled: boolean;
  llm_available: boolean;
  llm_provider: string;
  llm_model: string;
  model_ready: boolean;
  installed_models: string[];
  embedding_model?: string;
  embedding_model_ready?: boolean;
  chunks_count?: number;
  indexed_documents?: string[];
  chroma_ready?: boolean;
  chroma_count?: number;
  last_indexed_at?: string;
};

export const digitalBuddyApi = {
  async getStatus(): Promise<DigitalBuddyStatus> {
    const response = await httpClient.get<DigitalBuddyStatus>(
      "/digital-buddy/status"
    );

    return response.data;
  },

  async askQuestion(
    question: string,
    language?: BuddyLanguage,
  ): Promise<DigitalBuddyAnswer> {
    const response = await httpClient.post<DigitalBuddyAnswer>(
      "/digital-buddy/ask",
      {
        employee_id: 1,
        question,
        language,
      }
    );

    return response.data;
  },
};
