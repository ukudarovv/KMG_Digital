import 'package:flutter/material.dart';

import '../../api/hr_api.dart';
import '../../api/survey_api.dart';
import '../../core/config/app_config.dart';
import '../../core/theme/kmg_theme.dart';
import '../../models/hr_detail.dart';
import '../../models/survey.dart';
import '../../shared/widgets/info_card.dart';
import '../../shared/widgets/kmg_scaffold.dart';
import '../../shared/widgets/progress_card.dart';

const _employeeId = AppConfig.demoEmployeeId;

/// Этап 5 «Закрепление» — порт RetentionPage.tsx.
class RetentionScreen extends StatefulWidget {
  const RetentionScreen({super.key});

  @override
  State<RetentionScreen> createState() => _RetentionScreenState();
}

class _RetentionScreenState extends State<RetentionScreen> {
  HrEmployeeDetail? _detail;
  SurveySummary? _surveySummary;
  bool _isLoading = true;
  bool _isSubmitting = false;
  String? _error;

  int _finalNpsScore = 9;
  String _finalNpsComment = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final results = await Future.wait([
        hrApi.getEmployeeDetail(_employeeId),
        surveyApi.getSummary(_employeeId),
      ]);

      if (mounted) {
        setState(() {
          _detail = results[0] as HrEmployeeDetail;
          _surveySummary = results[1] as SurveySummary;
          _error = null;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _error = 'Не удалось загрузить HR-аналитику. '
            'Проверьте, что backend запущен (${AppConfig.apiBaseUrl}).');
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _submitFinalNps() async {
    if (_isSubmitting) {
      return;
    }

    setState(() => _isSubmitting = true);
    try {
      await surveyApi.createSurvey(
        _employeeId,
        SurveyCreatePayload(
          surveyType: 'final_nps',
          npsScore: _finalNpsScore,
          comment: _finalNpsComment,
          answers: {
            'recommend_company': _finalNpsScore,
            'adaptation_quality': _finalNpsScore >= 9
                ? 'excellent'
                : _finalNpsScore >= 7
                    ? 'good'
                    : _finalNpsScore >= 5
                        ? 'neutral'
                        : 'needs_attention',
          },
        ),
      );

      await _load();
      if (mounted) {
        setState(() => _finalNpsComment = '');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Final NPS успешно отправлен.')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return KmgScaffold(
      appBar: AppBar(title: const Text('Этап 5 · Закрепление')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Padding(
                  padding: const EdgeInsets.all(16),
                  child: InfoCard(title: 'Ошибка', text: _error!),
                )
              : RefreshIndicator(
                  onRefresh: _load,
                  child: _buildContent(),
                ),
    );
  }

  Widget _buildContent() {
    final detail = _detail!;
    final employee = detail.employee;
    final activeRisks =
        detail.riskFlags.where((r) => r.status == 'active').length;
    final finalNps = _surveySummary?.latestNps ?? employee.nps ?? 0;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
      children: [
        const Text(
          'Месяц 3–12: итоговая оценка, HR-аналитика, sentiment-анализ, '
          'at_risk-флаги, финальный NPS и план развития сотрудника.',
          style: TextStyle(color: KmgColors.gray600, height: 1.45),
        ),
        const SizedBox(height: 16),
        _buildSummaryGrid(employee, finalNps),
        const SizedBox(height: 16),
        ProgressCard(
          completed: employee.completedTasks,
          total: employee.totalTasks == 0 ? 1 : employee.totalTasks,
          label: 'Задачи маршрута',
        ),
        const SizedBox(height: 20),
        _sectionTitle('Динамика тональности по неделям'),
        const SizedBox(height: 12),
        _buildSentimentChart(detail.sentimentWeeks),
        const SizedBox(height: 20),
        _sectionTitle('Final NPS · итоговая оценка адаптации'),
        const SizedBox(height: 12),
        _buildFinalNpsCard(),
        const SizedBox(height: 20),
        _sectionTitle('Флаги риска адаптации (at_risk)'),
        const SizedBox(height: 12),
        if (detail.riskFlags.isEmpty)
          const InfoCard(
              success: true,
              title: 'Рисков нет',
              text: 'Активных риск-флагов не обнаружено.')
        else
          for (final risk in detail.riskFlags) ...[
            _buildRiskCard(risk),
            const SizedBox(height: 10),
          ],
        const SizedBox(height: 10),
        _sectionTitle('Рекомендации Digital Buddy'),
        const SizedBox(height: 12),
        for (final item in detail.recommendations) ...[
          _buildRecommendationCard(item),
          const SizedBox(height: 10),
        ],
        const SizedBox(height: 10),
        InfoCard(title: 'HR-отчёт на 90-й день', text: detail.hrSummary),
        const SizedBox(height: 12),
        InfoCard(
          title: 'Активные риски',
          text: 'Сейчас активных риск-флагов: $activeRisks. HR получит '
              'мягкий сигнал для дополнительного контакта.',
        ),
        const SizedBox(height: 12),
        InfoCard(
          success: true,
          title: 'Передача в HR-аналитику',
          text: detail.privacyNote.isNotEmpty
              ? detail.privacyNote
              : 'Данные маршрута, опросов и sentiment готовы к передаче в '
                  'HR-аналитику KMG. Личная переписка не передаётся.',
        ),
      ],
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

  Widget _buildSummaryGrid(HrEmployee employee, int finalNps) {
    final items = [
      (Icons.bar_chart, 'Маршрут', '${employee.progress}%'),
      (
        Icons.task_alt,
        'Задачи',
        '${employee.completedTasks}/${employee.totalTasks}'
      ),
      (Icons.description_outlined, 'Финальный NPS', '$finalNps/10'),
      (Icons.shield_outlined, 'Риск', employee.riskLevel),
    ];

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 10,
      crossAxisSpacing: 10,
      childAspectRatio: 1.9,
      children: [
        for (final (icon, label, value) in items)
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: KmgColors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: KmgColors.gray200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Row(
                  children: [
                    Icon(icon, size: 18, color: KmgColors.green700),
                    const SizedBox(width: 6),
                    Text(label,
                        style: const TextStyle(
                            fontSize: 12, color: KmgColors.gray600)),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w800,
                    color: KmgColors.navy800,
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildSentimentChart(List<SentimentWeek> weeks) {
    if (weeks.isEmpty) {
      return const InfoCard(
          title: 'Нет данных',
          text: 'Sentiment-аналитика появится после первых диалогов.');
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: KmgColors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: KmgColors.gray200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (final week in weeks) ...[
            Text(week.week,
                style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: KmgColors.gray600)),
            const SizedBox(height: 4),
            _buildSentimentBar(week),
            const SizedBox(height: 12),
          ],
          Row(
            children: const [
              _LegendDot(color: KmgColors.green500, label: 'Позитив'),
              SizedBox(width: 12),
              _LegendDot(color: KmgColors.gray400, label: 'Нейтрально'),
              SizedBox(width: 12),
              _LegendDot(color: KmgColors.danger, label: 'Негатив'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSentimentBar(SentimentWeek week) {
    final total = week.positive + week.neutral + week.negative;
    if (total == 0) {
      return Container(height: 14, color: KmgColors.gray100);
    }

    return ClipRRect(
      borderRadius: BorderRadius.circular(6),
      child: Row(
        children: [
          Expanded(
            flex: week.positive,
            child: Container(height: 14, color: KmgColors.green500),
          ),
          Expanded(
            flex: week.neutral,
            child: Container(height: 14, color: KmgColors.gray400),
          ),
          Expanded(
            flex: week.negative,
            child: Container(height: 14, color: KmgColors.danger),
          ),
        ],
      ),
    );
  }

  Widget _buildFinalNpsCard() {
    final completed = _surveySummary?.finalNpsCompleted ?? false;

    if (completed) {
      return InfoCard(
        success: true,
        title: 'Final NPS уже отправлен',
        text: 'Последняя NPS-оценка: ${_surveySummary?.latestNps ?? '—'}/10',
      );
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: KmgColors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: KmgColors.gray200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Оценка: $_finalNpsScore/10',
            style: const TextStyle(
                fontWeight: FontWeight.w700,
                fontSize: 15,
                color: KmgColors.navy800),
          ),
          Slider(
            value: _finalNpsScore.toDouble(),
            min: 0,
            max: 10,
            divisions: 10,
            label: '$_finalNpsScore',
            onChanged: (v) => setState(() => _finalNpsScore = v.round()),
          ),
          TextField(
            minLines: 2,
            maxLines: 4,
            onChanged: (v) => _finalNpsComment = v,
            decoration: const InputDecoration(
              hintText: 'Комментарий к итоговой адаптации',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: _isSubmitting ? null : _submitFinalNps,
            child:
                Text(_isSubmitting ? 'Отправка...' : 'Отправить Final NPS'),
          ),
        ],
      ),
    );
  }

  Widget _buildRiskCard(RiskFlag risk) {
    final color = switch (risk.level) {
      'high' => KmgColors.danger,
      'medium' => KmgColors.warning,
      _ => KmgColors.green600,
    };

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: KmgColors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: KmgColors.gray200),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.warning_amber_outlined, color: color, size: 22),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        risk.title,
                        style: const TextStyle(
                            fontWeight: FontWeight.w700,
                            fontSize: 14,
                            color: KmgColors.navy800),
                      ),
                    ),
                    Text(
                      risk.status == 'active' ? 'Активен' : 'Решён',
                      style: TextStyle(
                        fontSize: 11.5,
                        fontWeight: FontWeight.w700,
                        color: risk.status == 'active'
                            ? color
                            : KmgColors.green700,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  risk.description,
                  style: const TextStyle(
                      fontSize: 12.5,
                      height: 1.4,
                      color: KmgColors.gray600),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationCard(DevelopmentRecommendation item) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: KmgColors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: KmgColors.gray200),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.lightbulb_outline,
              color: KmgColors.green600, size: 22),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.title,
                  style: const TextStyle(
                      fontWeight: FontWeight.w700,
                      fontSize: 14,
                      color: KmgColors.navy800),
                ),
                const SizedBox(height: 4),
                Text(
                  item.description,
                  style: const TextStyle(
                      fontSize: 12.5,
                      height: 1.4,
                      color: KmgColors.gray600),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _LegendDot extends StatelessWidget {
  final Color color;
  final String label;

  const _LegendDot({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 4),
        Text(label,
            style:
                const TextStyle(fontSize: 11.5, color: KmgColors.gray600)),
      ],
    );
  }
}
