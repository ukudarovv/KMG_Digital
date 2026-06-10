/// Зеркало ApiMeeting / ApiGoal / ApiLearningModule из AdaptationPage.tsx.
class OneToOneMeeting {
  final int id;
  final String title;
  final String? description;
  final DateTime meetingDate;
  final String? meetingTime;
  final String status; // planned | completed | cancelled

  const OneToOneMeeting({
    required this.id,
    required this.title,
    this.description,
    required this.meetingDate,
    this.meetingTime,
    required this.status,
  });

  factory OneToOneMeeting.fromJson(Map<String, dynamic> json) {
    return OneToOneMeeting(
      id: json['id'] as int,
      title: json['title'] as String,
      description: json['description'] as String?,
      meetingDate: DateTime.parse(json['meeting_date'] as String),
      meetingTime: json['meeting_time'] as String?,
      status: json['status'] as String,
    );
  }
}

class SmartGoal {
  final int id;
  final String title;
  final String? description;
  final DateTime deadline;
  final String status; // planned | in_progress | completed | needs_update

  const SmartGoal({
    required this.id,
    required this.title,
    this.description,
    required this.deadline,
    required this.status,
  });

  factory SmartGoal.fromJson(Map<String, dynamic> json) {
    return SmartGoal(
      id: json['id'] as int,
      title: json['title'] as String,
      description: json['description'] as String?,
      deadline: DateTime.parse(json['deadline'] as String),
      status: json['status'] as String,
    );
  }
}

class LearningModule {
  final int id;
  final String title;
  final DateTime deadline;
  final int progress;
  final String status;

  const LearningModule({
    required this.id,
    required this.title,
    required this.deadline,
    required this.progress,
    required this.status,
  });

  factory LearningModule.fromJson(Map<String, dynamic> json) {
    return LearningModule(
      id: json['id'] as int,
      title: json['title'] as String,
      deadline: DateTime.parse(json['deadline'] as String),
      progress: (json['progress'] as num?)?.round() ?? 0,
      status: (json['status'] as String?) ?? 'not_started',
    );
  }
}
