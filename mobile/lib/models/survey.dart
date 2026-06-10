/// Зеркало типов из src/api/surveyApi.ts.
class SurveySummary {
  final bool pulseDay14Completed;
  final bool npsDay30Completed;
  final bool finalNpsCompleted;
  final int? latestNps;

  const SurveySummary({
    required this.pulseDay14Completed,
    required this.npsDay30Completed,
    required this.finalNpsCompleted,
    this.latestNps,
  });

  factory SurveySummary.fromJson(Map<String, dynamic> json) {
    return SurveySummary(
      pulseDay14Completed: (json['pulse_day_14_completed'] as bool?) ?? false,
      npsDay30Completed: (json['nps_day_30_completed'] as bool?) ?? false,
      finalNpsCompleted: (json['final_nps_completed'] as bool?) ?? false,
      latestNps: json['latest_nps'] as int?,
    );
  }
}

class SurveyCreatePayload {
  final String surveyType; // pulse_day_14 | nps_day_30 | final_nps
  final int? npsScore;
  final String? comment;
  final Map<String, dynamic>? answers;

  const SurveyCreatePayload({
    required this.surveyType,
    this.npsScore,
    this.comment,
    this.answers,
  });

  Map<String, dynamic> toJson() => {
        'survey_type': surveyType,
        'nps_score': npsScore,
        'comment': comment,
        'answers': answers,
      };
}
