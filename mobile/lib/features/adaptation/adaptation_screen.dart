import 'package:flutter/material.dart';

import '../../api/adaptation_api.dart';
import '../../core/config/app_config.dart';
import '../../core/theme/kmg_theme.dart';
import '../../models/adaptation.dart';
import '../../shared/widgets/info_card.dart';
import '../../shared/widgets/kmg_scaffold.dart';
import '../../shared/widgets/progress_card.dart';
import '../digital_buddy/buddy_chat_sheet.dart';

const _employeeId = AppConfig.demoEmployeeId;

const _reflectionQuestions = [
  (
    question: 'Что уже получилось хорошо?',
    hint: 'Опишите задачи, процессы или коммуникации, где вы чувствуете '
        'прогресс.',
  ),
  (
    question: 'Где сейчас есть сложности?',
    hint: 'Укажите темы, документы, процессы или ожидания, которые нужно '
        'уточнить.',
  ),
  (
    question: 'Что нужно обсудить с руководителем?',
    hint: 'Подготовьте вопросы для встречи 1:1.',
  ),
];

/// Этап 4 «Адаптация» — порт AdaptationPage.tsx (read-only).
class AdaptationScreen extends StatefulWidget {
  const AdaptationScreen({super.key});

  @override
  State<AdaptationScreen> createState() => _AdaptationScreenState();
}

class _AdaptationScreenState extends State<AdaptationScreen> {
  List<OneToOneMeeting> _meetings = [];
  List<SmartGoal> _goals = [];
  List<LearningModule> _modules = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final results = await Future.wait([
        adaptationApi.getMeetings(_employeeId),
        adaptationApi.getGoals(_employeeId),
        adaptationApi.getLearningModules(_employeeId),
      ]);

