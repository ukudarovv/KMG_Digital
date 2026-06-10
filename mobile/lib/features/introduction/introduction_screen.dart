import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../api/onboarding_api.dart';
import '../../core/config/app_config.dart';
import '../../core/theme/kmg_theme.dart';
import '../../models/login_popup.dart';
import '../../models/onboarding_task.dart';
import '../../shared/widgets/info_card.dart';
import '../../shared/widgets/kmg_scaffold.dart';
import '../../shared/widgets/progress_card.dart';
import '../../shared/widgets/task_card.dart';
import '../digital_buddy/buddy_chat_sheet.dart';
import 'welcome_popup.dart';

const _employeeId = AppConfig.demoEmployeeId;

/// Этап 2 «Знакомство» — порт IntroductionPage.tsx.
class IntroductionScreen extends StatefulWidget {
  const IntroductionScreen({super.key});

  @override
  State<IntroductionScreen> createState() => _IntroductionScreenState();
}

class _IntroductionScreenState extends State<IntroductionScreen> {
  // Аналог sessionStorage-ключа kmg_intro_popup_shown на сайте.
  static bool _popupShownThisSession = false;

  List<OnboardingTask> _tasks = [];
  LoginPopup? _loginPopup;
  bool _isLoading = true;
  bool _isSimulatingLogin = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    try {
      await _simulatePortalLogin(forcePopup: !_popupShownThisSession);
    } catch (e) {
      if (mounted) {
        setState(() => _error = 'Не удалось загрузить данные: $e\n'
            'API: ${AppConfig.apiBaseUrl}');
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _loadTasks() async {
    final tasks = await onboardingApi.getDayOneTasks(_employeeId);
    if (mounted) {
      setState(() => _tasks = tasks);
    }
  }

  Future<void> _simulatePortalLogin({
    bool forcePopup = false,
    bool resetDemo = false,
  }) async {
    setState(() => _isSimulatingLogin = true);

    try {
      if (resetDemo) {
        await onboardingApi.resetDayOneDemo(_employeeId);
        _popupShownThisSession = false;
      }

      final popup = await onboardingApi.triggerUserLogin(_employeeId);
      if (mounted) {
        setState(() => _loginPopup = popup);
      }
      await _loadTasks();

      if ((forcePopup || resetDemo) && mounted) {
        _popupShownThisSession = true;
        _showWelcomePopup();
      }
    } finally {
      if (mounted) {
        setState(() => _isSimulatingLogin = false);
      }
    }
  }

  OnboardingTask? get _videoTask {
    for (final task in _tasks) {
      if ((task.externalLink ?? '').isNotEmpty) {
        return task;
      }
    }
    return _tasks.isNotEmpty ? _tasks.first : null;
  }

  String get _videoUrl =>
      _loginPopup?.videoUrl.isNotEmpty == true
          ? _loginPopup!.videoUrl
          : _videoTask?.externalLink ??
              'https://team.kmg.kz/onboarding/welcome-video';

  int get _completedCount => _tasks.where((t) => t.isCompleted).length;

  void _showWelcomePopup() {
    final completed = _loginPopup?.completedTasks ?? _completedCount;
    final total = _loginPopup?.totalTasks ?? _tasks.length;

    showWelcomePopup(
      context,
      employeeName: _loginPopup?.employeeName ?? 'Азамат',
      adaptationDay: 1,
      completedTasks: completed,
      totalTasks: total,
      nextTaskTitle: _loginPopup?.nextTask?.title ??
          _tasks
              .where((t) => !t.isCompleted)
              .map((t) => t.title)
              .firstOrNull,
      onWatchVideo: _watchVideo,
      onAskQuestion: () => showBuddyChat(context),
    );
  }

  void _watchVideo() {
    launchUrl(Uri.parse(_videoUrl), mode: LaunchMode.externalApplication);
  }

  Future<void> _completeTask(int taskId) async {
    await onboardingApi.completeTask(taskId);
    await _loadTasks();
  }

  @override
  Widget build(BuildContext context) {
    return KmgScaffold(
      appBar: AppBar(
        title: const Text('Этап 2 · Знакомство'),
        actions: [
          IconButton(
            tooltip: 'Симулировать вход',
            icon: _isSimulatingLogin
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                        strokeWidth: 2, color: KmgColors.white),
                  )
                : const Icon(Icons.restart_alt),
            onPressed: _isSimulatingLogin
                ? null
                : () => _simulatePortalLogin(forcePopup: true, resetDemo: true),
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
              : RefreshIndicator(
                  onRefresh: _loadTasks,
                  child: ListView(
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
                    children: [
                      const Text(
                        'День 1: приветствие, обязательные инструктажи, видео '
                        'и первый контакт с Digital Buddy.',
                        style: TextStyle(
                            color: KmgColors.gray600, height: 1.45),
                      ),
                      const SizedBox(height: 16),
                      ProgressCard(
                        completed: _completedCount,
                        total: _tasks.length,
                        label: 'Задачи Дня 1',
                      ),
                      const SizedBox(height: 16),
                      _buildVideoCard(),
                      const SizedBox(height: 20),
                      const Text(
                        'Обязательные задачи',
                        style: TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.w700,
                          color: KmgColors.navy800,
                        ),
                      ),
                      const SizedBox(height: 12),
                      for (final task in _tasks) ...[
                        TaskCard(task: task, onComplete: _completeTask),
                        const SizedBox(height: 10),
                      ],
                      const SizedBox(height: 10),
                      OutlinedButton.icon(
                        onPressed: _showWelcomePopup,
                        icon: const Icon(Icons.smart_toy_outlined, size: 18),
                        label:
                            const Text('Открыть приветствие Digital Buddy'),
                      ),
                      const SizedBox(height: 16),
                      if (_tasks.isNotEmpty &&
                          _completedCount == _tasks.length)
                        const InfoCard(
                          success: true,
                          title: 'День 1 завершён',
                          text:
                              'Все обязательные инструктажи выполнены. Завтра '
                              'начнётся этап «Вовлечение» с Culture Fit Nudges.',
                        )
                      else
                        const InfoCard(
                          title: 'Что важно сегодня?',
                          text:
                              'Завершите все обязательные инструктажи до конца '
                              'рабочего дня. Если задача не будет выполнена '
                              'вовремя, HR получит уведомление за 2 часа до '
                              'конца дня.',
                        ),
                      const SizedBox(height: 12),
                      const InfoCard(
                        title: 'Digital Buddy 24/7',
                        text:
                            'Нажмите кнопку Buddy внизу экрана — ассистент '
                            'доступен на всех экранах и ответит по ВНД.',
                      ),
                    ],
                  ),
                ),
    );
  }

  Widget _buildVideoCard() {
    final videoCompleted = _videoTask?.isCompleted ?? false;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [KmgColors.navy800, KmgColors.green800],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                videoCompleted
                    ? Icons.check_circle
                    : Icons.play_circle_outline,
                color: KmgColors.green300,
                size: 36,
              ),
              const SizedBox(width: 10),
              const Expanded(
                child: Text(
                  'Видеообращение Председателя Правления КМГ',
                  style: TextStyle(
                    color: KmgColors.white,
                    fontWeight: FontWeight.w700,
                    fontSize: 15,
                    height: 1.3,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            videoCompleted
                ? 'Просмотр подтверждён'
                : 'Требуется просмотр и подтверждение',
            style: const TextStyle(color: KmgColors.green300, fontSize: 12.5),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              FilledButton.icon(
                onPressed: _watchVideo,
                icon: const Icon(Icons.play_arrow, size: 18),
                label: const Text('Смотреть видео'),
              ),
              if (_videoTask != null && !videoCompleted)
                OutlinedButton(
                  style: OutlinedButton.styleFrom(
                    foregroundColor: KmgColors.white,
                    side: const BorderSide(color: KmgColors.green300),
                  ),
                  onPressed: () => _completeTask(_videoTask!.id),
                  child: const Text('Подтвердить просмотр'),
                ),
            ],
          ),
        ],
      ),
    );
  }
}
