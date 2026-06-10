import 'package:flutter/material.dart';

import '../../core/theme/kmg_theme.dart';

class InfoCard extends StatelessWidget {
  final String title;
  final String text;
  final bool success;

  const InfoCard({
    super.key,
    required this.title,
    required this.text,
    this.success = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: success ? KmgColors.green100 : KmgColors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: success ? KmgColors.green300 : KmgColors.gray200,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 15,
              color: KmgColors.navy800,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            text,
            style: const TextStyle(
              fontSize: 13.5,
              height: 1.45,
              color: KmgColors.gray600,
            ),
          ),
        ],
      ),
    );
  }
}
