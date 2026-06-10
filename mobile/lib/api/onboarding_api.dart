import '../core/network/api_client.dart';
import '../models/login_popup.dart';
import '../models/nudge.dart';
import '../models/onboarding_task.dart';

/// Порт src/api/onboardingApi.ts.
class OnboardingApi {
  const OnboardingApi();

  Future<List<OnboardingTask>> getDayOneTasks(int employeeId) async {
    final response = await apiClient.get('/onboarding/day-one/tasks/$employeeId');
    return (response.data as List)
        .map((e) => OnboardingTask.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<OnboardingTask>> getEngagementTasks(int employeeId) async {
    final response =
        await apiClient.get('/onboarding/engagement/tasks/$employeeId');
    return (response.data as List)
        .map((e) => OnboardingTask.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<OnboardingTask> completeTask(int taskId) async {
    final response = await apiClient.post('/onboarding/tasks/$taskId/complete');
    return OnboardingTask.fromJson(response.data as Map<String, dynamic>);
  }

  Future<List<Nudge>> getCultureFitNudges() async {
    final response = await apiClient.get('/onboarding/nudges');
    return (response.data as List)
        .map((e) => Nudge.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<CurrentNudgeResponse> getCurrentNudge(int employeeId) async {
    final response =
        await apiClient.get('/onboarding/nudges/current/$employeeId');
    return CurrentNudgeResponse.fromJson(
        response.data as Map<String, dynamic>);
  }

  Future<void> sendNudgeToChat(int employeeId) async {
    await apiClient.post('/onboarding/nudges/$employeeId/send');
  }

  Future<void> resetTodayNudgeDelivery(int employeeId) async {
    await apiClient.delete('/onboarding/nudges/demo-reset/$employeeId');
  }

  Future<LoginPopup> triggerUserLogin(int employeeId) async {
    final response =
        await apiClient.post('/webhooks/on-user-login/$employeeId');
    final data = response.data as Map<String, dynamic>;
    return LoginPopup.fromJson(data['popup'] as Map<String, dynamic>);
  }

  Future<void> resetDayOneDemo(int employeeId) async {
    await apiClient.post('/onboarding/day-one/demo-reset/$employeeId');
  }

  Future<ShiftAdaptationDayResponse> setupEngagementDemo(int employeeId) async {
    final response =
        await apiClient.post('/onboarding/engagement/demo-setup/$employeeId');
    return ShiftAdaptationDayResponse.fromJson(
        response.data as Map<String, dynamic>);
  }

  Future<ShiftAdaptationDayResponse> shiftAdaptationDay(
    int employeeId, {
    int? delta,
    int? targetDay,
  }) async {
    final response = await apiClient.post(
      '/onboarding/nudges/demo-shift-day/$employeeId',
      data: {
        'delta': ?delta,
        'target_day': ?targetDay,
      },
    );
    return ShiftAdaptationDayResponse.fromJson(
        response.data as Map<String, dynamic>);
  }
}

const onboardingApi = OnboardingApi();
