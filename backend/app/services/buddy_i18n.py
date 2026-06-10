import re

from app.schemas.digital_buddy import DigitalBuddyAnswer

KAZAKH_CHARS = set("әғқңөұүһі")
KAZAKH_WORDS = {
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
    "не",
    "қандай",
    "қайда",
    "неге",
    "болуы",
    "керек",
    "және",
    "немесе",
    "болса",
    "бар",
    "жоқ",
}

KAZAKH_RAG_SYNONYMS: list[tuple[str, list[str]]] = [
    ("құжат", ["документ", "регламент", "внд", "нқа"]),
    ("карт", ["карт", "проксим", "пропуск", "турникет"]),
    ("жоғал", ["потер", "утрат"]),
    ("беру", ["передав", "передач"]),
    ("беруге", ["передав", "передач"]),
    ("мүдде", ["интерес", "конфликт"]),
    ("конфликт", ["конфликт", "интерес"]),
    ("пара", ["взятк", "коррупц"]),
    ("коррупция", ["коррупц", "взятк", "антикоррупц"]),
    ("сенім", ["доверия", "линия"]),
    ("хат", ["переписк", "этик", "делов"]),
    ("кездесу", ["совещан"]),
    ("мақсат", ["smart", "цел"]),
    ("адаптация", ["адаптац", "испытатель"]),
    ("бейімделу", ["адаптац", "онбординг"]),
    ("ақпараттық", ["информацион", "иб"]),
    ("қауіпсіздік", ["безопасност"]),
    ("еңбек", ["техник", "тб"]),
    ("инструктаж", ["инструктаж", "нұсқау"]),
    ("нұсқау", ["инструктаж"]),
    ("тапсырма", ["задач", "день"]),
    ("этика", ["этик", "кодекс"]),
    ("видео", ["видео", "председател"]),
    ("төраға", ["председател", "видео"]),
    ("комплаенс", ["комплаенс", "антикоррупц"]),
]

FOOTER_RU = (
    "\n\nЕсли остались вопросы — напишите, помогу найти нужный раздел ВНД."
)
FOOTER_KK = (
    "\n\nҚосымша сұрақтар болса — жазыңыз, НҚА бойынша көмектесемін."
)

GREETING_MARKERS = (
    "здравствуй",
    "здравствуйте",
    "привет",
    "добрый день",
    "доброе утро",
    "добрый вечер",
    "сәлем",
    "сәлеметсіз",
    "салем",
    "салам",
    "hello",
    "hi",
)

THANKS_MARKERS = (
    "спасибо",
    "благодар",
    "рахмет",
    "спс",
    "thanks",
)

HELP_MARKERS = (
    "что ты умеешь",
    "чем помочь",
    "как пользоваться",
    "помоги",
    "көмектес",
    "не істей",
)

GENERIC_QUESTION_MARKERS = (
    "?",
    "что",
    "как",
    "где",
    "когда",
    "можно",
    "нужно",
    "должен",
    "обязан",
    "расскаж",
    "объясн",
    "подскаж",
    "зачем",
    "почему",
    "какой",
    "какая",
    "какие",
    "сколько",
    "разрешен",
    "запрещ",
    "қандай",
    "қайда",
    "неге",
    "бола",
    "керек",
)

VND_DOMAIN_MARKERS = (
    "внд",
    "нқа",
    "kmg",
    "қмг",
    "инструктаж",
    "пропуск",
    "проксим",
    "конфликт",
    "комплаенс",
    "smart",
    "этик",
    "переписк",
    "совещан",
    "взятк",
    "коррупц",
    "доверия",
    "адаптац",
    "бейімделу",
    "беруге",
    "мүдде",
    "пара",
    "сенім",
    "карт",
    "турникет",
    "потер",
    "жоғал",
    "сотрудник",
    "қызметкер",
    "испытатель",
    "онбординг",
    "culture fit",
    "делов",
    "хат",
    "кездесу",
    "мақсат",
    "задач",
    "тапсырма",
    "бейімделу",
    "интерес",
    "линия",
    "антикоррупц",
)

