import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/config/app_config.dart';
import '../../core/theme/kmg_theme.dart';
import '../../models/onboarding_task.dart';
import 'pdf_viewer_screen.dart';

/// Порт компонента TaskCard с сайта: материал ВНД, внешняя ссылка,
/// подтверждение ознакомления.
class TaskCard extends StatelessWidget {
  final OnboardingTask task;
  final Future<void> Function(int taskId) onComplete;

  const TaskCard({super.key, required this.task, required this.onComplete});

  String? get _documentFullUrl {
    final docUrl = task.documentUrl;
    if (docUrl == null || docUrl.isEmpty) {
      return null;
    }
    if (docUrl.startsWith('http')) {
      return docUrl;
    }
    return '${AppConfig.apiBaseUrl}$docUrl';
  }

  void _openDocument(BuildContext context) {
    final url = _documentFullUrl;
    if (url == null) {
      return;
    }
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => PdfViewerScreen(url: url, title: task.title),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final completed = task.isCompleted;
    final deadline = task.deadlineAt != null
        ? '${task.deadlineAt!.day.toString().padLeft(2, '0')}.'
            '${task.deadlineAt!.month.toString().padLeft(2, '0')}.'
            '${task.deadlineAt!.year}'
        : 'Сегодня до 18:00';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: completed ? KmgColors.green100 : KmgColors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: completed ? KmgColors.green300 : KmgColors.gray200,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                completed ? Icons.check_circle : Icons.radio_button_unchecked,
                color: completed ? KmgColors.green600 : KmgColors.gray400,
                size: 22,
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      task.title,
                      style: TextStyle(
                        fontWeight: FontWeight.w700,
                        fontSize: 15,
                        color: KmgColors.navy800,
                        decoration:
                            completed ? TextDecoration.lineThrough : null,
                      ),
                    ),
                    if ((task.description ?? '').isNotEmpty) ...[
                      const SizedBox(height: 4),
                      Text(
                        task.description!,
                        style: const TextStyle(
                          fontSize: 13,
                          height: 1.4,
                          color: KmgColors.gray600,
                        ),
                      ),
                    ],
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        const Icon(Icons.schedule,
                            size: 14, color: KmgColors.gray400),
                        const SizedBox(width: 4),
                        Text(
                          deadline,
                          style: const TextStyle(
                            fontSize: 12,
                            color: KmgColors.gray400,
                          ),
                        ),
                        if (task.isRequired) ...[
                          const SizedBox(width: 10),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: KmgColors.green100,
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: const Text(
                              'Обязательно',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: KmgColors.green800,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
          if (!completed || _documentFullUrl != null) ...[
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                if (_documentFullUrl != null)
                  OutlinedButton.icon(
                    onPressed: () => _openDocument(context),
                    icon: const Icon(Icons.description_outlined, size: 18),
                    label: const Text('Открыть материал'),
                  ),
                if ((task.externalLink ?? '').isNotEmpty)
                  OutlinedButton.icon(
                    onPressed: () => launchUrl(
                      Uri.parse(task.externalLink!),
                      mode: LaunchMode.externalApplication,
                    ),
                    icon: const Icon(Icons.open_in_new, size: 18),
                    label: const Text('Перейти'),
                  ),
                if (!completed)
                  FilledButton.icon(
                    onPressed: () => onComplete(task.id),
                    icon: const Icon(Icons.check, size: 18),
                    label: const Text('Подтвердить ознакомление'),
                  ),
              ],
            ),
          ],
        ],
      ),
    );
  }
}
