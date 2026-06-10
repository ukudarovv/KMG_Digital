/// Зеркало BackendDayOneTask из src/api/onboardingApi.ts.
class OnboardingTask {
  final int id;
  final int employeeId;
  final String stage;
  final String title;
  final String? description;
  final DateTime? deadlineAt;
  final String status; // pending | in_progress | completed | overdue
  final bool isRequired;
  final String? vndDocumentCode;
  final String? externalLink;
  final bool confirmationRequired;
  final String? documentUrl;
  final DateTime? completedAt;

  const OnboardingTask({
    required this.id,
    required this.employeeId,
    required this.stage,
    required this.title,
    this.description,
    this.deadlineAt,
    required this.status,
    required this.isRequired,
    this.vndDocumentCode,
    this.externalLink,
    this.confirmationRequired = false,
    this.documentUrl,
    this.completedAt,
  });

  bool get isCompleted => status == 'completed';

  factory OnboardingTask.fromJson(Map<String, dynamic> json) {
    return OnboardingTask(
      id: json['id'] as int,
      employeeId: json['employee_id'] as int,
      stage: json['stage'] as String,
      title: json['title'] as String,
      description: json['description'] as String?,
      deadlineAt: json['deadline_at'] != null
          ? DateTime.tryParse(json['deadline_at'] as String)
          : null,
      status: (json['status'] as String?) ?? 'pending',
      isRequired: (json['is_required'] as bool?) ?? true,
      vndDocumentCode: json['vnd_document_code'] as String?,
      externalLink: json['external_link'] as String?,
      confirmationRequired: (json['confirmation_required'] as bool?) ?? false,
      documentUrl: json['document_url'] as String?,
      completedAt: json['completed_at'] != null
          ? DateTime.tryParse(json['completed_at'] as String)
          : null,
    );
  }
}
