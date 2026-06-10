import 'package:flutter/material.dart';

/// Порт src/data/stages.ts.
class OnboardingStage {
  final String id;
  final String title;
  final String description;
  final String status;
  final String period;
  final String? path;
  final IconData icon;
  final bool disabled;

  const OnboardingStage({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
    required this.period,
    this.path,
    required this.icon,
    this.disabled = false,
  });
}

const onboardingStages = [
  OnboardingStage(
    id: 'preboarding',
    title: 'Подготовка',
    description: 'Подготовка рабочего места, доступов, пропуска и техники',
    status: 'Готово',
    period: 'За 2 недели до выхода',
    icon: Icons.assignment_outlined,
    disabled: true,
  ),
  OnboardingStage(
    id: 'introduction',
    title: 'Знакомство',
    description: 'День 1: приветствие, видео, инструктажи и Digital Buddy',
    status: 'Активно',
    period: 'День 1',
    path: '/introduction',
    icon: Icons.waving_hand_outlined,
  ),
  OnboardingStage(
    id: 'engagement',
    title: 'Вовлечение',
    description: 'Culture Fit Nudges, первые задачи, опросы 14 и 30 дня',
    status: 'Активно',
    period: 'Дни 2–30',
    path: '/engagement',
    icon: Icons.bar_chart_outlined,
  ),
  OnboardingStage(
    id: 'adaptation',
    title: 'Адаптация',
    description: 'Встречи 1:1, SMART-цели, обучение и промежуточная оценка',
    status: 'Активно',
    period: 'Месяц 1–3',
    path: '/adaptation',
    icon: Icons.settings_outlined,
  ),
  OnboardingStage(
    id: 'retention',
    title: 'Закрепление',
    description: 'Итоговая оценка, HR-аналитика, NPS и развитие',
    status: 'Активно',
    period: 'Месяц 3–12',
    path: '/retention',
    icon: Icons.flag_outlined,
  ),
];
