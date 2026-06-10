import '../core/network/api_client.dart';
import '../models/adaptation.dart';

/// GET-методы из src/api/adaptationApi.ts (для сотрудника — только чтение).
class AdaptationApi {
  const AdaptationApi();

  Future<List<OneToOneMeeting>> getMeetings(int employeeId) async {
    final response =
        await apiClient.get('/adaptation/employees/$employeeId/meetings');
    return (response.data as List)
        .map((e) => OneToOneMeeting.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<SmartGoal>> getGoals(int employeeId) async {
    final response =
        await apiClient.get('/adaptation/employees/$employeeId/goals');
    return (response.data as List)
        .map((e) => SmartGoal.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<List<LearningModule>> getLearningModules(int employeeId) async {
    final response = await apiClient
        .get('/adaptation/employees/$employeeId/learning-modules');
    return (response.data as List)
        .map((e) => LearningModule.fromJson(e as Map<String, dynamic>))
        .toList();
  }
}

const adaptationApi = AdaptationApi();
