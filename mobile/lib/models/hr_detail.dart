/// Зеркало HREmployeeDetailResponse из src/api/hrApi.ts
/// (используется только read-only на экране «Закрепление»).
class HrEmployee {
  final int id;
  final String fullName;
  final String? position;
  final String? department;
  final String currentStage;
  final int progress;
  final int completedTasks;
  final int totalTasks;
  final int? nps;
  final String sentiment; // positive | neutral | negative
  final String riskLevel; // low | medium | high

  const HrEmployee({
    required this.id,
    required this.fullName,
    this.position,
    this.department,
    required this.currentStage,
    required this.progress,
    required this.completedTasks,
    required this.totalTasks,
    this.nps,
    required this.sentiment,
    required this.riskLevel,
  });

  factory HrEmployee.fromJson(Map<String, dynamic> json) {
    return HrEmployee(
      id: json['id'] as int,
      fullName: (json['full_name'] as String?) ?? '',
      position: json['position'] as String?,
      department: json['department'] as String?,
      currentStage: (json['current_stage'] as String?) ?? '',
      progress: (json['progress'] as num?)?.round() ?? 0,
      completedTasks: (json['completed_tasks'] as int?) ?? 0,
      totalTasks: (json['total_tasks'] as int?) ?? 0,
      nps: json['nps'] as int?,
      sentiment: (json['sentiment'] as String?) ?? 'neutral',
      riskLevel: (json['risk_level'] as String?) ?? 'low',
    );
  }
}

class SentimentWeek {
  final String week;
  final int positive;
  final int neutral;
  final int negative;

  const SentimentWeek({
    required this.week,
    required this.positive,
    required this.neutral,
    required this.negative,
  });

  factory SentimentWeek.fromJson(Map<String, dynamic> json) {
    return SentimentWeek(
      week: (json['week'] as String?) ?? '',
      positive: (json['positive'] as num?)?.round() ?? 0,
      neutral: (json['neutral'] as num?)?.round() ?? 0,
      negative: (json['negative'] as num?)?.round() ?? 0,
    );
  }
}

class RiskFlag {
  final int id;
  final String title;
  final String description;
  final String level; // low | medium | high
  final String status; // active | resolved

  const RiskFlag({
    required this.id,
    required this.title,
    required this.description,
    required this.level,
    required this.status,
  });

  factory RiskFlag.fromJson(Map<String, dynamic> json) {
    return RiskFlag(
      id: json['id'] as int,
      title: (json['title'] as String?) ?? '',
      description: (json['description'] as String?) ?? '',
      level: (json['level'] as String?) ?? 'low',
      status: (json['status'] as String?) ?? 'active',
    );
  }
}

class DevelopmentRecommendation {
  final int id;
  final String title;
  final String description;
  final String priority; // low | medium | high

  const DevelopmentRecommendation({
    required this.id,
    required this.title,
    required this.description,
    required this.priority,
  });

  factory DevelopmentRecommendation.fromJson(Map<String, dynamic> json) {
    return DevelopmentRecommendation(
      id: json['id'] as int,
      title: (json['title'] as String?) ?? '',
      description: (json['description'] as String?) ?? '',
      priority: (json['priority'] as String?) ?? 'medium',
    );
  }
}

class HrEmployeeDetail {
  final HrEmployee employee;
  final List<SentimentWeek> sentimentWeeks;
  final List<RiskFlag> riskFlags;
  final List<DevelopmentRecommendation> recommendations;
  final String hrSummary;
  final String privacyNote;

  const HrEmployeeDetail({
    required this.employee,
    required this.sentimentWeeks,
    required this.riskFlags,
    required this.recommendations,
    required this.hrSummary,
    required this.privacyNote,
  });

  factory HrEmployeeDetail.fromJson(Map<String, dynamic> json) {
    return HrEmployeeDetail(
      employee: HrEmployee.fromJson(json['employee'] as Map<String, dynamic>),
      sentimentWeeks: ((json['sentiment_weeks'] as List?) ?? [])
          .map((e) => SentimentWeek.fromJson(e as Map<String, dynamic>))
          .toList(),
      riskFlags: ((json['risk_flags'] as List?) ?? [])
          .map((e) => RiskFlag.fromJson(e as Map<String, dynamic>))
          .toList(),
      recommendations: ((json['recommendations'] as List?) ?? [])
          .map((e) =>
              DevelopmentRecommendation.fromJson(e as Map<String, dynamic>))
          .toList(),
      hrSummary: (json['hr_summary'] as String?) ?? '',
      privacyNote: (json['privacy_note'] as String?) ?? '',
    );
  }
}
