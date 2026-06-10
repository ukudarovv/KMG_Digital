import 'package:flutter/material.dart';

import '../../core/theme/kmg_theme.dart';

/// Порт компонента ProgressBar с сайта.
class ProgressCard extends StatelessWidget {
  final int completed;
  final int total;
  final String label;

  const ProgressCard({
    super.key,
    required this.completed,
    required this.total,
    this.label = 'Прогресс',
  });

  @override
  Widget build(BuildContext context) {
    final ratio = total > 0 ? completed / total : 0.0;
    final percent = (ratio * 100).round();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: KmgColors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: KmgColors.gray200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontWeight: FontWeight.w600,
                  color: KmgColors.navy800,
                ),
              ),
              Text(
                '$completed / $total · $percent%',
                style: const TextStyle(
                  fontWeight: FontWeight.w700,
                  color: KmgColors.green700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: LinearProgressIndicator(
              value: ratio,
              minHeight: 10,
              backgroundColor: KmgColors.gray100,
              valueColor: const AlwaysStoppedAnimation(KmgColors.green500),
            ),
          ),
        ],
      ),
    );
  }
}
