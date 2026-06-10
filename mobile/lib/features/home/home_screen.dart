import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/theme/kmg_theme.dart';
import '../../shared/widgets/kmg_scaffold.dart';
import 'stages_data.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return KmgScaffold(
      body: CustomScrollView(
        slivers: [
          const SliverAppBar(
            pinned: true,
            backgroundColor: KmgColors.navy800,
            title: Text('Программа адаптации'),
          ),
          SliverToBoxAdapter(
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [KmgColors.navy900, KmgColors.green800],
                ),
              ),
              padding: const EdgeInsets.fromLTRB(16, 20, 16, 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: KmgColors.green500,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text(
                          'KMG',
                          style: TextStyle(
                            color: KmgColors.white,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      const Text(
                        'team.kmg.kz',
                        style: TextStyle(
                            color: KmgColors.green300, fontSize: 13),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  const Text(
                    'Добро пожаловать в нашу команду',
                    style: TextStyle(
                      color: KmgColors.white,
                      fontSize: 21,
                      fontWeight: FontWeight.w700,
                      height: 1.25,
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'Пройдите пять этапов, чтобы уверенно начать работу '
                    'и почувствовать себя частью KMG',
                    style: TextStyle(
                      color: KmgColors.gray200,
                      fontSize: 13,
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
          ),
          SliverPadding(
            padding: const EdgeInsets.fromLTRB(16, 20, 16, 100),
            sliver: SliverList.separated(
              itemCount: onboardingStages.length,
              separatorBuilder: (_, _) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                return _StageCard(
                  step: index + 1,
                  stage: onboardingStages[index],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class _StageCard extends StatelessWidget {
  final int step;
  final OnboardingStage stage;

  const _StageCard({required this.step, required this.stage});

  @override
  Widget build(BuildContext context) {
    final disabled = stage.disabled;

    return InkWell(
      borderRadius: BorderRadius.circular(16),
      onTap: disabled || stage.path == null
          ? null
          : () => context.push(stage.path!),
      child: Opacity(
        opacity: disabled ? 0.55 : 1,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: KmgColors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: KmgColors.gray200),
          ),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: KmgColors.green100,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(stage.icon, color: KmgColors.green700),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          'Этап $step · ${stage.period}',
                          style: const TextStyle(
                            fontSize: 11.5,
                            fontWeight: FontWeight.w600,
                            color: KmgColors.gray400,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: disabled
                                ? KmgColors.gray100
                                : KmgColors.green100,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            disabled ? 'team.kmg.kz' : stage.status,
                            style: TextStyle(
                              fontSize: 10.5,
                              fontWeight: FontWeight.w700,
                              color: disabled
                                  ? KmgColors.gray600
                                  : KmgColors.green800,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      stage.title,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: KmgColors.navy800,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      stage.description,
                      style: const TextStyle(
                        fontSize: 12.5,
                        height: 1.4,
                        color: KmgColors.gray600,
                      ),
                    ),
                  ],
                ),
              ),
              if (!disabled)
                const Icon(Icons.chevron_right, color: KmgColors.gray400),
            ],
          ),
        ),
      ),
    );
  }
}
