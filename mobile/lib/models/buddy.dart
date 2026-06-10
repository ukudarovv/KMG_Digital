/// Зеркало DigitalBuddyAnswer / DigitalBuddyStatus из src/api/digitalBuddyApi.ts.
class BuddyAnswer {
  final String answer;
  final String? source;
  final String? section;
  final String? documentCode;
  final String? language; // ru | kk
  final String? mode; // llm | rag | fallback | no_context

  const BuddyAnswer({
    required this.answer,
    this.source,
    this.section,
    this.documentCode,
    this.language,
    this.mode,
  });

  factory BuddyAnswer.fromJson(Map<String, dynamic> json) {
    return BuddyAnswer(
      answer: (json['answer'] as String?) ?? '',
      source: json['source'] as String?,
      section: json['section'] as String?,
      documentCode: json['document_code'] as String?,
      language: json['language'] as String?,
      mode: json['mode'] as String?,
    );
  }
}

class BuddyStatus {
  final bool llmEnabled;
  final bool llmAvailable;
  final String llmModel;
  final bool modelReady;

  const BuddyStatus({
    required this.llmEnabled,
    required this.llmAvailable,
    required this.llmModel,
    required this.modelReady,
  });

  factory BuddyStatus.fromJson(Map<String, dynamic> json) {
    return BuddyStatus(
      llmEnabled: (json['llm_enabled'] as bool?) ?? false,
      llmAvailable: (json['llm_available'] as bool?) ?? false,
      llmModel: (json['llm_model'] as String?) ?? '',
      modelReady: (json['model_ready'] as bool?) ?? false,
    );
  }
}