OFF_TOPIC_MARKERS = (
    "курс доллара",
    "курс доллар",
    "курс евро",
    "погода",
    "погоду",
    "биткоин",
    "криптовалют",
    "рецепт",
    "анекдот",
    "футбол",
    "netflix",
    "кино",
    "сериал",
)

DOCUMENT_TOPIC_MARKERS: dict[str, tuple[str, ...]] = {
    "KMG-PR-1186": ("пропуск", "проксим", "карт", "турникет", "переда"),
    "KMG-VND-6677": ("конфликт", "интерес", "коррупц", "взятк", "доверия", "мүдде", "пара", "сенім"),
    "KMG-VND-4071": ("переписк", "совещан", "этик", "делов", "хат", "кездесу"),
    "KMG-DI-6241": ("smart", "испытатель", "мақсат", "цел", "адаптац"),
}

DOCUMENT_META: dict[str, tuple[str, str]] = {
    "KMG-PR-1186": ("Правила организации пропускного режима", "Пропускной режим"),
    "KMG-VND-6677": ("Инструкция по противодействию коррупции", "Конфликт интересов"),
    "KMG-VND-4071": ("Кодекс деловой этики", "Деловая переписка и совещания"),
    "KMG-DI-6241": ("Должностная инструкция", "SMART-цели"),
}

RUSSIAN_MARKERS_IN_KK_ANSWER = (
    "работник",
    "противоречие",
    "обязан",
    "принять",
    "меры",
    "это ",
    " это",
    "между",
    "личными",
    "интересами",
    "является",
    "подлежит",
    "передач",
    "запрещ",
    "должен",
    "сотрудник",
)


def detect_language(text: str) -> str:
    lower = text.lower()
    if any(char in lower for char in KAZAKH_CHARS):
        return "kk"

    tokens = re.findall(r"[a-zа-яёәғқңөұүһі]+", lower)
    if any(token in KAZAKH_WORDS for token in tokens):
        return "kk"

    return "ru"


