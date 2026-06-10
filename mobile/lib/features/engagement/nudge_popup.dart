import 'package:flutter/material.dart';

import '../../core/theme/kmg_theme.dart';
import '../../models/nudge.dart';

/// Попап карточки Culture Fit (порт NudgePopup с сайта).
Future<void> showNudgePopup(
  BuildContext context, {
  required Nudge nudge,
  required bool alreadySentToday,
  required bool canSendToChat,
  required Future<void> Function() onSendToChat,
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
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: KmgColors.green100,
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                'Culture Fit · День ${nudge.dayNumber}',
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w700,
                  color: KmgColors.green800,
                ),
              ),
            ),
            const SizedBox(height: 12),
            Text(
              nudge.title,
              style: const TextStyle(
                fontSize: 17,
                fontWeight: FontWeight.w700,
                color: KmgColors.navy800,
              ),
            ),
            const SizedBox(height: 10),
            Text(
              nudge.text,
              style: const TextStyle(
                  fontSize: 14, height: 1.5, color: KmgColors.gray600),
            ),
            const SizedBox(height: 10),
            Text(
              'Источник: ${nudge.source}',
              style: const TextStyle(
                fontSize: 12,
                fontStyle: FontStyle.italic,
                color: KmgColors.gray400,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.of(dialogContext).pop(),
                    child: const Text('Закрыть'),
                  ),
                ),
                if (canSendToChat) ...[
                  const SizedBox(width: 8),
                  Expanded(
                    child: FilledButton.icon(
                      onPressed: alreadySentToday
                          ? null
                          : () async {
                              Navigator.of(dialogContext).pop();
                              await onSendToChat();
                            },
                      icon: const Icon(Icons.chat_bubble_outline, size: 18),
                      label: Text(
                          alreadySentToday ? 'Уже отправлено' : 'В чат'),
                    ),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    ),
  );
}