      if (mounted) {
        setState(() {
          _meetings = results[0] as List<OneToOneMeeting>;
          _goals = results[1] as List<SmartGoal>;
          _modules = results[2] as List<LearningModule>;
          _error = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _error = 'Не удалось загрузить данные адаптации. '
            'Проверьте, что backend запущен (${AppConfig.apiBaseUrl}).');
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  int get _completedGoals =>
      _goals.where((g) => g.status == 'completed').length;

  int get _averageLearningProgress => _modules.isEmpty
      ? 0
      : (_modules.fold<int>(0, (sum, m) => sum + m.progress) /
              _modules.length)
          .round();

  String _formatDate(DateTime date) =>
      '${date.day.toString().padLeft(2, '0')}.'
      '${date.month.toString().padLeft(2, '0')}.${date.year}';

  @override
  Widget build(BuildContext context) {
    return KmgScaffold(
      appBar: AppBar(title: const Text('Этап 4 · Адаптация')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Padding(
                  padding: const EdgeInsets.all(16),
                  child: InfoCard(title: 'Ошибка', text: _error!),
                )
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView(
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
                    children: [
                      const Text(
                        'Месяц 1–3: регулярные встречи 1:1, постановка целей '
                        'по SMART, промежуточная оценка и корректировка плана '
                        'адаптации.',
                        style:
                            TextStyle(color: KmgColors.gray600, height: 1.45),
                      ),
                      const SizedBox(height: 16),
                      _buildBuddyHero(),
                      const SizedBox(height: 16),
                      ProgressCard(
                        completed: _completedGoals,
                        total: _goals.isEmpty ? 1 : _goals.length,
                        label: 'SMART-цели',
                      ),
                      const SizedBox(height: 20),
                      _sectionTitle('Встречи 1:1'),
                      const SizedBox(height: 12),
                      for (final meeting in _meetings) ...[
                        _buildMeetingCard(meeting),
                        const SizedBox(height: 10),
                      ],
                      if (_meetings.isEmpty)
                        const InfoCard(
                            title: 'Встреч пока нет',
                            text: 'HR или руководитель добавят встречи 1:1.'),
                      const SizedBox(height: 16),
                      _sectionTitle('SMART-цели на испытательный срок'),
                      const SizedBox(height: 12),
                      for (final goal in _goals) ...[
                        _buildGoalCard(goal),
                        const SizedBox(height: 10),
                      ],
                      if (_goals.isEmpty)
                        const InfoCard(
                            title: 'Целей пока нет',
                            text:
                                'SMART-цели появятся после встречи с руководителем.'),
                      const SizedBox(height: 16),
                      _sectionTitle(
                          'Обучение · средний прогресс $_averageLearningProgress%'),
                      const SizedBox(height: 12),
                      for (final module in _modules) ...[
                        _buildLearningTile(module),
                        const SizedBox(height: 10),
                      ],
                      const SizedBox(height: 16),
                      _sectionTitle('Рефлексия перед промежуточной оценкой'),
                      const SizedBox(height: 12),
                      for (final item in _reflectionQuestions) ...[
                        _buildReflectionCard(item.question, item.hint),
                        const SizedBox(height: 10),
                      ],
                      const SizedBox(height: 6),
                      const InfoCard(
                        title: 'Промежуточная оценка',
                        text: 'За неделю до оценки Digital Buddy напомнит '
                            'сотруднику и руководителю, что нужно подготовить.',
                      ),
                    ],
                  ),
                ),
    );
  }

  Widget _sectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 17,
        fontWeight: FontWeight.w700,
        color: KmgColors.navy800,
      ),
    );
  }

  Widget _buildBuddyHero() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [KmgColors.navy800, KmgColors.navy600],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Digital Buddy помогает подготовиться',
            style: TextStyle(color: KmgColors.green300, fontSize: 12.5),
          ),
          const SizedBox(height: 6),
          const Text(
            'Перед встречей 1:1 соберите вопросы и зафиксируйте прогресс',
            style: TextStyle(
              color: KmgColors.white,
              fontWeight: FontWeight.w700,
              fontSize: 15,
              height: 1.35,
            ),
          ),
          const SizedBox(height: 12),
          FilledButton.icon(
            onPressed: () => showBuddyChat(context),
            icon: const Icon(Icons.chat_bubble_outline, size: 18),
            label: const Text('Подготовить вопросы'),
          ),
        ],
      ),
    );
  }

  Widget _buildMeetingCard(OneToOneMeeting meeting) {
    final isCompleted = meeting.status == 'completed';

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: KmgColors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: KmgColors.gray200),
      ),
      child: Row(
        children: [
          Icon(
            isCompleted ? Icons.event_available : Icons.event,
            color: isCompleted ? KmgColors.green600 : KmgColors.navy600,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  meeting.title,
                  style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                      color: KmgColors.navy800),
                ),
                const SizedBox(height: 2),
                Text(
                  '${_formatDate(meeting.meetingDate)} · '
                  '${meeting.meetingTime?.substring(0, 5) ?? '—'}',
                  style: const TextStyle(
                      fontSize: 12.5, color: KmgColors.gray600),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: isCompleted ? KmgColors.green100 : KmgColors.gray100,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              isCompleted
                  ? 'Завершена'
                  : meeting.status == 'planned'
                      ? 'Запланирована'
                      : meeting.status,
              style: TextStyle(
                fontSize: 11,
                fontWeight: FontWeight.w600,
                color:
                    isCompleted ? KmgColors.green800 : KmgColors.gray600,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildGoalCard(SmartGoal goal) {
    final (label, color) = switch (goal.status) {
      'completed' => ('Выполнена', KmgColors.green700),
      'needs_update' => ('Требует обновления', KmgColors.warning),
      'in_progress' => ('В работе', KmgColors.navy600),
      _ => ('Черновик', KmgColors.gray600),
    };

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: KmgColors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: KmgColors.gray200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.flag_outlined,
                  size: 18, color: KmgColors.green700),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  goal.title,
                  style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                      color: KmgColors.navy800),
                ),
              ),
            ],
          ),
          if ((goal.description ?? '').isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              goal.description!,
              style: const TextStyle(
                  fontSize: 12.5, height: 1.4, color: KmgColors.gray600),
            ),
          ],
          const SizedBox(height: 8),
          Row(
            children: [
              Text(
                'Дедлайн: ${_formatDate(goal.deadline)}',
                style:
                    const TextStyle(fontSize: 12, color: KmgColors.gray400),
              ),
              const Spacer(),
              Text(
                label,
                style: TextStyle(
                    fontSize: 12, fontWeight: FontWeight.w700, color: color),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildLearningTile(LearningModule module) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: KmgColors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: KmgColors.gray200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  module.title,
                  style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 13.5,
                      color: KmgColors.navy800),
                ),
              ),
              Text(
                '${module.progress}%',
                style: const TextStyle(
                    fontWeight: FontWeight.w800, color: KmgColors.green700),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: module.progress / 100,
              minHeight: 7,
              backgroundColor: KmgColors.gray100,
              valueColor:
                  const AlwaysStoppedAnimation(KmgColors.green500),
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'Дедлайн: ${_formatDate(module.deadline)}',
            style: const TextStyle(fontSize: 11.5, color: KmgColors.gray400),
          ),
        ],
      ),
    );
  }

  Widget _buildReflectionCard(String question, String hint) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: KmgColors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: KmgColors.gray200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            question,
            style: const TextStyle(
                fontWeight: FontWeight.w700,
                fontSize: 14,
                color: KmgColors.navy800),
          ),
          const SizedBox(height: 4),
          Text(
            hint,
            style: const TextStyle(fontSize: 12.5, color: KmgColors.gray600),
          ),
          const SizedBox(height: 10),
          const TextField(
            minLines: 2,
            maxLines: 4,
            decoration: InputDecoration(
              hintText: 'Введите короткий ответ...',
              border: OutlineInputBorder(),
            ),
          ),
        ],
      ),
    );
  }
}