def _normalize_chat_text(text: str) -> str:
    cleaned = re.sub(r"[^\wа-яёәғқңөұүһі\s]", " ", text.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def is_conversational_message(question: str) -> bool:
    normalized = _normalize_chat_text(question)
    if not normalized:
        return True

    tokens = normalized.split()
    if len(tokens) <= 3 and any(marker in normalized for marker in GREETING_MARKERS):
        return True
    if any(marker in normalized for marker in THANKS_MARKERS) and len(tokens) <= 6:
        return True
    if any(marker in normalized for marker in HELP_MARKERS):
        return True

    short_ack = {"да", "нет", "ок", "окей", "понятно", "ясно", "хорошо", "жақсы", "иә", "жоқ"}
    return len(tokens) <= 2 and tokens[0] in short_ack


def is_off_topic_question(question: str) -> bool:
    normalized = _normalize_chat_text(question)
    if any(marker in normalized for marker in OFF_TOPIC_MARKERS):
        return True

    has_domain = any(marker in normalized for marker in VND_DOMAIN_MARKERS)
    has_generic = any(marker in normalized for marker in GENERIC_QUESTION_MARKERS)
    return has_generic and not has_domain and len(normalized.split()) >= 3


def is_vnd_question(question: str) -> bool:
    if is_conversational_message(question) or is_off_topic_question(question):
        return False

    normalized = _normalize_chat_text(question)
    if len(normalized) < 8:
        return False

    has_domain = any(marker in normalized for marker in VND_DOMAIN_MARKERS)
    if not has_domain:
        return False

    return any(marker in normalized for marker in GENERIC_QUESTION_MARKERS) or has_domain


def conversational_answer(question: str, language: str) -> DigitalBuddyAnswer:
    normalized = _normalize_chat_text(question)

    if any(marker in normalized for marker in THANKS_MARKERS):
        text = (
            "Рақмет! Келесі сұрағыңызды жазыңыз — НҚА, тапсырмалар немесе бейімделу бойынша көмектесемін."
            if language == "kk"
            else "Пожалуйста! Если появятся вопросы по ВНД, задачам Дня 1 или этапам адаптации — напишите, помогу."
        )
    elif any(marker in normalized for marker in HELP_MARKERS):
        text = (
            "Мен Digital Buddy — НҚА (ВНД), Culture Fit, День 1 тапсырмалары және бейімделу "
            "бойынша сұрақтарға жауап беремін. Мысалы: «Проксим-картаны беруге бола ма?»"
            if language == "kk"
            else (
                "Я Digital Buddy — отвечаю по ВНД, Culture Fit, задачам Дня 1 и этапам адаптации. "
                "Например: «Можно ли передавать проксим-карту?» или «Что такое конфликт интересов?»"
            )
        )
    elif any(marker in normalized for marker in GREETING_MARKERS) or len(normalized.split()) <= 2:
        text = (
            "Сәлеметсіз бе! Мен Digital Buddy. НҚА, тапсырмалар немесе бейімделу туралы сұрақ қойыңыз — "
            "нақты жауап беремін."
            if language == "kk"
            else (
                "Здравствуйте! Рад вас видеть. Задайте вопрос по ВНД, задачам Дня 1 "
                "или этапам адаптации — отвечу по документам KMG."
            )
        )
    else:
        text = (
            "Сұрақты нақтырақ жазыңыз — мысалы, НҚА тармағы, тапсырма немесе бейімделу кезеңі туралы."
            if language == "kk"
            else (
                "Уточните, пожалуйста, вопрос — например, про раздел ВНД, задачу Дня 1 "
                "или этап адаптации. Так я смогу дать точный ответ."
            )
        )

    return DigitalBuddyAnswer(
        answer=text,
        source="Digital Buddy",
        section="Диалог" if language == "ru" else "Диалог",
        mode="chat",
    )


def align_source_with_answer(answer: DigitalBuddyAnswer) -> DigitalBuddyAnswer:
    if not answer.answer:
        return answer

    aligned = answer.model_copy()
    answer_lower = aligned.answer.lower()
    current_code = aligned.document_code

    if current_code:
        markers = DOCUMENT_TOPIC_MARKERS.get(current_code, ())
        if markers and any(marker in answer_lower for marker in markers):
            meta = DOCUMENT_META.get(current_code)
            if meta:
                aligned.source = meta[0]
            return aligned

    for code, markers in DOCUMENT_TOPIC_MARKERS.items():
        if any(marker in answer_lower for marker in markers):
            aligned.document_code = code
            meta = DOCUMENT_META.get(code)
            if meta:
                aligned.source = meta[0]
                if not aligned.section or aligned.section.startswith("п."):
                    aligned.section = meta[1]
            return aligned

    if current_code and not validate_answer_relevance(
        _question_from_answer_topics(answer_lower),
        aligned.answer,
    ):
        aligned.source = None
        aligned.section = None
        aligned.document_code = None

    return aligned


def _question_from_answer_topics(answer_lower: str) -> str:
    for code, markers in DOCUMENT_TOPIC_MARKERS.items():
        if any(marker in answer_lower for marker in markers):
            return markers[0]
    return ""


def expand_search_query(question: str, language: str = "ru") -> str:
    lower = question.lower()
    extras: list[str] = []

    for marker, ru_terms in KAZAKH_RAG_SYNONYMS:
        if marker in lower:
            extras.extend(ru_terms)

    if language == "kk" or detect_language(question) == "kk":
        extras.extend(["внд", "нқа", "регламент", "инструкция"])

    if not extras:
        return question

    unique_extras = list(dict.fromkeys(extras))
    return f"{question} {' '.join(unique_extras)}"


def ensure_formal_tone(text: str, language: str) -> str:
    if language == "ru":
        replacements = {
            r"\bты\b": "вы",
            r"\bТы\b": "Вы",
            r"\bтебе\b": "вам",
            r"\bТебе\b": "Вам",
            r"\bтвой\b": "ваш",
            r"\bТвой\b": "Ваш",
            r"\bтвоя\b": "ваша",
            r"\bтвоё\b": "ваше",
            r"\bтвои\b": "ваши",
        }
        result = text
        for pattern, replacement in replacements.items():
            result = re.sub(pattern, replacement, result)
        return result.strip()

    return text.strip()


def answer_has_kazakh(text: str) -> bool:
    lower = text.lower()
    return any(char in lower for char in KAZAKH_CHARS)


def _strip_document_codes(text: str) -> str:
    return re.sub(r"KMG-[A-Z0-9-]+", "", text)


def validate_answer_relevance(question: str, answer: str) -> bool:
    question_lower = question.lower()
    answer_lower = answer.lower()

    topic_checks: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
        (("конфликт", "мүдде", "интерес"), ("конфликт", "интерес", "мүдде")),
        (("проксим", "карт", "пропуск", "жоғал", "турникет"), ("проксим", "пропуск", "карт", "переда")),
        (("взятк", "пара", "коррупц"), ("взятк", "коррупц", "пара")),
        (("доверия", "сенім", "линия"), ("доверия", "сенім", "линия")),
        (("переписк", "хат", "делов"), ("переписк", "делов", "хат")),
        (("совещан", "кездесу"), ("совещан", "кездесу")),
        (("smart", "мақсат", "испытатель"), ("smart", "испытатель", "мақсат")),
    ]

    for question_markers, answer_markers in topic_checks:
        if any(marker in question_lower for marker in question_markers):
            return any(marker in answer_lower for marker in answer_markers)

    return True


