import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../api/onboarding_api.dart';
import '../../api/survey_api.dart';
import '../../core/config/app_config.dart';
import '../../core/theme/kmg_theme.dart';
import '../../models/nudge.dart';
import '../../models/onboarding_task.dart';
import '../../models/survey.dart';
import '../../shared/widgets/info_card.dart';
import '../../shared/widgets/kmg_scaffold.dart';
import '../../shared/widgets/progress_card.dart';
import '../../shared/widgets/task_card.dart';
import 'nudge_popup.dart';

const _employeeId = AppConfig.demoEmployeeId;

/// Этап 3 «Вовлечение» — порт EngagementPage.tsx.
class EngagementScreen extends StatefulWidget {
  const EngagementScreen({super.key});

  @override
  State<EngagementScreen> createState() => _EngagementScreenState();
}

class _EngagementScreenState extends State<EngagementScreen> {
  // Аналог sessionStorage-ключа kmg_engagement_popup_shown на сайте.
  static bool _popupShownThisSession = false;

  List<Nudge> _nudges = [];
  List<OnboardingTask> _engagementTasks = [];
  CurrentNudgeResponse? _currentNudgeData;
  SurveySummary? _surveySummary;

  bool _isLoading = true;
  bool _isSending = false;
  bool _isShiftingDay = false;
  String? _error;

  // Формы опросов.
  String _pulseComment = '';
  bool _pulseRoleClear = true;
  bool _pulseManagerSupport = true;
  bool _pulseHasQuestions = false;
  int _npsScore = 8;
  String _npsComment = '';

  Nudge? get _currentNudge => _currentNudgeData?.nudge;
  bool get _alreadySentToday => _currentNudgeData?.alreadySentToday ?? false;
  int get _adaptationDay => _currentNudgeData?.adaptationDay ?? 1;
  int get _nudgeDay => math.min(_adaptationDay, 23);
  int get _sentCount =>
      _alreadySentToday ? _nudgeDay : math.max(_nudgeDay - 1, 0);

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    try {
      await onboardingApi.setupEngagementDemo(_employeeId);
      final current =
          await _refreshState(openPopupForCurrent: !_popupShownThisSession);

      if (!_popupShownThisSession && current.nudge != null) {
        _popupShownThisSession = true;
      }
    } catch (e) {
      if (mounted) {
        setState(() => _error = 'Не удалось загрузить этап «Вовлечение». '
            'Проверьте, что backend запущен (${AppConfig.apiBaseUrl}).');
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<CurrentNudgeResponse> _refreshState(
      {bool openPopupForCurrent = false}) async {
    final results = await Future.wait([
      onboardingApi.getCultureFitNudges(),
      onboardingApi.getCurrentNudge(_employeeId),
      surveyApi.getSummary(_employeeId),
      onboardingApi.getEngagementTasks(_employeeId),
    ]);

    final current = results[1] as CurrentNudgeResponse;

    if (mounted) {
      setState(() {
        _nudges = results[0] as List<Nudge>;
        _currentNudgeData = current;
        _surveySummary = results[2] as SurveySummary;
        _engagementTasks = results[3] as List<OnboardingTask>;
      });

      if (openPopupForCurrent && current.nudge != null) {
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (mounted) {
            _openNudge(current.nudge!);
          }
        });
      }
    }

    return current;
  }

  void _openNudge(Nudge nudge) {
    showNudgePopup(
      context,
      nudge: nudge,
      alreadySentToday: _alreadySentToday,
      canSendToChat: nudge.dayNumber == _nudgeDay,
      onSendToChat: _sendToChat,
    );
  }

  Future<void> _sendToChat() async {
    if (_currentNudge == null || _alreadySentToday || _isSending) {
      return;
    }

    setState(() => _isSending = true);
    try {
      await onboardingApi.sendNudgeToChat(_employeeId);
      await _refreshState();
      _showSnack(
          'Карточка Culture Fit отправлена в Bitrix-чат от имени Digital Buddy.');
    } finally {
      if (mounted) {
        setState(() => _isSending = false);
      }
    }
  }

  Future<void> _shiftDay(int delta) async {
    final target = _adaptationDay + delta;
    if (_isShiftingDay || target < 2 || target > 30) {
      return;
    }

    setState(() => _isShiftingDay = true);
    try {
      await onboardingApi.shiftAdaptationDay(_employeeId, delta: delta);
      await _refreshState(openPopupForCurrent: true);
    } finally {
      if (mounted) {
        setState(() => _isShiftingDay = false);
      }
    }
  }

