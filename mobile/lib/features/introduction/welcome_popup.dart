import 'package:flutter/material.dart';

import '../../core/theme/kmg_theme.dart';

/// Приветственный попап Digital Buddy при входе (порт DigitalBuddyPopup).
Future<void> showWelcomePopup(
  BuildContext context, {
  required String employeeName,
  required int adaptationDay,
  required int completedTasks,
  required int totalTasks,
  String? nextTaskTitle,
  required VoidCallback onWatchVideo,
  required VoidCallback onAskQuestion,
}) {
  return showDialog(
    context: context,
    builder: (dialogContext) => Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const CircleAvatar(
                  radius: 22,
                  backgroundColor: KmgColors.green500,
                  child:
                      Icon(Icons.smart_toy_outlined, color: KmgColors.white),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Здравствуйте, $employeeName!',
                        style: const TextStyle(
                          fontWeight: FontWeight.w700,
                          fontSize: 16,
                          color: KmgColors.navy800,
                        ),
                      ),
                      Text(
                        'Digital Buddy · День $adaptationDay',
                        style: const TextStyle(
                            fontSize: 12, color: KmgColors.gray600),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            const Text(
              'Добро пожаловать в КМГ! Я помогу пройти первый день: '
              'посмотрите видеообращение и выполните обязательные инструктажи.',
              style: TextStyle(
                  fontSize: 13.5, height: 1.45, color: KmgColors.gray600),
            ),
            const SizedBox(height: 14),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: KmgColors.green100,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Прогресс: $completedTasks из $totalTasks задач',
                    style: const TextStyle(
                      fontWeight: FontWeight.w700,
                      fontSize: 13,
                      color: KmgColors.green800,
                    ),
                  ),
                  if (nextTaskTitle != null) ...[
                    const SizedBox(height: 4),
                    Text(
                      'Следующая задача: $nextTaskTitle',
                      style: const TextStyle(
                          fontSize: 12.5, color: KmgColors.green800),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: () {
                      Navigator.of(dialogContext).pop();
                      onWatchVideo();
                    },
                    icon: const Icon(Icons.play_arrow, size: 18),
                    label: const Text('Видео'),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {
                      Navigator.of(dialogContext).pop();
                      onAskQuestion();
                    },
                    icon: const Icon(Icons.chat_bubble_outline, size: 18),
                    label: const Text('Задать вопрос'),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    ),
  );
}