def validate_answer_language(text: str, language: str) -> bool:
    cleaned = _strip_document_codes(text).strip()
    if len(cleaned) < 12:
        return False

    if language == "kk":
        if not answer_has_kazakh(cleaned):
            return False
        lower = cleaned.lower()
        return not any(marker in lower for marker in RUSSIAN_MARKERS_IN_KK_ANSWER)

    if answer_has_kazakh(cleaned):
        return False

    return bool(re.search(r"[а-яё]", cleaned.lower()))


def finalize_answer(
    answer: DigitalBuddyAnswer,
    language: str,
    *,
    add_footer: bool = True,
) -> DigitalBuddyAnswer:
    localized = answer.model_copy()
    localized.answer = ensure_formal_tone(localized.answer, language)

    if localized.mode in {"chat", "adaptation"}:
        return localized

    localized = align_source_with_answer(localized)

    if not validate_answer_language(localized.answer, language):
        localized.answer = _language_mismatch_fallback(language)

    if add_footer:
        footer = FOOTER_KK if language == "kk" else FOOTER_RU
        if footer.strip() not in localized.answer:
            localized.answer = f"{localized.answer}{footer}"

    if (
        language == "kk"
        and localized.source
        and localized.source != "Digital Buddy"
        and "(НҚА)" not in localized.source
    ):
        localized.source = f"{localized.source} (НҚА)"

    return localized


def _language_mismatch_fallback(language: str) -> str:
    if language == "kk":
        return (
            "Сұрағыңыз бойынша НҚА деректері табылды, бірақ жауапты дайындау мүмкін "
            "болмады. Сұрақты қайта жазыңыз немесе HR-ға хабарласыңыз."
        )

    return (
        "По вашему вопросу найдены данные ВНД, но не удалось сформировать ответ. "
        "Переформулируйте вопрос или обратитесь в HR."
    )


def localize_answer(answer: DigitalBuddyAnswer, language: str) -> DigitalBuddyAnswer:
    return finalize_answer(answer, language)


def no_context_answer(language: str) -> DigitalBuddyAnswer:
    if language == "kk":
        return DigitalBuddyAnswer(
            answer=(
                "Сұрағыңыз бойынша НҚА (ВНД) базасында нақты ақпарат табылмады. "
                "Сұрақты нақтылаңыз немесе HR-ға хабарласыңыз."
            ),
            source="Digital Buddy",
            section="НҚА бойынша іздеу",
            mode="no_context",
        )

    return DigitalBuddyAnswer(
        answer=(
            "В базе знаний ВНД нет информации по этому вопросу. "
            "Уточните формулировку или обратитесь в HR за дополнительной помощью."
        ),
        source="Digital Buddy",
        section="Поиск по ВНД",
        mode="no_context",
    )


