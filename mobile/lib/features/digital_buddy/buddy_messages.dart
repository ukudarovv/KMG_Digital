/// Порт src/components/DigitalBuddy/buddyMessages.ts: тексты RU/KK
/// и клиентское определение языка вопроса.
const buddyName = 'Digital Buddy';

const buddyWelcomeMessages = {
  'ru': 'Здравствуйте! Я Digital Buddy — ваш цифровой помощник по адаптации '
      'в КМГ. Помогу с задачами, регламентами (ВНД), Culture Fit и вопросами '
      'по этапам онбординга.',
  'kk': 'Сәлеметсіз бе! Мен Digital Buddy — KMG бейімделу бойынша сіздің '
      'цифрлық көмекшіңізбін. Тапсырмалар, НҚА (ВНД), Culture Fit және '
      'онбординг кезеңдері бойынша көмектесемін.',
};

const buddyErrorMessages = {
  'ru': 'Не удалось получить ответ. Пожалуйста, попробуйте ещё раз.',
  'kk': 'Жауап алу мүмкін болмады. Қайта көріңіз.',
};

const buddyLoadingMessages = {
  'ru': 'Ищу ответ в ВНД...',
  'kk': 'НҚА ішінен жауап іздеуде...',
};

const buddyInputPlaceholders = {
  'ru': 'Напишите вопрос...',
  'kk': 'Сұрағыңызды жазыңыз...',
};

const buddySubtitle = {
  'ru': 'ИИ-ассистент онбординга',
  'kk': 'Онбординг ЖИ-көмекшісі',
};

final _kazakhChars = RegExp(r'[әғқңөұүһі]');

const _kazakhWords = {
  'сәлем', 'сәлеметсіз', 'рахмет', 'қалай', 'күн', 'сұрақ', 'көмек',
  'жауап', 'құжат', 'нқа', 'бейімделу', 'тапсырма', 'қауіпсіздік',
  'ақпараттық', 'еңбек', 'кездесу', 'мүдде', 'пара', 'коррупция', 'сенім',
  'хат', 'мақсат', 'түсіндір', 'айтыңыз', 'қандай', 'қайда', 'неге',
  'керек', 'және', 'немесе',
};

String detectClientLanguage(String text) {
  final lower = text.toLowerCase();

  if (_kazakhChars.hasMatch(lower)) {
    return 'kk';
  }

  final tokens = RegExp(r'[a-zа-яёәғқңөұүһі]+').allMatches(lower);
  for (final token in tokens) {
    if (_kazakhWords.contains(token.group(0))) {
      return 'kk';
    }
  }

  return 'ru';
}
