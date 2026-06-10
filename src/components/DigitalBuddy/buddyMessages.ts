export type BuddyLanguage = "ru" | "kk";

export const BUDDY_NAME = "Digital Buddy";

export const buddyWelcomeMessages: Record<BuddyLanguage, string> = {
  ru: "Здравствуйте! Я Digital Buddy — ваш цифровой помощник по адаптации в КМГ. Помогу с задачами, регламентами (ВНД), Culture Fit и вопросами по этапам онбординга.",
  kk: "Сәлеметсіз бе! Мен Digital Buddy — KMG бейімделу бойынша сіздің цифрлық көмекшіңізбін. Тапсырмалар, НҚА (ВНД), Culture Fit және онбординг кезеңдері бойынша көмектесемін.",
};

export const buddyErrorMessages: Record<BuddyLanguage, string> = {
  ru: "Не удалось получить ответ. Пожалуйста, попробуйте ещё раз.",
  kk: "Жауап алу мүмкін болмады. Қайта көріңіз.",
};

export const buddyLoadingMessages: Record<BuddyLanguage, string> = {
  ru: "Готовлю ответ...",
  kk: "Жауап дайындауда...",
};

export function buddyLoadingLabel(
  language: BuddyLanguage,
  message: string,
): string {
  const isShort =
    message.trim().length < 12 ||
    /^(здравствуй|привет|спасибо|сәлем|рахмет|hello|hi)\b/i.test(message.trim());

  if (isShort) {
    return language === "kk" ? "Жауап дайындауда..." : "Готовлю ответ...";
  }

  return language === "kk"
    ? "НҚА ішінен жауап іздеуде..."
    : "Ищу ответ в ВНД...";
}

export const buddyInputPlaceholders: Record<BuddyLanguage, string> = {
  ru: "Напишите вопрос...",
  kk: "Сұрағыңызды жазыңыз...",
};

export const buddySubtitle: Record<BuddyLanguage, string> = {
  ru: "ИИ-ассистент онбординга",
  kk: "Онбординг ЖИ-көмекшісі",
};

export const buddyModelLoadingMessages: Record<BuddyLanguage, string> = {
  ru: "Локальная модель загружается...",
  kk: "Жергілікті модель жүктелуде...",
};

export function buddyModelReadyLabel(
  language: BuddyLanguage,
  modelName: string,
): string {
  return language === "kk"
    ? `Жергілікті модель: ${modelName}`
    : `Локальная модель: ${modelName}`;
}

export function buddyModelGeneratingLabel(language: BuddyLanguage): string {
  return language === "kk"
    ? "Жергілікті модель жауап дайындауда..."
    : "Локальная модель формирует ответ...";
}

const KAZAKH_CHARS = /[әғқңөұүһі]/;
const KAZAKH_WORDS = new Set([
  "сәлем",
  "сәлеметсіз",
  "рахмет",
  "қалай",
  "күн",
  "сұрақ",
  "көмек",
  "жауап",
  "құжат",
  "нқа",
  "бейімделу",
  "тапсырма",
  "қауіпсіздік",
  "ақпараттық",
  "еңбек",
  "кездесу",
  "мүдде",
  "пара",
  "коррупция",
  "сенім",
  "хат",
  "мақсат",
  "түсіндір",
  "айтыңыз",
  "қандай",
  "қайда",
  "неге",
  "керек",
  "және",
  "немесе",
]);

export function detectClientLanguage(text: string): BuddyLanguage {
  const lower = text.toLowerCase();

  if (KAZAKH_CHARS.test(lower)) {
    return "kk";
  }

  const tokens = lower.match(/[a-zа-яёәғқңөұүһі]+/g) ?? [];
  if (tokens.some((token) => KAZAKH_WORDS.has(token))) {
    return "kk";
  }

  return "ru";
}