CURATED_KK_BY_CODE: dict[str, str] = {
    "KMG-PR-1186": (
        "Проксим-картаны басқа адамдарға беруге болмайды. "
        "Бұл жеке кіру құралы және оны үшінші тұлғаларға беру тыйым салынады."
    ),
    "KMG-VND-6677": (
        "Мүдде конфликті — KMG қызметкерінің жеке және кәсіби мүдделерінің "
        "қайшы келуі. Мұндай жағдайды уақытылы хабарлау және реттеу шараларын "
        "қабылдау қажет."
    ),
    "KMG-VND-4071": (
        "Деловая хат алмасу мен келіссөздерде сыпайылық, нақтылық және "
        "құрмет сақталуы тиіс. KMG іскерлік этикасының нормаларын ұстаныңыз."
    ),
    "KMG-DI-6241": (
        "SMART-мақсаттар нақты, өлшенетін, қолжетімді, релевантты және "
        "уақыт бойынша шектелген болуы керек."
    ),
}


def curated_kk_answer(document_code: str | None) -> str | None:
    if not document_code:
        return None
    return CURATED_KK_BY_CODE.get(document_code)


def detect_adaptation_topic(question: str) -> str | None:
    normalized = _normalize_chat_text(question)

    one_to_one_markers = (
        "1:1",
        "1 1",
        "встреч",
        "кездесу",
        "руководител",
        "один на один",
        "подготов",
    )
    smart_markers = (
        "smart",
        "смарт",
        "цел",
        "кпд",
        "мақсат",
        "испытатель",
        "формулиров",
    )
    reflection_markers = (
        "рефлекс",
        "прогресс",
        "достиж",
        "сложност",
        "промежуточн",
        "оценк",
    )

    if any(marker in normalized for marker in one_to_one_markers):
        if any(
            marker in normalized
            for marker in ("подготов", "обсуд", "вопрос", "структур", "кездес")
        ):
            return "one_to_one_prep"
        return "one_to_one_prep"

    if any(marker in normalized for marker in smart_markers):
        return "smart_goals"

    if any(marker in normalized for marker in reflection_markers):
        return "reflection"

    return None


