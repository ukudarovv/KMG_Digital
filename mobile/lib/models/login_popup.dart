import 'nudge.dart';

/// Зеркало LoginPopupResponse из src/api/onboardingApi.ts.
class LoginPopupNextTask {
  final String title;
  final String? description;
  final String? deadlineAt;

  const LoginPopupNextTask({
    required this.title,
    this.description,
    this.deadlineAt,
  });

  factory LoginPopupNextTask.fromJson(Map<String, dynamic> json) {
    return LoginPopupNextTask(
      title: json['title'] as String,
      description: json['description'] as String?,
      deadlineAt: json['deadline_at'] as String?,
    );
  }
}

class LoginPopup {
  final String employeeName;
  final int adaptationDay;
  final String mode;
  final bool nudgeSent;
  final int completedTasks;
  final int totalTasks;
  final String videoUrl;
  final Nudge? nudge;
  final LoginPopupNextTask? nextTask;

  const LoginPopup({
    required this.employeeName,
    required this.adaptationDay,
    required this.mode,
    required this.nudgeSent,
    required this.completedTasks,
    required this.totalTasks,
    required this.videoUrl,
    this.nudge,
    this.nextTask,
  });

  factory LoginPopup.fromJson(Map<String, dynamic> json) {
    return LoginPopup(
      employeeName: (json['employee_name'] as String?) ?? '',
      adaptationDay: (json['adaptation_day'] as int?) ?? 1,
      mode: (json['mode'] as String?) ?? '',
      nudgeSent: (json['nudge_sent'] as bool?) ?? false,
      completedTasks: (json['completed_tasks'] as int?) ?? 0,
      totalTasks: (json['total_tasks'] as int?) ?? 0,
      videoUrl: (json['video_url'] as String?) ?? '',
      nudge: json['nudge'] != null
          ? Nudge.fromJson(json['nudge'] as Map<String, dynamic>)
          : null,
      nextTask: json['next_task'] != null
          ? LoginPopupNextTask.fromJson(
              json['next_task'] as Map<String, dynamic>)
          : null,
    );
  }
}