  Future<void> _simulateLogin() async {
    await onboardingApi.triggerUserLogin(_employeeId);
    final current = await _refreshState(openPopupForCurrent: true);
    if (current.alreadySentToday) {
      _showSnack(
          'Симуляция входа: карточка дня показана и продублирована в Bitrix-чат.');
    }
  }

  Future<void> _resetDemo() async {
    await onboardingApi.resetTodayNudgeDelivery(_employeeId);
    await _refreshState(openPopupForCurrent: true);
    _showSnack('Demo-флаг сброшен. Карточку снова можно отправить.');
  }

  Future<void> _completeTask(int taskId) async {
    await onboardingApi.completeTask(taskId);
    final tasks = await onboardingApi.getEngagementTasks(_employeeId);
    if (mounted) {
      setState(() => _engagementTasks = tasks);
    }
  }

  Future<void> _submitPulseSurvey() async {
    await surveyApi.createSurvey(
      _employeeId,
      SurveyCreatePayload(
        surveyType: 'pulse_day_14',
        comment: _pulseComment,
        answers: {
          'understands_role': _pulseRoleClear,
          'has_manager_support': _pulseManagerSupport,
          'has_open_questions': _pulseHasQuestions,
        },
      ),
    );

    final summary = await surveyApi.getSummary(_employeeId);
    if (mounted) {
      setState(() {
        _surveySummary = summary;
        _pulseComment = '';
      });
    }
    _showSnack('Пульс-опрос День 14 отправлен.');
  }

  Future<void> _submitNpsSurvey() async {
    await surveyApi.createSurvey(
      _employeeId,
      SurveyCreatePayload(
        surveyType: 'nps_day_30',
        npsScore: _npsScore,
        comment: _npsComment,
        answers: {'recommend_onboarding': _npsScore},
      ),
    );

    final summary = await surveyApi.getSummary(_employeeId);
    if (mounted) {
      setState(() {
        _surveySummary = summary;
        _npsComment = '';
      });
    }
    _showSnack('NPS-опрос День 30 отправлен.');
  }

