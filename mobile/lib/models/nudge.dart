/// Зеркало BackendNudge / CurrentNudgeResponse из src/api/onboardingApi.ts.
class Nudge {
  final int id;
  final int dayNumber;
  final String title;
  final String text;
  final String source;
  final String? vndDocumentCode;
  final bool isActive;

  const Nudge({
    required this.id,
    required this.dayNumber,
    required this.title,
    required this.text,
    required this.source,
    this.vndDocumentCode,
    required this.isActive,
  });

  factory Nudge.fromJson(Map<String, dynamic> json) {
    return Nudge(
      id: (json['id'] as num?)?.toInt() ?? 0,
      dayNumber: (json['day_number'] as num?)?.toInt() ?? 0,
      title: (json['title'] as String?) ?? '',
      text: (json['text'] as String?) ?? '',
      source: (json['source'] as String?) ?? '',
      vndDocumentCode: json['vnd_document_code'] as String?,
      isActive: (json['is_active'] as bool?) ?? true,
    );
  }
}

class CurrentNudgeResponse {
  final Nudge? nudge;
  final bool alreadySentToday;
  final int adaptationDay;

  const CurrentNudgeResponse({
    this.nudge,
    required this.alreadySentToday,
    required this.adaptationDay,
  });

  factory CurrentNudgeResponse.fromJson(Map<String, dynamic> json) {
    return CurrentNudgeResponse(
      nudge: json['nudge'] != null
          ? Nudge.fromJson(json['nudge'] as Map<String, dynamic>)
          : null,
      alreadySentToday: (json['already_sent_today'] as bool?) ?? false,
      adaptationDay: (json['adaptation_day'] as int?) ?? 1,
    );
  }
}

class ShiftAdaptationDayResponse {
  final bool success;
  final int adaptationDay;
  final int nudgeDay;
  final String message;

  const ShiftAdaptationDayResponse({
    required this.success,
    required this.adaptationDay,
    required this.nudgeDay,
    required this.message,
  });

  factory ShiftAdaptationDayResponse.fromJson(Map<String, dynamic> json) {
    return ShiftAdaptationDayResponse(
      success: (json['success'] as bool?) ?? false,
      adaptationDay: (json['adaptation_day'] as int?) ?? 1,
      nudgeDay: (json['nudge_day'] as int?) ?? 1,
      message: (json['message'] as String?) ?? '',
    );
  }
}