def adaptation_answer(topic: str, language: str) -> DigitalBuddyAnswer:
    if topic == "one_to_one_prep":
        if language == "kk":
            text = (
                "1:1 кездесуге дайындық — ұсынылатын құрылым:\n\n"
                "1. Міндеттер мен мақсаттар бойынша прогресс\n"
                "2. Қиындықтар мен кедергілер\n"
                "3. Орындалған жұмысқа кері байланыс\n"
                "4. Оқыту және дағдыларды дамыту\n"
                "5. Келесі 2 аптаға басымдықтар\n\n"
                "Сұрақ мысалдары:\n"
                "• Бұл аптада мен үшін қандай міндеттер басым?\n"
                "• Прогрессім сынақ мерзімі күтілетін деңгейіне сәйкес бе?\n"
                "• КПД жүйесінде мақсаттарды қалай дұрыс формулировать ету керек?"
            )
            source = "Бейімделу бағдарламасы"
            section = "1:1 кездесу"
        else:
            text = (
                "Структура разговора на встрече 1:1 с руководителем:\n\n"
                "1. Прогресс по задачам и целям испытательного срока\n"
                "2. Сложности и блокеры — что мешает работе\n"
                "3. Обратная связь по качеству выполнения задач\n"
                "4. Обучение и развитие — какие навыки усилить\n"
                "5. Следующие шаги и приоритеты на ближайшие 2 недели\n\n"
                "Примеры вопросов руководителю:\n"
                "• Какие задачи для меня приоритетны на этой неделе?\n"
                "• Соответствует ли мой прогресс ожиданиям на испытательный срок?\n"
                "• Как лучше сформулировать цели в системе КПД?\n"
                "• Какую обратную связь вы можете дать по моим последним задачам?\n\n"
                "Сформулируйте 2–3 вопроса своими словами — я помогу их уточнить."
            )
            source = "Программа адаптации"
            section = "Подготовка к 1:1 (F-18)"

    elif topic == "smart_goals":
        if language == "kk":
            text = (
                "SMART-мақсаттарды қоюға көмек — нақтылау сұрақтары:\n\n"
                "• Қандай нақты нәтиже көрсетілуі керек?\n"
                "• Сәттілікті қалай өлшейміз — сан, мерзім немесе сапа?\n"
                "• Міндеттің көлемі ағымдағы жүктемеге сай ма?\n"
                "• Мақсат бөлім KPI-мен және лауазымдық нұсқаулықпен "
                "қалай байланысты?\n"
                "• Қандай мерзімге дейін орындалуы тиіс?\n\n"
                "Мысал: «30 күн ішінде 3 ішкі регламентті оқып, "
                "руководительмен талқылау»."
            )
            source = "Лауазымдық нұсқаулық (KMG-DI-6241)"
            section = "SMART-мақсаттар"
        else:
            text = (
                "Помощь с постановкой целей по SMART на основе должностной "
                "инструкции и KPI подразделения:\n\n"
                "Уточняющие вопросы:\n"
                "• Какой конкретный результат вы должны показать к дедлайну?\n"
                "• Как измерить успех — в цифрах, сроках или качестве?\n"
                "• Реалистичен ли объём задачи с учётом текущей нагрузки?\n"
                "• Как цель связана с KPI подразделения и должностной инструкцией?\n"
                "• К какой дате цель должна быть достигнута?\n\n"
                "Пример формулировки: «До конца 1 месяца изучить 3 ключевых "
                "регламента подразделения и обсудить применение с руководителем».\n\n"
                "Опишите вашу задачу — помогу оформить её по SMART."
            )
            source = "Должностная инструкция (KMG-DI-6241)"
            section = "SMART-цели (F-19)"

    else:
        if language == "kk":
            text = (
                "Прогресс рефлексиясы — диалог форматында:\n\n"
                "1. Не уже получилось хорошо?\n"
                "   Қандай тапсырмалар мен процестерде прогресс сезіледі?\n\n"
                "2. Қай жерде қиындықтар бар?\n"
                "   Не түсініксіз немесе кедергі келтіреді?\n\n"
                "3. Не скорректировать?\n"
                "   Мақсаттар, оқыту, басымдықтар.\n\n"
                "Жауаптарыңызды қысқаша жазыңыз — аралық бағаға "
                "дайындыққа көмектесемін."
            )
            source = "Бейімделу бағдарламасы"
            section = "Рефлексия (F-21)"
        else:
            text = (
                "Рефлексия прогресса — давайте пройдём в формате диалога:\n\n"
                "1. Что уже получилось хорошо?\n"
                "   Опишите задачи, процессы или коммуникации, где вы чувствуете прогресс.\n\n"
                "2. Где сейчас есть сложности?\n"
                "   Укажите темы, документы, процессы или ожидания, которые нужно уточнить.\n\n"
                "3. Что нужно скорректировать?\n"
                "   Цели, обучение, приоритеты или формат взаимодействия с руководителем.\n\n"
                "Напишите короткие ответы на каждый пункт — помогу подготовиться "
                "к промежуточной оценке."
            )
            source = "Программа адаптации"
            section = "Рефлексия прогресса (F-21)"

    return DigitalBuddyAnswer(
        answer=text,
        source=source,
        section=section,
        document_code="KMG-DI-6241" if topic == "smart_goals" else None,
        mode="adaptation",
    )


def fallback_answer(language: str) -> DigitalBuddyAnswer:
    if language == "kk":
        return DigitalBuddyAnswer(
            answer=(
                "Сұрағыңызды түсіндім. Digital Buddy НҚА (ВНД) бойынша жауап іздейді "
                "және нақты құжат пен тармақты көрсетеді."
            ),
            source="Digital Buddy RAG",
            section="НҚА бойынша іздеу",
        )

    return DigitalBuddyAnswer(
        answer=(
            "Я понял ваш вопрос. Digital Buddy найдёт ответ по внутренним "
            "нормативным документам КМГ и укажет конкретный документ и пункт."
        ),
        source="Digital Buddy RAG",
        section="Поиск по ВНД",
    )