  void _showSnack(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(message)));
    }
  }

  @override
  Widget build(BuildContext context) {
    return KmgScaffold(
      appBar: AppBar(
        title: const Text('Этап 3 · Вовлечение'),
        actions: [
          IconButton(
            tooltip: 'Симулировать вход',
            icon: const Icon(Icons.login),
            onPressed: _isLoading ? null : _simulateLogin,
          ),
          IconButton(
            tooltip: 'Сбросить demo-флаг',
            icon: const Icon(Icons.restart_alt),
            onPressed: _isLoading ? null : _resetDemo,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Padding(
                  padding: const EdgeInsets.all(16),
                  child: InfoCard(title: 'Ошибка', text: _error!),
                )
              : _currentNudge == null
                  ? const Padding(
                      padding: EdgeInsets.all(16),
                      child: InfoCard(
                        title: 'Карточка не найдена',
                        text: 'Проверьте, что backend запущен, миграции '
                            'применены, а seed-данные созданы.',
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh: () => _refreshState(),
                      child: _buildContent(),
                    ),
    );
  }

  Widget _buildContent() {
    final nudge = _currentNudge!;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                'Дни 2–30: ежедневные Culture Fit Nudges, первые HR-опросы '
                'и вовлечение в процессы.',
                style: const TextStyle(color: KmgColors.gray600, height: 1.45),
              ),
            ),
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              decoration: BoxDecoration(
                color: KmgColors.navy800,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                'День $_adaptationDay',
                style: const TextStyle(
                  color: KmgColors.white,
                  fontWeight: FontWeight.w700,
                  fontSize: 13,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        _buildTodayNudgeCard(nudge),
        const SizedBox(height: 16),
        ProgressCard(
          completed: _sentCount,
          total: _nudges.length,
          label: 'Culture Fit Nudges',
        ),
        const SizedBox(height: 16),
        _buildDayShiftCard(),
        const SizedBox(height: 20),
        _buildSectionTitle('Опросы'),
        const SizedBox(height: 12),
        _buildPulseSurveyCard(),
        const SizedBox(height: 12),
        _buildNpsSurveyCard(),
        const SizedBox(height: 20),
        _buildSectionTitle('ДИ и цели КПД'),
        const SizedBox(height: 12),
        if (_engagementTasks.isEmpty)
          const InfoCard(
            title: 'Задачи вовлечения не найдены',
            text: 'Запустите seed для создания задач F-10 и F-11.',
          )
        else
          for (final task in _engagementTasks) ...[
            TaskCard(task: task, onComplete: _completeTask),
            const SizedBox(height: 10),
          ],
        const SizedBox(height: 10),
        _buildSectionTitle('Банк Culture Fit · 23 карточки'),
        const SizedBox(height: 12),
        for (final item in _nudges) ...[
          _buildNudgeBankTile(item),
          const SizedBox(height: 8),
        ],
        const SizedBox(height: 12),
        InfoCard(
          title: 'Статус сегодня',
          text: _alreadySentToday
              ? 'Карточка уже отправлена сегодня.'
              : 'Карточка ещё не отправлена сегодня.',
        ),
      ],
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 17,
        fontWeight: FontWeight.w700,
        color: KmgColors.navy800,
      ),
    );
  }

  Widget _buildTodayNudgeCard(Nudge nudge) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [KmgColors.green800, KmgColors.green600],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Карточка дня $_nudgeDay',
            style: const TextStyle(color: KmgColors.green300, fontSize: 12.5),
          ),
          const SizedBox(height: 6),
          Text(
            nudge.title,
            style: const TextStyle(
              color: KmgColors.white,
              fontWeight: FontWeight.w700,
              fontSize: 16,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            nudge.text,
            maxLines: 4,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
                color: KmgColors.gray100, fontSize: 13.5, height: 1.45),
          ),
          const SizedBox(height: 8),
          Text(
            'Источник: ${nudge.source}',
            style: const TextStyle(color: KmgColors.green300, fontSize: 11.5),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              FilledButton(
                style: FilledButton.styleFrom(
                  backgroundColor: KmgColors.white,
                  foregroundColor: KmgColors.green800,
                ),
                onPressed: () => _openNudge(nudge),
                child: const Text('Открыть карточку'),
              ),
              FilledButton.icon(
                style: FilledButton.styleFrom(
                  backgroundColor: KmgColors.navy800,
                ),
                onPressed:
                    _alreadySentToday || _isSending ? null : _sendToChat,
                icon: const Icon(Icons.chat_bubble_outline, size: 17),
                label: Text(_isSending
                    ? 'Отправка...'
                    : _alreadySentToday
                        ? 'Уже отправлено'
                        : 'Отправить в чат'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDayShiftCard() {
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
          const Text(
            'Имитация дня',
            style: TextStyle(
                fontWeight: FontWeight.w700, color: KmgColors.navy800),
          ),
          const SizedBox(height: 4),
          const Text(
            'Сдвиньте день адаптации (2–30), чтобы открыть карточку '
            'следующего дня и протестировать механику OnUserLogin.',
            style: TextStyle(fontSize: 12.5, color: KmgColors.gray600),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              OutlinedButton.icon(
                onPressed: _isShiftingDay || _adaptationDay <= 2
                    ? null
                    : () => _shiftDay(-1),
                icon: const Icon(Icons.chevron_left),
                label: const Text('День −1'),
              ),
              Column(
                children: [
                  Text(
                    '$_adaptationDay',
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      color: KmgColors.green700,
                    ),
                  ),
                  const Text('из 30',
                      style: TextStyle(
                          fontSize: 11, color: KmgColors.gray400)),
                ],
              ),
              OutlinedButton.icon(
                onPressed: _isShiftingDay || _adaptationDay >= 30
                    ? null
                    : () => _shiftDay(1),
                icon: const Icon(Icons.chevron_right),
                label: const Text('День +1'),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPulseSurveyCard() {
    final completed = _surveySummary?.pulseDay14Completed ?? false;

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
          const Text('День 14',
              style: TextStyle(fontSize: 12, color: KmgColors.gray400)),
          const Text(
            'Пульс-опрос',
            style: TextStyle(
                fontWeight: FontWeight.w700,
                fontSize: 16,
                color: KmgColors.navy800),
          ),
          const SizedBox(height: 4),
          const Text(
            '3 вопроса о первых двух неделях адаптации. Результат видит HR.',
            style: TextStyle(fontSize: 12.5, color: KmgColors.gray600),
          ),
          const SizedBox(height: 10),
          if (completed)
            const InfoCard(
                success: true,
                title: 'Готово',
                text: 'Пульс-опрос уже отправлен')
          else ...[
            CheckboxListTile(
              dense: true,
              contentPadding: EdgeInsets.zero,
              controlAffinity: ListTileControlAffinity.leading,
              value: _pulseRoleClear,
              onChanged: (v) => setState(() => _pulseRoleClear = v ?? false),
              title: const Text('Я понимаю свою роль и задачи',
                  style: TextStyle(fontSize: 13.5)),
            ),
            CheckboxListTile(
              dense: true,
              contentPadding: EdgeInsets.zero,
              controlAffinity: ListTileControlAffinity.leading,
              value: _pulseManagerSupport,
              onChanged: (v) =>
                  setState(() => _pulseManagerSupport = v ?? false),
              title: const Text('У меня есть поддержка руководителя',
                  style: TextStyle(fontSize: 13.5)),
            ),
            CheckboxListTile(
              dense: true,
              contentPadding: EdgeInsets.zero,
              controlAffinity: ListTileControlAffinity.leading,
              value: _pulseHasQuestions,
              onChanged: (v) =>
                  setState(() => _pulseHasQuestions = v ?? false),
              title: const Text('У меня остались открытые вопросы',
                  style: TextStyle(fontSize: 13.5)),
            ),
            const SizedBox(height: 8),
            TextField(
              minLines: 2,
              maxLines: 4,
              onChanged: (v) => _pulseComment = v,
              decoration: const InputDecoration(
                hintText: 'Комментарий',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            FilledButton(
              onPressed: _submitPulseSurvey,
              child: const Text('Отправить пульс-опрос'),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildNpsSurveyCard() {
    final completed = _surveySummary?.npsDay30Completed ?? false;

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
          const Text('День 30',
              style: TextStyle(fontSize: 12, color: KmgColors.gray400)),
          const Text(
            'NPS-опрос',
            style: TextStyle(
                fontWeight: FontWeight.w700,
                fontSize: 16,
                color: KmgColors.navy800),
          ),
          const SizedBox(height: 4),
          const Text(
            'Оценка удовлетворённости адаптацией и открытый комментарий.',
            style: TextStyle(fontSize: 12.5, color: KmgColors.gray600),
          ),
          const SizedBox(height: 10),
          if (completed)
            InfoCard(
              success: true,
              title: 'Готово',
              text:
                  'NPS уже отправлен: ${_surveySummary?.latestNps ?? '—'}/10',
            )
          else ...[
            Text('Оценка NPS: $_npsScore/10',
                style: const TextStyle(
                    fontWeight: FontWeight.w600, fontSize: 13.5)),
            Slider(
              value: _npsScore.toDouble(),
              min: 0,
              max: 10,
              divisions: 10,
              label: '$_npsScore',
              onChanged: (v) => setState(() => _npsScore = v.round()),
            ),
            TextField(
              minLines: 2,
              maxLines: 4,
              onChanged: (v) => _npsComment = v,
              decoration: const InputDecoration(
                hintText: 'Комментарий',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 10),
            FilledButton(
              onPressed: _submitNpsSurvey,
              child: const Text('Отправить NPS'),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildNudgeBankTile(Nudge nudge) {
    final isActive = nudge.dayNumber == _nudgeDay;
    final isCompleted = nudge.dayNumber <= _sentCount;

    return InkWell(
      borderRadius: BorderRadius.circular(12),
      onTap: () => _openNudge(nudge),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: isActive
              ? KmgColors.green100
              : isCompleted
                  ? KmgColors.gray100
                  : KmgColors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isActive ? KmgColors.green400 : KmgColors.gray200,
          ),
        ),
        child: Row(
          children: [
            CircleAvatar(
              radius: 15,
              backgroundColor:
                  isActive ? KmgColors.green600 : KmgColors.gray200,
              child: isCompleted && !isActive
                  ? const Icon(Icons.check,
                      size: 16, color: KmgColors.green700)
                  : Text(
                      '${nudge.dayNumber}',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: isActive
                            ? KmgColors.white
                            : KmgColors.gray600,
                      ),
                    ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                nudge.title,
                style: const TextStyle(
                  fontSize: 13.5,
                  fontWeight: FontWeight.w600,
                  color: KmgColors.navy800,
                ),
              ),
            ),
            const Icon(Icons.chevron_right,
                size: 18, color: KmgColors.gray400),
          ],
        ),
      ),
    );
  }
}
